"""Offline speech-to-text via faster-whisper (no internet, no Google API)."""

from __future__ import annotations

import time

from .models import ExtractResult, Segment

WHISPER_MODELS = ("tiny", "base", "small", "medium", "large-v3")


def whisper_lang_tag(lang: str) -> str:
    """Map BCP-47 (``fa-IR``) or bare tags to whisper language codes (``fa``)."""
    tag = (lang or "").strip().lower().replace("_", "-")
    if tag.startswith("fa"):
        return "fa"
    if tag.startswith("en"):
        return "en"
    # faster-whisper accepts e.g. "de", "fr", "ar"... take the primary subtag.
    return tag.split("-")[0] if tag else "fa"


def whisper_to_result(
    audio_path: str,
    lang: str = "fa-IR",
    model: str = "small",
) -> ExtractResult:
    """Transcribe *audio_path* offline with faster-whisper.

    Raises:
        RuntimeError: If ``faster-whisper`` is not installed.
        ValueError: For unknown model names or transcription failures
            caused by bad input.
    """
    if model not in WHISPER_MODELS:
        raise ValueError(
            f"Unknown whisper model '{model}'. Choose: {list(WHISPER_MODELS)}"
        )
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "faster-whisper is not installed. Install it with: "
            "'pip install faster-whisper' (see requirements-optional.txt). "
            f"Original: {exc}"
        ) from exc

    started = time.perf_counter()
    try:
        whisper_model = WhisperModel(model, device="auto", compute_type="auto")
        raw_segments, _info = whisper_model.transcribe(
            audio_path, language=whisper_lang_tag(lang)
        )
        segments = [
            Segment(i + 1, float(s.start), float(s.end), (s.text or "").strip())
            for i, s in enumerate(raw_segments)
            if (s.text or "").strip()
        ]
    except RuntimeError:
        raise
    except Exception as exc:
        raise ValueError(
            f"Whisper transcription failed for '{audio_path}': {exc}"
        ) from exc

    text = " ".join(s.text for s in segments).strip()
    return ExtractResult(
        text=text,
        engine=f"whisper:{model}",
        source=audio_path,
        lang=lang,
        segments=segments,
        elapsed_sec=time.perf_counter() - started,
    )
