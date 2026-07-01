import argparse
from app.core import image_to_text, pdf_to_text, audio_to_text


def main():
    parser = argparse.ArgumentParser(
        description="OCR + PDF + Speech-to-Text tool (cross-platform)"
    )
    parser.add_argument("mode", choices=["image", "pdf", "audio"],
                        help="Processing mode")
    parser.add_argument("source", help="Path to file")
    parser.add_argument("--lang", default="fa-IR",
                        help="Language code for speech-to-text (default: fa-IR)")

    args = parser.parse_args()

    if args.mode == "image":
        text = image_to_text(args.source)
    elif args.mode == "pdf":
        text = pdf_to_text(args.source)
    else:
        text = audio_to_text(args.source, lang=args.lang)

    print(text)


if __name__ == "__main__":
    main()
