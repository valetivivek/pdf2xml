from __future__ import annotations
from typing import List
from .base import DocMeta
from ..utils.text import fix_ligatures, collapse_ws, unhyphenate, strip_superscripts_digits
import re

SECTION_BREAK_RE = re.compile(r"^(abstract|index terms|keywords|introduction|1\.|i\.)\b", re.I)
ABSTRACT_RE = re.compile(r"^abstract\b[:\-]?\s*$", re.I)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
AFFIL_HINT_RE = re.compile(
    r"\b(university|institute|department|school|hospital|laborator(y|ies)|center|centre|graduate|college)\b",
    re.I,
)

def _is_affiliation_line(s: str) -> bool:
    return bool(AFFIL_HINT_RE.search(s)) or "@" in s or s.lower().startswith(("corresponding author", "copyright", "©"))

class PyMuPDFReader:
    def __init__(self) -> None:
        try:
            import fitz  # PyMuPDF
        except Exception as e:
            raise RuntimeError("PyMuPDF (fitz) is not available") from e

    def _page_lines(self, doc, page_index: int) -> List[str]:
        text = doc.load_page(page_index).get_text("text")
        lines = [collapse_ws(fix_ligatures(ln)) for ln in text.splitlines()]
        return [ln for ln in lines if ln.strip()]

    def _find_title(self, lines: List[str]) -> str:
        return lines[0] if lines else "Untitled"

    def _find_abstract(self, lines: List[str]) -> str:
        for i, ln in enumerate(lines[:300]):
            if ABSTRACT_RE.match(ln):
                buf: List[str] = []
                for ln2 in lines[i+1:i+150]:
                    if not ln2.strip() or SECTION_BREAK_RE.match(ln2):
                        break
                    buf.append(ln2)
                return collapse_ws(unhyphenate(buf))
        return ""

    def _author_block_lines(self, lines: List[str], title: str) -> List[str]:
        # Collect between title and abstract/keywords; skip obvious affiliation lines.
        try:
            t_idx = lines.index(title)
        except ValueError:
            t_idx = 0
        block: List[str] = []
        for ln in lines[t_idx+1: t_idx+40]:  # generous window
            if ABSTRACT_RE.match(ln) or SECTION_BREAK_RE.match(ln):
                break
            if _is_affiliation_line(ln):
                continue
            # skip lines that are all caps & too long (often headers)
            if len(ln) > 80 and ln.upper() == ln:
                continue
            block.append(ln)
        return block

    def _extract_authors(self, lines: List[str], title: str) -> str:
        block_lines = self._author_block_lines(lines, title)
        if not block_lines:
            return ""
        block = " ".join(block_lines)
        block = EMAIL_RE.sub("", block)
        block = strip_superscripts_digits(block)
        # Split on commas, semicolons, " and ", "&"
        parts = re.split(r"\s*[,;]\s*|\s+and\s+|\s+&\s+", block)
        # Filter out affiliation-like fragments
        parts = [p for p in parts if p and not AFFIL_HINT_RE.search(p)]
        names: List[str] = []
        for p in parts:
            toks = p.split()
            if 1 <= len(toks) <= 3:
                names.append(" ".join(toks))
        # Deduplicate while preserving order
        seen = set()
        dedup = []
        for n in names:
            if n.lower() not in seen:
                seen.add(n.lower())
                dedup.append(n)
        return ", ".join(dedup[:16])

    def extract_meta(self, path: str) -> DocMeta:
        import fitz
        doc = fitz.open(path)
        try:
            lines: List[str] = []
            for p in range(min(3, doc.page_count)):  # up to first 3 pages
                lines.extend(self._page_lines(doc, p))

            title = self._find_title(lines)
            abstract = self._find_abstract(lines)
            authors = self._extract_authors(lines, title)
            return DocMeta(
                title=title or "Untitled",
                abstract=abstract,
                authors=authors
            )
        finally:
            doc.close()
