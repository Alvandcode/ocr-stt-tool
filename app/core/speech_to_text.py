"""Convert speech in an audio file to text via Google Web Speech API.

Privacy note: this sends audio to Google's servers and requires internet.
Do not use with sensitive recordings without consent. For offline use,
consider Vosk / faster-whisper (see requirements-optional.txt).
"""

from __future__ import annotations

import os

try:
    import speech_recognition as sr
    _SR_IMPORT_ERROR: Exception | None = None
except Exception as exc:  # noqa: BLE001 - intentional: SR breaks many ways (py3.15 aifc etc.)
    sr = None  # type: ignore[assignment]
    _SR_IMPORT_ERROR = exc

MAX_AUDIO_BYTES = 100 * 1024 * 1024
# AudioFile supports WAV/AIFF/FLAC natively. Anything else needs ffmpeg/pydub.
NATIVE_EXTENSIONS = {".wav", ".aiff", ".aif", ".flac"}


def audio_to_text(audio_path: str, lang: str = "fa-IR") -> str:
    """Transcribe an audio file with Google Web Speech API.

    Args:
        audio_path: Path to a ``.wav`` / ``.aiff`` / ``.flac`` file.
            MP3/OGG/M4A need ``pydub`` + ``ffmpeg`` -- convert first.
        lang: BCP-47 code, e.g. ``"fa-IR"``, ``"en-US"``.

    Returns:
        Recognized text (stripped).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: For empty/oversized/unsupported files, or when speech
            is unintelligible (wraps ``UnknownValueError``).
        ConnectionError: When the Google API is unreachable (wraps
            ``RequestError`` -- no internet, quota, firewall).
        RuntimeError: For undecodable/corrupt audio.
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

    if sr is None:
        raise RuntimeError(
            "SpeechRecognition library could not be imported "
            f"({_SR_IMPORT_ERROR}). On Python 3.15+ the stdlib 'aifc' module "
            "was removed and SpeechRecognition<4 breaks. Use Python 3.10-3.13, "
            "or switch to an offline backend (Vosk / faster-whisper, see "
            "requirements-optional.txt)."
        )

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

    return (text or "").strip()
