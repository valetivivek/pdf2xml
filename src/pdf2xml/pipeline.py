from __future__ import annotations
import re
from .config import Config
from .utils.log import get_logger
from .xml.build import build_minimal_article
from .xml.validate import validate_article

class Report:
    def __init__(self, src: str) -> None:
        self.src = src
        self.sections = 0
        self.figures = 0
        self.tables = 0
        self.references = 0
        self.warnings = []
    def summary(self) -> str:
        return (f"File: {self.src}\n"
                f"Sections: {self.sections}, Figures: {self.figures}, "
                f"Tables: {self.tables}, References: {self.references}\n"
                f"Warnings: {len(self.warnings)}")

def _make_reader(name: str):
    logger = get_logger()
    name = (name or "").lower()
    if name == "pymupdf":
        try:
            from .pdf_reader.pymupdf_reader import PyMuPDFReader
            logger.info("Using PyMuPDFReader")
            return PyMuPDFReader()
        except Exception as e:
            logger.warning(f"Falling back to DummyReader: {e}")
    from .pdf_reader.dummy_reader import DummyReader
    logger.info("Using DummyReader")
    return DummyReader()

def _split_authors(authors_str: str) -> list[str]:
    """Split 'A B, C D and E F' into ['A B','C D','E F']."""
    if not authors_str:
        return []
    parts = re.split(r"\s*,\s*|\s+and\s+", authors_str)
    return [p.strip() for p in parts if p.strip()]

def convert_pdf(path: str, cfg: Config):
    logger = get_logger()
    logger.info("Starting conversion")
    reader = _make_reader(cfg.reader)
    meta = reader.extract_meta(path)

    authors_list = _split_authors(meta.authors)

    meta_dict = {
        "title": meta.title if meta.title else "Untitled",
        # kept for backward-compat fallback
        "author_surname": (meta.authors.split(",")[0].split()[-1] if meta.authors else "Doe"),
        "author_given": (meta.authors.split(",")[0].split()[0] if meta.authors else "Jane"),
        "authors_list": authors_list,   # NEW: full list for contrib-group
        "summary": meta.abstract or "This is a placeholder body; later steps will emit full sections.",
    }
    tree = build_minimal_article(meta_dict)
    rep = Report(path)
    vr = validate_article(tree)
    if not vr.ok:
        rep.warnings.append(vr.summary())
    logger.info(vr.summary())
    return tree, rep
