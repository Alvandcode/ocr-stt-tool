"""Extract text from a PDF file (text layer, with optional OCR fallback)."""

from __future__ import annotations

import os
import time

import pdfplumber

from .models import ExtractResult

MAX_PDF_BYTES = 100 * 1024 * 1024
SCANNED_PDF_HINT = (
    "No text layer found. This looks like a scanned/image-only PDF. "
    "Re-run with --ocr-fallback (needs tesseract + poppler) "
    "or OCR the pages as images."
)


def _ocr_page_with_tesseract(page_image, lang: str) -> str:
    """OCR a pdfplumber page image. Imported lazily so pdf-only installs work."""
    import pytesseract  # local import: optional dependency path

    return pytesseract.image_to_string(page_image, lang=lang) or ""


def pdf_to_text(
    pdf_path: str,
    max_pages: int | None = None,
    ocr_fallback: bool = False,
    ocr_lang: str = "fas+eng",
) -> ExtractResult:
    """Extract text from all (or first N) pages of a PDF.

    This reads the embedded text layer via pdfplumber. Scanned/image-only
    PDFs have no text layer -- in that case an empty result with a warning
    is returned unless ``ocr_fallback=True`` (requires ``pdf2image`` +
    ``pytesseract`` + system ``tesseract`` and ``poppler``).

    Args:
        pdf_path: Path to a ``.pdf`` file.
        max_pages: Process at most this many pages (DoS guard). ``None`` = all.
        ocr_fallback: If True, OCR pages whose text layer is empty.
        ocr_lang: Tesseract langs for the fallback path.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: For empty/oversized/non-PDF files or bad ``max_pages``.
        RuntimeError: For encrypted/unreadable PDFs.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    size = os.path.getsize(pdf_path)
    if size == 0:
        raise ValueError(f"PDF file is empty: {pdf_path}")
    if size > MAX_PDF_BYTES:
        raise ValueError(
            f"PDF file too large (> {MAX_PDF_BYTES // (1024 * 1024)} MB): {pdf_path}"
        )

    if os.path.splitext(pdf_path)[1].lower() != ".pdf":
        raise ValueError(f"Not a .pdf file: {pdf_path}")

    if max_pages is not None and (not isinstance(max_pages, int) or max_pages < 1):
        raise ValueError(f"max_pages must be a positive int, got: {max_pages!r}")

    started = time.perf_counter()
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return ExtractResult(
                    text="",
                    engine="pdfplumber",
                    source=pdf_path,
                    lang="n/a",
                    pages=0,
                    elapsed_sec=time.perf_counter() - started,
                )
            pages = pdf.pages if max_pages is None else pdf.pages[:max_pages]
            chunks: list[str] = []
            warnings: list[str] = []
            empty_pages = 0
            fallback_used = False
            for i, page in enumerate(pages, start=1):
                try:
                    page_text = page.extract_text() or ""
                except Exception as exc:  # corrupt page content
                    raise RuntimeError(
                        f"Failed to extract text from page {i} of '{pdf_path}': {exc}"
                    ) from exc

                if not page_text.strip() and ocr_fallback:
                    try:
                        # 150 DPI is a good speed/accuracy trade-off for fallback.
                        page_image = page.to_image(resolution=150).original
                        page_text = _ocr_page_with_tesseract(page_image, ocr_lang)
                        fallback_used = True
                    except ImportError as exc:
                        raise RuntimeError(
                            "ocr_fallback=True needs 'pdf2image', 'pytesseract' "
                            "and system 'tesseract' + 'poppler'. "
                            f"Install them first. Original: {exc}"
                        ) from exc
                    except Exception as exc:
                        raise RuntimeError(
                            f"OCR fallback failed on page {i}: {exc}"
                        ) from exc

                if not page_text.strip():
                    empty_pages += 1
                # Keep per-page separation instead of blind concatenation.
                chunks.append(f"--- Page {i} ---\n{page_text.strip()}")
            engine = "pdfplumber+tesseract" if fallback_used else "pdfplumber"
            if empty_pages == len(pages):
                # All pages empty: almost certainly a scanned PDF without
                # a text layer. Return "" but flag it via warnings.
                warnings.append(SCANNED_PDF_HINT)
                return ExtractResult(
                    text="",
                    engine=engine,
                    source=pdf_path,
                    lang="n/a",
                    warnings=warnings,
                    pages=len(pages),
                    elapsed_sec=time.perf_counter() - started,
                )
            text = "\n\n".join(c for c in chunks if c).strip()
            return ExtractResult(
                text=text,
                engine=engine,
                source=pdf_path,
                lang="n/a",
                warnings=warnings,
                pages=len(pages),
                elapsed_sec=time.perf_counter() - started,
            )
    except (FileNotFoundError, ValueError, RuntimeError):
        raise
    except Exception as exc:
        msg = str(exc).lower()
        if "password" in msg or "encrypt" in msg:
            raise RuntimeError(
                f"PDF is encrypted or password-protected: {pdf_path}. "
                f"Decrypt it first (e.g. qpdf/pikepdf). Original: {exc}"
            ) from exc
        if "no such file" in msg:
            raise FileNotFoundError(f"PDF file not found: {pdf_path}") from exc
        raise RuntimeError(f"Could not read PDF '{pdf_path}': {exc}") from exc
