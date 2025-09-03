from __future__ import annotations
import re
from typing import Iterable

_LIGATURES = {
    "ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl",
    "ﬅ": "ft", "ﬆ": "st",
    "’": "'", "“": '"', "”": '"', "—": "-", "–": "-",
    "\u00a0": " ",
    "Ã—": "×",            # ← fix 128Ã×128
    "ï¬": "fi",
}

def fix_ligatures(s: str) -> str:
    for k, v in _LIGATURES.items():
        s = s.replace(k, v)
    return s

def collapse_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def unhyphenate(lines: Iterable[str]) -> str:
    text = "\n".join(lines)
    text = re.sub(r"-\n(?=[a-z])", "", text)
    text = re.sub(r"\n+", " ", text)
    return collapse_ws(text)

def strip_superscripts_digits(s: str) -> str:
    s = re.sub(r"[0-9\u00B2\u00B3\u00B9\u2070-\u209F\u2020\u2021]+", "", s)
    return collapse_ws(s)
