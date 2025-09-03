from __future__ import annotations
import argparse, os
from .config import Config
from .pipeline import convert_pdf
from .xml.build import write_pretty
from .xml.validate import validate_article
from .utils.log import get_logger
from xml.etree.ElementTree import parse

def _cmd_convert(args):
    logger = get_logger()
    cfg = Config.load(args.config)
    tree, report = convert_pdf(args.input, cfg)
    out_path = args.output or (os.path.splitext(args.input)[0] + ".xml")
    write_pretty(tree, out_path)
    logger.info(f"Wrote XML -> {out_path}")
    print(report.summary())
    return 0

def _cmd_validate(args):
    tree = parse(args.input)
    vr = validate_article(tree)
    print(vr.summary())
    return 0 if vr.ok else 2

def _cmd_preview(args):
    print("Preview (stub): structure summary to be added in later steps.")
    return 0

def main(argv=None):
    parser = argparse.ArgumentParser(prog="pdf2xml", description="pdf2xml CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_conv = sub.add_parser("convert", help="Convert a single PDF to XML")
    p_conv.add_argument("input", help="Path to PDF file")
    p_conv.add_argument("-o","--output", help="Output XML path")
    p_conv.add_argument("-c","--config", help="YAML/JSON config path")
    p_conv.set_defaults(func=_cmd_convert)

    p_val = sub.add_parser("validate", help="Validate XML against basic schema")
    p_val.add_argument("input", help="Path to XML file")
    p_val.set_defaults(func=_cmd_validate)

    p_prev = sub.add_parser("preview", help="Preview detected document structure (stub)")
    p_prev.add_argument("input", help="Path to PDF file")
    p_prev.set_defaults(func=_cmd_preview)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
