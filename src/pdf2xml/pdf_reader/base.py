
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

@dataclass
class DocMeta:
    title: str = ""
    abstract: str = ""
    authors: str = ""

class PDFReader(Protocol):
    def extract_meta(self, path: str) -> DocMeta: ...
