"""Golden + format tests (no tesseract / internet needed; heavy deps mocked)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.cli import build_parser, main
from app.core.fa_normalize import normalize_persian
from app.core.models import ExtractResult, Segment, format_srt_timestamp
from app.core.pdf_ocr import pdf_to_text
from app.core.whisper_stt import whisper_lang_tag

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_PDF = str(ROOT / "examples" / "sample.pdf")
SAMPLE_PNG = str(ROOT / "examples" / "sample.png")
SAMPLE_WAV = str(ROOT / "examples" / "sample.wav")


def test_pdf_sample_golden():
    result = pdf_to_text(SAMPLE_PDF)
    assert isinstance(result, ExtractResult)
    assert "Hello OCR-STT" in result.text
    assert "--- Page 1 ---" in result.text
    assert result.pages == 1
    assert result.engine == "pdfplumber"
    assert result.warnings == []


def test_result_json_roundtrip():
    result = ExtractResult(
        text="سلام دنیا",
        engine="google",
        source="a.wav",
        lang="fa-IR",
        warnings=["w1"],
        segments=[Segment(1, 0.0, 1.5, "سلام دنیا")],
    )
    data = json.loads(result.to_json())
    assert data["text"] == "سلام دنیا"
    assert data["engine"] == "google"
    assert data["warnings"] == ["w1"]
    assert data["segments"][0]["end_sec"] == 1.5
    assert str(result) == "سلام دنیا"
    assert bool(result) is True
    assert bool(ExtractResult(text="  ", engine="x", source="s", lang="l")) is False


def test_srt_timestamp_format():
    assert format_srt_timestamp(0) == "00:00:00,000"
    assert format_srt_timestamp(61.5) == "00:01:01,500"
    assert format_srt_timestamp(3661.25) == "01:01:01,250"


def test_srt_export_segments():
    result = ExtractResult(
        text="hi you",
        engine="whisper:small",
        source="a.wav",
        lang="en-US",
        segments=[Segment(1, 0.0, 1.0, "hi"), Segment(2, 1.0, 2.5, "you")],
    )
    srt = result.to_srt()
    assert srt.startswith("1\n00:00:00,000 --> 00:00:01,000\nhi")
    assert "\n2\n00:00:01,000 --> 00:00:02,500\nyou" in srt


def test_srt_empty_raises():
    result = ExtractResult(text="  ", engine="x", source="s", lang="l")
    with pytest.raises(ValueError):
        result.to_srt()


def test_save_txt_json_srt(tmp_path):
    result = ExtractResult(
        text="hello",
        engine="google",
        source="a.wav",
        lang="en-US",
        segments=[Segment(1, 0.0, 2.0, "hello")],
    )
    p_txt = tmp_path / "o.txt"
    result.save(str(p_txt), "txt")
    assert p_txt.read_text(encoding="utf-8") == "hello\n"
    p_json = tmp_path / "o.json"
    result.save(str(p_json), "json")
    assert json.loads(p_json.read_text(encoding="utf-8"))["engine"] == "google"
    p_srt = tmp_path / "o.srt"
    result.save(str(p_srt), "srt")
    assert "-->" in p_srt.read_text(encoding="utf-8")
    with pytest.raises(ValueError):
        result.save(str(tmp_path / "o.xml"), "xml")


def test_image_mocked_ocr(monkeypatch):
    from app.core import image_ocr

    monkeypatch.setattr(
        image_ocr.pytesseract, "image_to_string", lambda img, lang=None: "  hello  "
    )
    result = image_ocr.image_to_text(SAMPLE_PNG, lang="eng")
    assert result.text == "hello"
    assert result.engine == "tesseract"
    assert result.lang == "eng"


def test_audio_google_mocked(monkeypatch):
    import app.core.speech_to_text as stt

    class _Audio:
        pass

    class _Source:
        pass

    class _Recognizer:
        def record(self, source):
            return _Audio()

        def recognize_google(self, audio, language=None):
            assert language == "fa-IR"
            return "سلام دنیا"

    class _AudioFile:
        def __init__(self, path):
            pass

        def __enter__(self):
            return _Source()

        def __exit__(self, *args):
            return False

    class _FakeSR:
        class UnknownValueError(Exception):
            pass

        class RequestError(Exception):
            pass

        Recognizer = _Recognizer
        AudioFile = _AudioFile

    monkeypatch.setattr(stt, "sr", _FakeSR)
    result = stt.audio_to_text(SAMPLE_WAV, lang="fa-IR")
    assert result.text == "سلام دنیا"
    assert result.engine == "google"
    assert len(result.segments or []) == 1
    assert result.segments[0].start_sec == 0.0
    # sample.wav is 1s of silence -> duration-based single cue
    assert result.segments[0].end_sec == pytest.approx(1.0, abs=0.05)


def test_audio_unknown_engine_rejected():
    from app.core.speech_to_text import audio_to_text

    with pytest.raises(ValueError):
        audio_to_text(SAMPLE_WAV, engine="nope")


def test_whisper_missing_backend_raises():
    try:
        import faster_whisper  # noqa: F401
    except ImportError:
        pass
    else:
        pytest.skip("faster-whisper installed; skipping missing-backend test")
    from app.core.whisper_stt import whisper_to_result

    with pytest.raises(RuntimeError, match="faster-whisper is not installed"):
        whisper_to_result(SAMPLE_WAV)


def test_whisper_mocked(monkeypatch):
    import sys
    import types

    from app.core import whisper_stt

    class _FakeSeg:
        def __init__(self, start, end, text):
            self.start = start
            self.end = end
            self.text = text

    class _FakeModel:
        def __init__(self, *args, **kwargs):
            pass

        def transcribe(self, path, language=None):
            assert language == "fa"
            return (
                [_FakeSeg(0.0, 1.2, "سلام"), _FakeSeg(1.2, 2.0, "دنیا")],
                {"language": "fa"},
            )

    fake_mod = types.ModuleType("faster_whisper")
    fake_mod.WhisperModel = _FakeModel
    monkeypatch.setitem(sys.modules, "faster_whisper", fake_mod)

    result = whisper_stt.whisper_to_result(SAMPLE_WAV, lang="fa-IR", model="tiny")
    assert result.engine == "whisper:tiny"
    assert result.text == "سلام دنیا"
    assert len(result.segments or []) == 2
    assert result.segments[1].end_sec == pytest.approx(2.0)

    with pytest.raises(ValueError):
        whisper_stt.whisper_to_result(SAMPLE_WAV, model="xxl")


def test_whisper_lang_tag_mapping():
    assert whisper_lang_tag("fa-IR") == "fa"
    assert whisper_lang_tag("en-US") == "en"
    assert whisper_lang_tag("de") == "de"


def test_normalize_fallback_arabic_chars():
    out = normalize_persian("علي كتاب", use_hazm=False)
    assert "علی" in out
    assert "کتاب" in out


def test_cli_format_json_pdf(tmp_path):
    out = tmp_path / "res.json"
    rc = main(["pdf", SAMPLE_PDF, "--format", "json", "-o", str(out)])
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "Hello OCR-STT" in data["text"]
    assert data["engine"] == "pdfplumber"


def test_cli_srt_rejected_for_non_audio():
    with pytest.raises(SystemExit):
        main(["image", SAMPLE_PNG, "--format", "srt"])


def test_cli_parser_new_options():
    args = build_parser().parse_args(
        ["audio", "a.wav", "--engine", "whisper", "--whisper-model", "base",
         "--format", "srt", "--normalize-fa"]
    )
    assert args.engine == "whisper"
    assert args.whisper_model == "base"
    assert args.format == "srt"
    assert args.normalize_fa is True
