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
        "Examples: fa-IR, en-US. Mapped to a whisper tag for --engine whisper.",
    )
    parser.add_argument(
        "--ocr-lang",
        default="fas+eng",
        help="Tesseract language(s) for image OCR and PDF OCR fallback "
        "(default: fas+eng). Requires matching traineddata, e.g. "
        "tesseract-ocr-fas for Persian.",
    )
    parser.add_argument(
        "--engine",
        choices=["google", "whisper"],
        default="google",
        help="Audio only: 'google' (online, default) or 'whisper' "
        "(offline via faster-whisper).",
    )
    parser.add_argument(
        "--whisper-model",
        default="small",
        help="Whisper engine only: tiny, base, small (default), medium, large-v3.",
    )
    parser.add_argument(
        "--format",
        choices=["txt", "json", "srt"],
        default="txt",
        help="Output format (default: txt). 'srt' is audio-only.",
    )
    parser.add_argument(
        "--normalize-fa",
        action="store_true",
        help="Normalize Persian characters (Arabic Yeh/Kaf fixes, uses hazm "
        "if installed, stdlib fallback otherwise).",
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
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_app_version()}",
        help="Show version and exit.",
    )
    return parser


def _app_version() -> str:
    """Installed distribution version, falling back to the repo release."""
    try:
        from importlib.metadata import version

        return version("ocr-stt-tool")
    except Exception:  # noqa: BLE001 - not installed (running from source)
        return "1.2.2"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.format == "srt" and args.mode != "audio":
        parser.error("--format srt is only supported for audio mode.")
    if args.mode != "audio" and (
        args.engine != "google" or args.whisper_model != "small"
    ):
        parser.error("--engine/--whisper-model are only supported for audio mode.")
    if args.mode != "pdf" and (args.max_pages is not None or args.ocr_fallback):
        parser.error("--max-pages/--ocr-fallback are only supported for pdf mode.")

    if not os.path.isfile(args.source):
        print(f"Error: file not found: {args.source}", file=sys.stderr)
        return 2

    try:
        if args.mode == "image":
            from app.core.image_ocr import image_to_text

            result = image_to_text(args.source, lang=args.ocr_lang)
        elif args.mode == "pdf":
            from app.core.pdf_ocr import pdf_to_text

            result = pdf_to_text(
                args.source,
                max_pages=args.max_pages,
                ocr_fallback=args.ocr_fallback,
                ocr_lang=args.ocr_lang,
            )
        else:
            from app.core.speech_to_text import audio_to_text

            result = audio_to_text(
                args.source, lang=args.lang,
                engine=args.engine, model=args.whisper_model,
            )

        if args.normalize_fa:
            from app.core.fa_normalize import normalize_persian

            result.text = normalize_persian(result.text)
            for seg in result.segments or []:
                seg.text = normalize_persian(seg.text)
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

    for warning in result.warnings:
        print(f"Warning: {warning}", file=sys.stderr)

    if args.format == "json":
        payload = result.to_json() + "\n"
    elif args.format == "srt":
        try:
            payload = result.to_srt()
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
    else:
        payload = result.text + "\n" if result.text else "(no text found)\n"

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(payload)
        except OSError as exc:
            print(f"Error: cannot write to '{args.output}': {exc}", file=sys.stderr)
            return 1
    else:
        print(payload, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
