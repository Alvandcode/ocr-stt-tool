# Examples

- `sample.png`: minimal valid PNG (white 400x120). Good for CLI smoke test
  (`python -m app.cli image examples/sample.png --ocr-lang eng` needs
  Tesseract installed; without it you get a clear install hint, not a crash).
- `sample.pdf`: one-page PDF with extractable text `Hello OCR-STT`.
  Test: `python -m app.cli pdf examples/sample.pdf`
- `sample.wav`: 1s silent WAV (valid container, no speech).
  Test: `python -m app.cli audio examples/sample.wav --lang en-US`
  correctly reports "unintelligible or silent" instead of crashing.

Replace these with real scans/recordings for accuracy tests.
