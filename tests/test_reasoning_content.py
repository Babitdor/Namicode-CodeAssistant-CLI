"""Thinking models get their reasoning_content echoed back.

DeepSeek/GLM-style models return their chain of thought in `reasoning_content`
and then require it sent back with that assistant message on the next turn:

    400 invalid_request_error — "The `reasoning_content` in the thinking mode
    must be passed back to the API."

langchain_openai's _convert_message_to_dict emits only role/content/tool_calls,
so the field is parsed in and silently dropped on the way out — which breaks the
second request of every conversation, and for an agent a tool call IS a second
request.

The safety property is the other half: the field must only ever be re-attached
when the model actually produced it, so strict endpoints that have never heard
of it see exactly the payload they see today.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from novacode_cli.utils.backend_patches import apply_openai_reasoning_content_patch


def _convert(message):
    """Serialize through the (patched) OpenAI message converter."""
    apply_openai_reasoning_content_patch()
    from langchain_openai.chat_models.base import _convert_message_to_dict

    return _convert_message_to_dict(message)


def test_reasoning_content_survives_serialization():
    """Without this the next request 400s on every thinking model."""
    out = _convert(
        AIMessage(content="4", additional_kwargs={"reasoning_content": "2+2 is 4"})
    )
    assert out["reasoning_content"] == "2+2 is 4"
    assert out["content"] == "4"


def test_it_survives_alongside_tool_calls():
    """The agent path: a tool call is the second turn, so this is the common case."""
    out = _convert(
        AIMessage(
            content="",
            additional_kwargs={"reasoning_content": "I should check the weather"},
            tool_calls=[
                {"name": "get_weather", "args": {}, "id": "call_1", "type": "tool_call"}
            ],
        )
    )
    assert out["reasoning_content"] == "I should check the weather"
    assert out["tool_calls"], "tool calls must still be serialized"


def test_a_reasoning_field_is_also_carried():
    """Some gateways name it `reasoning` rather than `reasoning_content`."""
    out = _convert(AIMessage(content="hi", additional_kwargs={"reasoning": "because"}))
    assert out["reasoning"] == "because"


# ── The safety half: never invent the field ─────────────────────────────────


def test_a_normal_message_is_untouched():
    """OpenAI has never heard of reasoning_content; it must not be sent one."""
    out = _convert(AIMessage(content="hello", additional_kwargs={"refusal": None}))
    assert "reasoning_content" not in out
    assert "reasoning" not in out
    assert sorted(out) == ["content", "role"]


def test_empty_reasoning_is_not_sent():
    """'' means the model returned no thought — not the same as sending one."""
    for empty in ("", None):
        out = _convert(
            AIMessage(content="hi", additional_kwargs={"reasoning_content": empty})
        )
        assert "reasoning_content" not in out


def test_human_and_tool_messages_are_unaffected():
    assert sorted(_convert(HumanMessage("yo"))) == ["content", "role"]
    tool = _convert(ToolMessage(content="42", tool_call_id="call_1"))
    assert "reasoning_content" not in tool


def test_the_patch_is_idempotent():
    """Applied on every model build; must not stack wrappers."""
    for _ in range(5):
        apply_openai_reasoning_content_patch()
    out = _convert(
        AIMessage(content="x", additional_kwargs={"reasoning_content": "once"})
    )
    assert out["reasoning_content"] == "once"


def test_building_an_openai_compatible_model_applies_the_patch(monkeypatch):
    """It has to be live before the first request, not on some later path."""
    import novacode_cli.utils.backend_patches as bp

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setattr(bp, "_reasoning_content_patched", False)
    called: list[bool] = []
    real = bp.apply_openai_reasoning_content_patch
    monkeypatch.setattr(
        bp,
        "apply_openai_reasoning_content_patch",
        lambda: (called.append(True), real())[1],
    )

    from novacode_cli.config.model_create import build_chat_model

    build_chat_model("openai", "gpt-4o")
    assert called, "model built without the reasoning_content patch applied"
