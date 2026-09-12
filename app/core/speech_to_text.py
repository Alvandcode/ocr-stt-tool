"""Convert speech in an audio file to text via Google Web Speech API.

Privacy note: this sends audio to Google's servers and requires internet.
Do not use with sensitive recordings without consent. For offline use,
consider the ``whisper`` engine (see requirements-optional.txt).
"""

from __future__ import annotations

import os
import time

try:
    import speech_recognition as sr
    _SR_IMPORT_ERROR: Exception | None = None
except Exception as exc:  # noqa: BLE001 - intentional: SR breaks many ways (py3.15 aifc etc.)
    sr = None  # type: ignore[assignment]
    _SR_IMPORT_ERROR = exc

from .models import ExtractResult, Segment

MAX_AUDIO_BYTES = 100 * 1024 * 1024
# AudioFile supports WAV/AIFF/FLAC natively. Anything else needs ffmpeg/pydub.
NATIVE_EXTENSIONS = {".wav", ".aiff", ".aif", ".flac"}


def audio_duration_sec(audio_path: str) -> float | None:
    """Best-effort audio duration in seconds (WAV only), else None."""
    try:
        import wave

        with wave.open(audio_path, "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate() or 1
            return frames / float(rate)
    except Exception:  # noqa: BLE001 - duration is best-effort only
        return None


def audio_to_text(
    audio_path: str,
    lang: str = "fa-IR",
    engine: str = "google",
) -> ExtractResult:
    """Transcribe an audio file.

    Args:
        audio_path: Path to a ``.wav`` / ``.aiff`` / ``.flac`` file.
            MP3/OGG/M4A need ``pydub`` + ``ffmpeg`` -- convert first.
        lang: BCP-47 code, e.g. ``"fa-IR"``, ``"en-US"`` (google engine)
            or whisper language tag (whisper engine).
        engine: ``"google"`` (online, default) or ``"whisper"``
            (offline via faster-whisper).

    Returns:
        :class:`ExtractResult` with a single timestamped segment
        (google) or per-chunk segments (whisper).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: For empty/oversized/unsupported files, unknown engine,
            or when speech is unintelligible (wraps ``UnknownValueError``).
        ConnectionError: When the Google API is unreachable (wraps
            ``RequestError`` -- no internet, quota, firewall).
        RuntimeError: For undecodable/corrupt audio or missing backends.
    """
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    size = os.path.getsize(audio_path)
    if size == 0:
        raise ValueError(f"Audio file is empty: {audio_path}")
    if size > MAX_AUDIO_BYTES:
        raise ValueError(
            f"Audio file too large (> {MAX_AUDIO_BYTES // (1024 * 1024)} MB): "
            f"{audio_path}. Split it first (whole file is loaded into RAM)."
        )

    ext = os.path.splitext(audio_path)[1].lower()
    if ext not in NATIVE_EXTENSIONS:
        raise ValueError(
            f"Unsupported audio extension '{ext or '(none)'}' for: {audio_path}. "
            f"Supported natively: {sorted(NATIVE_EXTENSIONS)}. "
            f"For MP3/OGG/M4A install 'pydub' + 'ffmpeg' and convert to WAV first."
        )

    if not lang or not isinstance(lang, str):
        raise ValueError(f"lang must be a non-empty string like 'fa-IR', got: {lang!r}")

    if engine not in ("google", "whisper"):
        raise ValueError(
            f"Unknown engine '{engine}'. Choose 'google' or 'whisper'."
        )

    if engine == "whisper":
        from .whisper_stt import whisper_to_result

        return whisper_to_result(audio_path, lang=lang)

    if sr is None:
        raise RuntimeError(
            "SpeechRecognition library could not be imported "
            f"({_SR_IMPORT_ERROR}). On Python 3.15+ the stdlib 'aifc' module "
            "was removed and SpeechRecognition breaks. Use Python 3.10-3.13, "
            "or switch to --engine whisper (offline, see "
            "requirements-optional.txt)."
        )

    started = time.perf_counter()
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
    except (FileNotFoundError, ValueError):
        raise
    except Exception as exc:
        raise RuntimeError(
            f"Could not decode audio '{audio_path}' (corrupt or unsupported "
            f"codec?). Original: {exc}"
        ) from exc

    try:
        text = recognizer.recognize_google(audio, language=lang)
    except sr.UnknownValueError as exc:
        raise ValueError(
            "Speech was unintelligible or silent (Google could not recognize "
            f"anything in '{audio_path}')."
        ) from exc
    except sr.RequestError as exc:
        raise ConnectionError(
            "Speech recognition service unreachable. Check internet connection, "
            f"firewall, or Google API quota. Original: {exc}"
        ) from exc

    text = (text or "").strip()
    duration = audio_duration_sec(audio_path)
    end = duration if duration else max(2.0, 0.08 * len(text))
    return ExtractResult(
        text=text,
        engine="google",
        source=audio_path,
        lang=lang,
        segments=[Segment(1, 0.0, end, text)] if text else [],
        elapsed_sec=time.perf_counter() - started,
    )
