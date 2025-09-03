
from __future__ import annotations
from xml.etree.ElementTree import ElementTree

class ValidationReport:
    def __init__(self, ok: bool, message: str = "") -> None:
        self.ok = ok
        self.message = message or ("OK" if ok else "Failed")
    def __bool__(self) -> bool: return self.ok
    def summary(self) -> str: return self.message

def validate_article(tree: ElementTree) -> ValidationReport:
    root = tree.getroot()
    if root.tag != "article":
        return ValidationReport(False, f"Root must be <article>, got <{root.tag}>")
    required = ["front", "body", "back"]
    got = [c.tag for c in root]
    missing = [t for t in required if t not in got]
    if missing:
        return ValidationReport(False, f"Missing required children: {missing}")
    return ValidationReport(True, "XML well-formed and basic structure OK")
