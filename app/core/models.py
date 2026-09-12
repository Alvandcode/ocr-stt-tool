"""Structured results shared by the OCR / PDF / STT backends.

Instead of returning bare strings, every backend returns an
:class:`ExtractResult` so callers also get the engine name, language,
per-page counts, warnings (e.g. "scanned PDF, no text layer") and --
for audio -- timestamped :class:`Segment` items for SRT export.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field


def format_srt_timestamp(seconds: float) -> str:
    """Format seconds as ``HH:MM:SS,mmm`` for SRT files."""
    seconds = max(0.0, float(seconds))
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = round((seconds - int(seconds)) * 1000)
    if millis == 1000:  # rounding carry
        secs += 1
        millis = 0
        if secs == 60:
            secs = 0
            minutes += 1
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


@dataclass
class Segment:
    """One timestamped chunk of transcribed speech."""

    index: int
    start_sec: float
    end_sec: float
    text: str

    def to_srt_block(self) -> str:
        return (
            f"{self.index}\n"
            f"{format_srt_timestamp(self.start_sec)} --> "
            f"{format_srt_timestamp(self.end_sec)}\n"
            f"{self.text.strip()}\n"
        )


@dataclass
class ExtractResult:
    """Uniform backend output."""

    text: str
    engine: str
    source: str
    lang: str
    warnings: list[str] = field(default_factory=list)
    pages: int | None = None
    elapsed_sec: float = 0.0
    segments: list[Segment] | None = None

    def __str__(self) -> str:
        return self.text

    def __bool__(self) -> bool:
        return bool(self.text.strip())

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "engine": self.engine,
            "source": self.source,
            "lang": self.lang,
            "warnings": list(self.warnings),
            "pages": self.pages,
            "elapsed_sec": round(self.elapsed_sec, 3),
            "segments": [
                {
                    "index": s.index,
                    "start_sec": round(s.start_sec, 3),
                    "end_sec": round(s.end_sec, 3),
                    "text": s.text,
                }
                for s in (self.segments or [])
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_srt(self, default_duration_sec: float | None = None) -> str:
        """Render segments as SRT.

        Raises:
            ValueError: If there are no segments and no text to wrap
                (e.g. image/PDF results -- SRT is an audio subtitle format).
        """
        segments = list(self.segments or [])
        if not segments:
            if not self.text.strip():
                raise ValueError("Nothing to export: result contains no text.")
            end = default_duration_sec
            if end is None:
                end = max(2.0, 0.08 * len(self.text))
            segments = [Segment(1, 0.0, end, self.text)]
        return "\n".join(s.to_srt_block() for s in segments).strip() + "\n"

    def save(self, path: str, fmt: str = "txt") -> None:
        """Write the result to *path* in ``txt`` / ``json`` / ``srt`` format."""
        fmt = fmt.lower()
        if fmt == "txt":
            payload = self.text + "\n"
        elif fmt == "json":
            payload = self.to_json() + "\n"
        elif fmt == "srt":
            payload = self.to_srt()
        else:
            raise ValueError(f"Unknown format '{fmt}'. Choose txt, json or srt.")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(payload)
