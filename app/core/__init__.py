"""Core OCR / PDF / STT functions (lazy imports).

Lazy loading matters: importing `image_to_text` must not require
`SpeechRecognition` (and vice versa). Otherwise one broken/optional
dependency -- e.g. SpeechRecognition on Python 3.15 where stdlib `aifc`
was removed -- would break every mode including unrelated ones.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # for type checkers only, no runtime cost
    from .image_ocr import image_to_text as image_to_text
    from .pdf_ocr import pdf_to_text as pdf_to_text
    from .speech_to_text import audio_to_text as audio_to_text

__all__ = ["audio_to_text", "image_to_text", "pdf_to_text"]


def __getattr__(name: str):
    if name == "image_to_text":
        from .image_ocr import image_to_text

        return image_to_text
    if name == "pdf_to_text":
        from .pdf_ocr import pdf_to_text

        return pdf_to_text
    if name == "audio_to_text":
        from .speech_to_text import audio_to_text

        return audio_to_text
    raise AttributeError(f"module 'app.core' has no attribute {name!r}")
