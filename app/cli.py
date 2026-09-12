"""Command-line interface: OCR image / PDF text / speech-to-text."""

from __future__ import annotations

import argparse
import os
import sys

# NOTE: core imports are lazy (inside main) so that e.g. `image` mode works
# even if SpeechRecognition is broken on this Python, and vice versa.


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="OCR + PDF + Speech-to-Text tool (cross-platform)"
    )
    parser.add_argument(
        "mode", choices=["image", "pdf", "audio"], help="Processing mode"
    )
    parser.add_argument("source", help="Path to input file")
    parser.add_argument(
        "--lang",
        default="fa-IR",
        help="BCP-47 code for speech-to-text (default: fa-IR). "
        "Examples: fa-IR, en-US.",
    )
    parser.add_argument(
        "--ocr-lang",
        default="fas+eng",
        help="Tesseract language(s) for image OCR and PDF OCR fallback "
        "(default: fas+eng). Requires matching traineddata, e.g. "
        "tesseract-ocr-fas for Persian.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write result to this file (UTF-8) instead of only stdout.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="PDF only: process at most N pages (default: all).",
    )
    parser.add_argument(
        "--ocr-fallback",
        action="store_true",
        help="PDF only: OCR pages with empty text layer (scanned PDFs). "
        "Needs pdf2image + poppler + tesseract.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not os.path.isfile(args.source):
        print(f"Error: file not found: {args.source}", file=sys.stderr)
        return 2

    try:
        if args.mode == "image":
            from app.core.image_ocr import image_to_text

            text = image_to_text(args.source, lang=args.ocr_lang)
        elif args.mode == "pdf":
            from app.core.pdf_ocr import pdf_to_text

            text = pdf_to_text(
                args.source,
                max_pages=args.max_pages,
                ocr_fallback=args.ocr_fallback,
                ocr_lang=args.ocr_lang,
            )
            if not text.strip():
                print(
                    "Warning: no text layer found. This looks like a scanned/image-only "
                    "PDF. Re-run with --ocr-fallback (needs tesseract + poppler) "
                    "or OCR the pages as images.",
                    file=sys.stderr,
                )
        else:
            from app.core.speech_to_text import audio_to_text

            text = audio_to_text(args.source, lang=args.lang)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ConnectionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(text + "\n")
        except OSError as exc:
            print(f"Error: cannot write to '{args.output}': {exc}", file=sys.stderr)
            return 1
    else:
        print(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
