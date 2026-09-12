"""Smoke tests that do NOT need tesseract / internet / audio hardware."""

from __future__ import annotations

import pytest

from app.cli import build_parser, main
from app.core.image_ocr import image_to_text
from app.core.pdf_ocr import pdf_to_text
from app.core.speech_to_text import audio_to_text


def test_missing_files_raise_filenotfound(tmp_path):
    with pytest.raises(FileNotFoundError):
        image_to_text(str(tmp_path / "nope.png"))
    with pytest.raises(FileNotFoundError):
        pdf_to_text(str(tmp_path / "nope.pdf"))
    with pytest.raises(FileNotFoundError):
        audio_to_text(str(tmp_path / "nope.wav"))


def test_empty_files_rejected(tmp_path):
    p = tmp_path / "empty.png"
    p.write_bytes(b"")
    with pytest.raises((ValueError, FileNotFoundError)):
        image_to_text(str(p))

    q = tmp_path / "empty.pdf"
    q.write_bytes(b"")
    with pytest.raises((ValueError, FileNotFoundError)):
        pdf_to_text(str(q))


def test_wrong_extensions_rejected(tmp_path):
    f = tmp_path / "note.txt"
    f.write_text("hello")
    with pytest.raises(ValueError):
        image_to_text(str(f))
    with pytest.raises(ValueError):
        pdf_to_text(str(f))

    mp3 = tmp_path / "sound.mp3"
    mp3.write_bytes(b"ID3" + b"\x00" * 100)
    with pytest.raises(ValueError):
        audio_to_text(str(mp3))


def test_bad_max_pages_rejected(tmp_path):
    f = tmp_path / "d.pdf"
    f.write_bytes(b"%PDF-1.4 fake")
    with pytest.raises(ValueError):
        pdf_to_text(str(f), max_pages=0)


def test_cli_missing_file_returns_2(tmp_path, capsys):
    rc = main(["image", str(tmp_path / "missing.png")])
    assert rc == 2
    rc = main(["pdf", str(tmp_path / "missing.pdf")])
    assert rc == 2
    rc = main(["audio", str(tmp_path / "missing.wav")])
    assert rc == 2


def test_cli_parser_has_new_options():
    parser = build_parser()
    args = parser.parse_args(["pdf", "a.pdf", "--ocr-fallback", "--max-pages", "2"])
    assert args.ocr_fallback is True
    assert args.max_pages == 2
    args = parser.parse_args(["image", "a.png", "--ocr-lang", "fas"])
    assert args.ocr_lang == "fas"
    args = parser.parse_args(["audio", "a.wav", "-o", "out.txt"])
    assert args.output == "out.txt"
