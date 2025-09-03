from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any, Dict
import os, json

def _load_kv_lines(path: str) -> Dict[str, Any]:
    cfg: Dict[str, Any] = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            if ":" in line:
                k, v = line.split(":", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg

def _load_mapping(path: str) -> Dict[str, Any]:
    try:
        import yaml  # type: ignore
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict): return data
    except Exception: pass
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict): return data
    except Exception: pass
    return _load_kv_lines(path)

@dataclass
class Config:
    reader: str = "pymupdf"      # "pymupdf" or "dummy"
    enable_ocr: bool = False
    table_extractor: str = "camelot"
    page_ranges: str = "all"
    detect_columns: bool = True
    strip_headers_footers: bool = True
    normalize_affiliations: bool = True
    reference_style: str = "auto"
    emit_base64_figures: bool = False
    emit_tables_as_html: bool = True
    timeout_sec: int = 120

    @classmethod
    def load(cls, path: Optional[str]) -> "Config":
        if path is None:
            return cls()
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config not found: {path}")
        m = _load_mapping(path)
        def b(x: Any, d: bool) -> bool:
            if isinstance(x, bool): return x
            if isinstance(x, str): return x.lower() in {"1","true","yes","on"}
            return d
        return cls(
            reader=str(m.get("reader", cls.reader)),
            enable_ocr=b(m.get("enable_ocr", cls.enable_ocr), cls.enable_ocr),
            table_extractor=str(m.get("table_extractor", cls.table_extractor)),
            page_ranges=str(m.get("page_ranges", cls.page_ranges)),
            detect_columns=b(m.get("detect_columns", cls.detect_columns), cls.detect_columns),
            strip_headers_footers=b(m.get("strip_headers_footers", cls.strip_headers_footers), cls.strip_headers_footers),
            normalize_affiliations=b(m.get("normalize_affiliations", cls.normalize_affiliations), cls.normalize_affiliations),
            reference_style=str(m.get("reference_style", cls.reference_style)),
            emit_base64_figures=b(m.get("emit_base64_figures", cls.emit_base64_figures), cls.emit_base64_figures),
            emit_tables_as_html=b(m.get("emit_tables_as_html", cls.emit_tables_as_html), cls.emit_tables_as_html),
            timeout_sec=int(m.get("timeout_sec", cls.timeout_sec)),
        )
