"""Extract text from an image using Tesseract OCR."""

from __future__ import annotations

import os

import pytesseract
from PIL import Image, UnidentifiedImageError
from pytesseract import TesseractError, TesseractNotFoundError

# Refuse absurdly large images early (Pillow DecompressionBomb protection
# is still active, this is just a clearer error message).
MAX_IMAGE_BYTES = 30 * 1024 * 1024
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}


def image_to_text(image_path: str, lang: str = "fas+eng") -> str:
    """Extract text from an image file.

    Args:
        image_path: Path to an image file.
        lang: Tesseract language codes, e.g. ``"fas"``, ``"eng"``,
            ``"fas+eng"``. Persian requires the ``fas`` traineddata
            (``tesseract-ocr-fas`` on Linux).

    Returns:
        Extracted text, stripped of leading/trailing whitespace.

    Raises:
        FileNotFoundError: If the path does not exist or is not a file.
        ValueError: If the file is empty, has an unsupported extension,
            or no text could be decoded.
        RuntimeError: If the Tesseract binary is missing or fails.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    if os.path.getsize(image_path) == 0:
        raise ValueError(f"Image file is empty: {image_path}")

    if os.path.getsize(image_path) > MAX_IMAGE_BYTES:
        raise ValueError(
            f"Image file too large (> {MAX_IMAGE_BYTES // (1024 * 1024)} MB): "
            f"{image_path}. Refusing to process to avoid OOM."
        )

    ext = os.path.splitext(image_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported image extension '{ext or '(none)'}' for: {image_path}. "
            f"Supported: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    try:
        with Image.open(image_path) as img:
            img.load()  # force decoding while file handle is open
            try:
                text = pytesseract.image_to_string(img, lang=lang)
            except TesseractNotFoundError as exc:
                raise RuntimeError(
                    "Tesseract OCR binary not found. Install it first: "
                    "'sudo apt install tesseract-ocr tesseract-ocr-fas' "
                    "(Linux), 'brew install tesseract tesseract-lang' (macOS), "
                    "or UB-Mannheim build (Windows), then ensure it is on PATH."
                ) from exc
            except TesseractError as exc:
                raise RuntimeError(
                    f"Tesseract failed (maybe missing language data for "
                    f"lang='{lang}'). Install e.g. 'tesseract-ocr-fas'. "
                    f"Original error: {exc}"
                ) from exc
    except UnidentifiedImageError as exc:
        raise ValueError(
            f"File is not a readable image (corrupt or wrong format): {image_path}"
        ) from exc
    except (FileNotFoundError, ValueError, RuntimeError):
        raise
    except OSError as exc:
        raise ValueError(f"Could not read image '{image_path}': {exc}") from exc

    return (text or "").strip()
