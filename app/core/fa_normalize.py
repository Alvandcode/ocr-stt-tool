"""Persian text normalization (hazm if available, stdlib fallback otherwise)."""

from __future__ import annotations

import re

# Arabic-lookalike chars -> Persian counterparts.
_FALLBACK_MAP = str.maketrans(
    {
        "ي": "ی",  # Arabic Yeh -> Persian Yeh
        "ك": "ک",  # Arabic Kaf -> Persian Kaf
        "ة": "ه",  # Teh Marbuta -> Heh
        "ؤ": "و",
        "إ": "ا",
        "أ": "ا",
        "ٱ": "ا",
    }
)
_WS_RE = re.compile(r"[ \t\u200c]{2,}")


def _fallback_normalize(text: str) -> str:
    text = text.translate(_FALLBACK_MAP)
    # Collapse repeated spaces/half-spaces, strip each line.
    lines = [_WS_RE.sub(" ", line).strip() for line in text.splitlines()]
    return "\n".join(lines).strip()


def normalize_persian(text: str, use_hazm: bool = True) -> str:
    """Normalize Persian text for stable, searchable output.

    Uses ``hazm.Normalizer`` when installed (and ``use_hazm`` is True),
    otherwise a small stdlib fallback (Arabic Yeh/Kaf fixes + whitespace
    cleanup). Never raises for missing hazm -- falls back silently.
    """
    if not text:
        return ""
    if use_hazm:
        try:
            from hazm import Normalizer

            return Normalizer().normalize(text).strip()
        except ImportError:
            pass
    return _fallback_normalize(text)
