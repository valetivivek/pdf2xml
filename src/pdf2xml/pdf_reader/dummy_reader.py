
from __future__ import annotations
import os
from .base import DocMeta

class DummyReader:
    """Fallback reader: guess a title from filename."""
    def extract_meta(self, path: str) -> DocMeta:
        base = os.path.basename(path)
        title_guess = os.path.splitext(base)[0].replace("_"," ").replace("-"," ").strip()
        return DocMeta(title=title_guess or "Untitled", abstract="", authors="")
