"""Escape stops the turn.

Reported symptom: "pressing escape does not stop, sometimes". These drive the
real key through the real binding against a turn that is actually in flight,
across the states the key can be pressed in.
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

import pytest

try:
    import textual  # noqa: F401

    _HAS_TEXTUAL = True
except ImportError:  # pragma: no cover
    _HAS_TEXTUAL = False

pytestmark = pytest.mark.skipif(not _HAS_TEXTUAL, reason="textual not installed")

sys.path.insert(0, str(Path(__file__).parent))


class _HangingAgent:
    """Streams one chunk, then hangs at an await — cancellable in principle."""

    def __init__(self) -> None:
        self.started = asyncio.Event()
        self.cancelled = False
        self.finished = False

    async def aget_state(self, config):
        from test_tui_app import _StateVal

        return _StateVal([])

    async def astream(self, inp, **kw):
        from test_tui_app import _Chunk

        yield ((), "messages", (_Chunk("m1", [{"type": "text", "text": "working"}]), {}))
        self.started.set()
        try:
            await asyncio.sleep(30)  # the long model call
        except asyncio.CancelledError:
            self.cancelled = True
            raise
        self.finished = True

    async def aupdate_state(self, **kw):
        pass


class _BlockingAgent(_HangingAgent):
    """Blocks the event loop in sync code — cancellation cannot reach it.

    This is what a provider client doing synchronous HTTP on the loop looks
    like, and it is the one shape Escape genuinely cannot interrupt.
    """

    async def astream(self, inp, **kw):
        from test_tui_app import _Chunk

        yield ((), "messages", (_Chunk("m1", [{"type": "text", "text": "working"}]), {}))
        self.started.set()
        time.sleep(1.5)  # noqa: ASYNC251 — deliberately blocking, that is the test
        self.finished = True


def _app(agent):
    from test_tui_app import _SS
    from novacode_cli.tui.app import NovaApp
    from novacode_cli.ui.ui_elements import TokenTracker

    return NovaApp(
        agent=agent,
        assistant_id="nova-agent",
        session_state=_SS(),
        backend=None,
        token_tracker=TokenTracker(),
        image_tracker=None,
        model_name="m",
    )


async def _settle(pilot, times: int = 6):
    for _ in range(times):
        await pilot.pause()


async def _wait_turn_over(app, timeout: float = 5.0) -> bool:
    """True if the turn ended within *timeout*."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not app._turn_active:
            return True
        await asyncio.sleep(0.05)
    return False


# ── The reported behaviour ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_escape_stops_a_running_turn():
    """The headline case: a turn is streaming, escape ends it."""
    agent = _HangingAgent()
    app = _app(agent)
    async with app.run_test(size=(120, 40)) as pilot:
        await _settle(pilot)
        app._dispatch("hello")
        await asyncio.wait_for(agent.started.wait(), timeout=5)
        assert app._turn_active, "the turn never started"

        await pilot.press("escape")
        assert await _wait_turn_over(app), "escape did not stop the turn"
        assert agent.cancelled, "the agent stream was never cancelled"
        assert not agent.finished


@pytest.mark.asyncio
async def test_escape_works_with_focus_in_the_prompt_box():
    """Where the cursor actually is while a turn runs.

    PromptInput is a TextArea; if it consumed escape the app binding would
    never fire, and the key would appear dead exactly when it is needed.
    """
    agent = _HangingAgent()
    app = _app(agent)
    async with app.run_test(size=(120, 40)) as pilot:
        await _settle(pilot)
        prompt = app.query_one("#prompt")
        prompt.focus()
        await _settle(pilot, 2)
        app._dispatch("hello")
        await asyncio.wait_for(agent.started.wait(), timeout=5)

        await pilot.press("escape")
        assert await _wait_turn_over(app), "escape was swallowed by the input"


@pytest.mark.asyncio
async def test_the_turn_flag_is_cleared_so_the_next_prompt_is_accepted():
    """A stuck _turn_active would make Nova look wedged after a cancel."""
    agent = _HangingAgent()
    app = _app(agent)
    async with app.run_test(size=(120, 40)) as pilot:
        await _settle(pilot)
        app._dispatch("hello")
        await asyncio.wait_for(agent.started.wait(), timeout=5)
        await pilot.press("escape")
        assert await _wait_turn_over(app)
        assert app._turn_active is False


@pytest.mark.asyncio
async def test_escape_is_idempotent_when_nothing_is_running():
    """Users press it twice; the second must not raise."""
    app = _app(_HangingAgent())
    async with app.run_test(size=(120, 40)) as pilot:
        await _settle(pilot)
        await pilot.press("escape")
        await pilot.press("escape")
        await _settle(pilot)
        assert app.is_running


@pytest.mark.asyncio
async def test_a_second_escape_during_cancellation_does_not_break_it():
    agent = _HangingAgent()
    app = _app(agent)
    async with app.run_test(size=(120, 40)) as pilot:
        await _settle(pilot)
        app._dispatch("hello")
        await asyncio.wait_for(agent.started.wait(), timeout=5)
        await pilot.press("escape")
        await pilot.press("escape")
        assert await _wait_turn_over(app)


# ── The case Escape genuinely cannot win ────────────────────────────────────


@pytest.mark.asyncio
async def test_a_loop_blocking_turn_cannot_be_interrupted_but_recovers():
    """Documents the real limit rather than pretending it does not exist.

    While sync code holds the event loop, the keypress is not even delivered —
    so Escape cannot help until it returns. What must be true is that the turn
    then ends, rather than the cancel being lost.
    """
    agent = _BlockingAgent()
    app = _app(agent)
    async with app.run_test(size=(120, 40)) as pilot:
        await _settle(pilot)
        app._dispatch("hello")
        await asyncio.wait_for(agent.started.wait(), timeout=5)
        await pilot.press("escape")
        # It may finish the blocking section, but it must not stay active.
        assert await _wait_turn_over(app, timeout=8), (
            "the turn stayed active after a blocking section ended"
        )


# ── Remote-bridge turns ─────────────────────────────────────────────────────
#
# A turn started from Telegram/Discord runs inside the "remote" consumer
# worker, NOT the "turn" group, so the group cancel in action_cancel_turn never
# reached it and escape silently did nothing for it. That is the "sometimes":
# locally typed prompts stopped, remote-triggered ones did not.


@pytest.mark.asyncio
async def test_escape_cancels_a_turn_started_from_a_remote_bridge():
    app = _app(_HangingAgent())
    async with app.run_test(size=(120, 40)) as pilot:
        await _settle(pilot)
        running = asyncio.Event()

        async def _remote_turn():
            running.set()
            await asyncio.sleep(30)

        task = asyncio.create_task(_remote_turn())
        app._remote_turn_task = task
        await asyncio.wait_for(running.wait(), timeout=5)

        await pilot.press("escape")
        await asyncio.sleep(0.1)
        assert task.cancelled() or task.done(), "escape did not reach the remote turn"


@pytest.mark.asyncio
async def test_cancelling_does_not_tear_down_the_remote_consumer():
    """The reason this cancels a task and not the "remote" worker group.

    Killing the group would stop the loop that receives bridge messages, so the
    bridge would go silent — a much worse bug than the one being fixed.
    """
    app = _app(_HangingAgent())
    cancelled_groups: list[str] = []
    async with app.run_test(size=(120, 40)) as pilot:
        await _settle(pilot)
        real = app.workers.cancel_group

        def _spy(node, group):
            cancelled_groups.append(group)
            return real(node, group)

        app.workers.cancel_group = _spy
        await pilot.press("escape")
        await _settle(pilot, 2)

    assert "remote" not in cancelled_groups, (
        "cancelled the whole remote group — this detaches the bridge"
    )


@pytest.mark.asyncio
async def test_cancel_is_safe_when_no_remote_turn_is_running():
    app = _app(_HangingAgent())
    async with app.run_test(size=(120, 40)) as pilot:
        await _settle(pilot)
        assert app._remote_turn_task is None
        await pilot.press("escape")
        await _settle(pilot)
        assert app.is_running


@pytest.mark.asyncio
async def test_a_finished_remote_turn_is_not_re_cancelled():
    app = _app(_HangingAgent())
    async with app.run_test(size=(120, 40)) as pilot:
        await _settle(pilot)

        async def _done():
            return "ok"

        task = asyncio.create_task(_done())
        await task
        app._remote_turn_task = task
        await pilot.press("escape")   # must not raise on an already-done task
        await _settle(pilot)
        assert task.done() and not task.cancelled()


@pytest.mark.asyncio
async def test_the_bridge_still_answers_after_a_cancelled_remote_turn():
    """Cancelling one remote turn must not silence the bridge.

    The consumer catches the turn's CancelledError inside its own loop, so it
    goes on to the next message. If that ever changed, escape would fix one bug
    by introducing a worse one: a bridge that stops responding entirely.
    """
    from novacode_cli.remote.bridge import RemoteMessage, RemotePlatform

    agent = _HangingAgent()
    app = _app(agent)
    replies: list[str] = []
    handled = asyncio.Event()

    def _msg(text: str) -> RemoteMessage:
        async def reply_fn(t):
            replies.append(t)
            handled.set()

        return RemoteMessage(
            platform=RemotePlatform.TELEGRAM,
            chat_id=1,
            user_name="babit",
            text=text,
            reply_fn=reply_fn,
        )

    async with app.run_test(size=(120, 40)) as pilot:
        await _settle(pilot)
        queue: asyncio.Queue = asyncio.Queue()
        app.session_state._remote_message_queue = queue
        app.session_state._remote_message_lock = None

        # @work-decorated: calling it schedules a Worker, not a coroutine.
        consumer = app._remote_consumer()
        await queue.put(_msg("first"))

        # Wait for the first turn to be in flight, then stop it with escape.
        for _ in range(60):
            if app._remote_turn_task is not None:
                break
            await asyncio.sleep(0.05)
        assert app._remote_turn_task is not None, "the remote turn never started"
        await pilot.press("escape")
        await asyncio.sleep(0.3)

        # The consumer must still be alive and willing to take the next message.
        from textual.worker import WorkerState

        assert consumer.state is WorkerState.RUNNING, (
            f"the consumer died with the cancelled turn: {consumer.state}"
        )

        # And it really does take the next message.
        await queue.put(_msg("second"))
        await asyncio.wait_for(handled.wait(), timeout=10)
        assert replies, "the bridge never replied after a cancelled turn"
        consumer.cancel()
