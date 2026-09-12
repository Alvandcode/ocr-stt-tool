# Changelog

## [1.2.2] - 2026-09-12

### Fixed
- `pip install` on Python 3.13+: Pillow is now ranged (`>=10.4.0`) so newer
  wheels are used instead of a failing from-source build. Full features
  (Google STT, whisper) still require Python 3.10-3.12 — documented in
  README, tutorial and install errors.

## [1.2.1] - 2026-09-12

### Fixed
- SRT timestamps at hour boundaries (`00:60:00,000` → `01:00:00,000`).
- Tutorial Termux steps: Persian traineddata is downloaded manually
  (no `tesseract-data-fas` package on Termux).
- README optional-install command now uses `pip install ".[offline,fa]"`.
- Mode-specific flags are validated (`--engine` audio-only,
  `--max-pages`/`--ocr-fallback` pdf-only) instead of silently ignored.
- `--normalize-fa` now normalizes subtitle segments too (json/srt consistent).
- `audio_to_text(..., model=...)` passes the model to the whisper backend.
- GUI imports backends lazily, drops nested ScrollView, shows all warnings,
  adds Save button and more STT languages.
- Dockerfile runs as non-root and runs the test suite during build.
- `faster-whisper` bumped to 1.2.1.

### Added
- `--version` flag.

## [Unreleased]

### Added
- Interactive Persian tutorial page `docs/tutorial.html` (mobile + desktop,
  responsive, offline single-file) linked from README via a tutorial button.

## [1.2.0] - 2026-09-12

### Added
- Structured `ExtractResult` (engine, lang, pages, warnings, elapsed time,
  timestamped segments) returned by all three backends (`app/core/models.py`).
- Output formats: `--format txt|json|srt` (`srt` is audio-only).
- Offline STT: `--engine whisper` via faster-whisper with `--whisper-model`
  (`tiny/base/small/medium/large-v3`), including per-chunk segments for SRT.
- Persian normalization: `--normalize-fa` (hazm if installed, stdlib fallback).
- `Dockerfile` (CLI-first, tesseract-fas + poppler + ffmpeg) + `.dockerignore`.
- Golden/format tests: `tests/test_golden.py` (16 tests, heavy deps mocked).
- GUI: engine selector, Persian-normalization checkbox, engine/timing in status.

### Changed
- **Breaking:** `image_to_text` / `pdf_to_text` / `audio_to_text` now return
  `ExtractResult` instead of `str` (`str(result)` still gives the text).
- Core split: `requirements.txt` is CLI-only; Kivy moved to
  `requirements-gui.txt` (`gui`, `offline`, `fa` extras in `pyproject.toml`).
- Mobile is documented as experimental; desktop/server is the primary target.

## [1.1.0] - 2026-09-11

### Added
- Input validation + clear errors (no raw tracebacks) across OCR/PDF/STT/CLI.
- Persian Tesseract support (`--ocr-lang fas+eng`), scanned-PDF `--ocr-fallback`,
  `--output`, `--max-pages`.
- Kivy GUI: background threads, scrollable output, language selectors.
- `examples/sample.{png,pdf,wav}`, smoke tests, CI (3 OS x 3 Python + ruff),
  `pyproject.toml`, `buildozer.spec`, issue template, code of conduct.
- Lazy `app.core` imports (one broken backend no longer kills every mode);
  clear error for SpeechRecognition on Python 3.15 (`aifc` removal).
