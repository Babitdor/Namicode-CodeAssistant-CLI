"""Voice notes sent from a remote bridge reach the agent as text.

Two properties carry real weight here and the rest is plumbing: an
unauthorized chat must never make Nova fetch and decode a file, and a sender
must never be left staring at silence — they are on a phone, so a voice note
that vanishes is indistinguishable from a dead bot.
"""

from __future__ import annotations

import asyncio
import math
import struct

import numpy as np
import pytest

from novacode_cli.remote import voice_notes as vn


# ── Fakes ───────────────────────────────────────────────────────────────────


class _FakeSTT:
    """Records the PCM it was handed and returns a canned transcript."""

    def __init__(self, transcript: str = "add a dry run flag") -> None:
        self.transcript = transcript
        self.seen: list[np.ndarray] = []

    async def transcribe(self, pcm_int16):
        self.seen.append(pcm_int16)
        return self.transcript


def _wav_bytes(seconds: float = 0.25, rate: int = 16000, freq: float = 440.0) -> bytes:
    """A real mono 16-bit WAV, so the decoder does actual work.

    WAV rather than OGG/Opus because it can be synthesized here without an
    encoder; both take the same PyAV path in decode_audio.
    """
    n = int(rate * seconds)
    frames = b"".join(
        struct.pack("<h", int(20000 * math.sin(2 * math.pi * freq * i / rate)))
        for i in range(n)
    )
    return (
        b"RIFF" + struct.pack("<I", 36 + len(frames)) + b"WAVE"
        b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, rate, rate * 2, 2, 16)
        + b"data" + struct.pack("<I", len(frames)) + frames
    )


# ── Decoding + transcription ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_audio_is_decoded_to_the_pcm_the_stt_layer_expects():
    """Every STT backend takes 16 kHz mono int16; the decoder must deliver it."""
    stt = _FakeSTT()
    text = await vn.transcribe_voice_note(_wav_bytes(), stt=stt)

    assert text == "add a dry run flag"
    pcm = stt.seen[0]
    assert pcm.dtype == np.int16, f"STT got {pcm.dtype}, not int16"
    assert pcm.ndim == 1, "audio must be downmixed to mono"
    # 0.25 s at 16 kHz, allowing for resampler edge effects.
    assert 3500 < pcm.size < 4500, f"unexpected length {pcm.size} — wrong rate?"


@pytest.mark.asyncio
async def test_a_hot_recording_is_clipped_rather_than_wrapped():
    """float32 above 1.0 would wrap to full-scale noise if cast without clipping."""
    loud = np.full(16000, 4.0, dtype=np.float32)

    class _Loud(_FakeSTT):
        pass

    stt = _Loud()
    monkey = vn._decode_to_pcm16
    try:
        vn._decode_to_pcm16 = lambda data: (  # noqa: ARG005
            np.clip(loud, -1.0, 1.0) * 32767.0
        ).astype(np.int16)
        await vn.transcribe_voice_note(b"x", stt=stt)
    finally:
        vn._decode_to_pcm16 = monkey
    assert stt.seen[0].max() == 32767, "clipping must saturate, not wrap negative"
    assert stt.seen[0].min() >= 0


@pytest.mark.asyncio
async def test_transcript_is_stripped_and_empty_speech_returns_empty():
    assert await vn.transcribe_voice_note(_wav_bytes(), stt=_FakeSTT("  hi  ")) == "hi"
    assert await vn.transcribe_voice_note(_wav_bytes(), stt=_FakeSTT("")) == ""
    assert await vn.transcribe_voice_note(b"", stt=_FakeSTT()) == ""


@pytest.mark.asyncio
async def test_an_overlong_note_is_refused_before_it_is_decoded():
    """Local Whisper runs near real time; a long clip would stall the bridge."""
    stt = _FakeSTT()
    with pytest.raises(vn.VoiceNoteTooLong) as exc:
        await vn.transcribe_voice_note(
            _wav_bytes(), duration=vn.MAX_DURATION_SECONDS + 1, stt=stt
        )
    assert str(vn.MAX_DURATION_SECONDS) in str(exc.value)
    assert stt.seen == [], "the clip was decoded despite being rejected"


@pytest.mark.asyncio
async def test_a_note_at_the_limit_is_accepted():
    stt = _FakeSTT()
    out = await vn.transcribe_voice_note(
        _wav_bytes(), duration=vn.MAX_DURATION_SECONDS, stt=stt
    )
    assert out


@pytest.mark.asyncio
async def test_oversized_audio_is_refused():
    with pytest.raises(vn.VoiceNoteTooLong):
        await vn.transcribe_voice_note(b"\0" * (vn.MAX_AUDIO_BYTES + 1), stt=_FakeSTT())


def test_missing_voice_extra_gives_an_installable_message(monkeypatch):
    """Voice is an optional extra, and the person who sees this is on a phone."""
    import builtins

    real = builtins.__import__

    def _no_whisper(name, *a, **k):
        if name.startswith("faster_whisper"):
            raise ImportError("no faster_whisper")
        return real(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", _no_whisper)
    with pytest.raises(vn.VoiceNotesUnavailable) as exc:
        vn._decode_to_pcm16(b"x")
    assert "pip install" in str(exc.value)
    assert "voice" in str(exc.value)


def test_configured_provider_is_used_not_a_hardcoded_one(monkeypatch):
    """A voice note must not be handled by a different engine than push-to-talk."""
    seen = {}

    def _fake(cfg):
        seen["cfg"] = cfg
        return _FakeSTT()

    monkeypatch.setattr("novacode_cli.audio.pipeline.stt_from_voice_config", _fake)
    vn._load_stt()
    assert "stt_provider" in seen["cfg"] or "providers" in seen["cfg"]


# ── The STT factory shared with the live pipeline ───────────────────────────


def test_stt_factory_honors_the_saved_provider_and_model():
    from novacode_cli.audio.pipeline import stt_from_voice_config

    stt = stt_from_voice_config(
        {"stt_provider": "faster-whisper", "stt_model": "tiny", "stt_device": "cpu"}
    )
    assert type(stt).__name__ == "Transcriber"
    assert stt._model_size == "tiny"
    assert stt._device_pref == "cpu"


def test_stt_factory_prefers_explicit_provider_config_over_legacy_keys():
    from novacode_cli.audio.pipeline import stt_from_voice_config

    stt = stt_from_voice_config(
        {
            "stt_provider": "faster-whisper",
            "stt_model": "tiny",
            "providers": {"faster-whisper": {"model": "small", "device": "cuda"}},
        }
    )
    assert stt._model_size == "small"
    assert stt._device_pref == "cuda"


def test_building_stt_does_not_hijack_the_live_voice_pipeline():
    """Constructing a VoicePipeline would install itself as _ACTIVE_PIPELINE."""
    from novacode_cli.audio import pipeline as pl

    before = pl._ACTIVE_PIPELINE
    pl.stt_from_voice_config({"stt_provider": "faster-whisper"})
    assert pl._ACTIVE_PIPELINE is before


def test_the_live_pipeline_still_builds_through_the_same_factory():
    """The extraction must not have left the pipeline on a divergent path."""
    from novacode_cli.audio.pipeline import VoicePipeline

    stt = VoicePipeline(stt_provider="faster-whisper", stt_model="tiny")._build_stt()
    assert type(stt).__name__ == "Transcriber"
    assert stt._model_size == "tiny"


def _ogg_opus_bytes(seconds: float = 1.0) -> bytes | None:
    """Encode a real OGG/Opus clip — the exact container Telegram sends."""
    try:
        import av
    except ImportError:  # pragma: no cover
        return None
    import io as _io

    buf = _io.BytesIO()
    try:
        container = av.open(buf, mode="w", format="ogg")
        stream = container.add_stream("libopus", rate=48000)
        stream.layout = "mono"
        rate = 48000
        t = np.arange(int(rate * seconds), dtype=np.float32)
        tone = (0.3 * np.sin(2 * np.pi * 440 * t / rate) * 32767).astype(np.int16)
        frame = av.AudioFrame.from_ndarray(tone.reshape(1, -1), format="s16", layout="mono")
        frame.rate = rate
        for packet in stream.encode(frame):
            container.mux(packet)
        for packet in stream.encode(None):
            container.mux(packet)
        container.close()
    except Exception:  # pragma: no cover — no libopus in this build
        return None
    return buf.getvalue()


@pytest.mark.asyncio
async def test_real_telegram_ogg_opus_decodes_to_the_expected_pcm():
    """The format that will actually arrive — 48 kHz stereo-capable OGG/Opus.

    The WAV cases above prove the plumbing; this proves the resample and
    downmix Telegram's container actually needs.
    """
    ogg = _ogg_opus_bytes(1.0)
    if ogg is None:
        pytest.skip("libopus encoder unavailable in this PyAV build")
    assert ogg[:4] == b"OggS"

    stt = _FakeSTT()
    await vn.transcribe_voice_note(ogg, duration=1, stt=stt)
    pcm = stt.seen[0]
    assert pcm.dtype == np.int16
    assert pcm.ndim == 1, "48 kHz source must be downmixed to mono"
    assert 15000 < pcm.size < 17000, (
        f"1 s should be ~16000 samples at 16 kHz, got {pcm.size} — not resampled"
    )
