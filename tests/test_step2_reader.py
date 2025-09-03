import sys
from pathlib import Path
SRC = Path(__file__).resolve().parents[2] / "src"
sys.path.insert(0, str(SRC))

from pdf2xml.config import Config
from pdf2xml.pipeline import convert_pdf

def test_dummy_reader_title_from_filename(tmp_path):
    pdf = tmp_path / "My_Sample-Paper.pdf"
    pdf.write_bytes(b"%PDF-1.1\n%%EOF\n")
    cfg = Config.load(None)
    cfg.reader = "dummy"
    tree, _ = convert_pdf(str(pdf), cfg)
    title = tree.getroot().find(".//article-title").text
    assert title == "My Sample Paper"

def test_cli_convert_creates_output(tmp_path):
    pdf = Path(__file__).parent / "data" / "sample1.pdf"
    cfg = Config.load(None)
    cfg.reader = "dummy"
    tree, _ = convert_pdf(str(pdf), cfg)
    assert tree.getroot().tag == "article"
