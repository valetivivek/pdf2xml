import sys
from pathlib import Path
SRC = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(SRC))

from pdf2xml.config import Config
from pdf2xml.pipeline import convert_pdf

def test_convert_returns_tree_and_report(tmp_path):
    cfg = Config.load(None)
    cfg.reader = "dummy"
    sample = Path(__file__).parent / "data" / "sample1.pdf"
    tree, report = convert_pdf(str(sample), cfg)
    assert tree.getroot().tag == "article"
    assert report.src.endswith("sample1.pdf")
