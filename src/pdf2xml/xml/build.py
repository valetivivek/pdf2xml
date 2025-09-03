from __future__ import annotations
from typing import Dict, Any, List, Tuple
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
import xml.dom.minidom as minidom

def _split_name(full: str) -> Tuple[str, str]:
    """Naive split: everything except last token is given-names, last token is surname."""
    full = (full or "").strip()
    if not full:
        return ("Jane", "Doe")
    toks = full.split()
    if len(toks) == 1:
        return ("", toks[0])
    return (" ".join(toks[:-1]), toks[-1])

def _add_contrib(contrib_group: Element, full_name: str) -> None:
    given, surname = _split_name(full_name)
    contrib = SubElement(contrib_group, "contrib")
    name = SubElement(contrib, "name")
    s = SubElement(name, "surname"); s.text = surname or "Doe"
    g = SubElement(name, "given-names"); g.text = given or "Jane"

def build_minimal_article(meta: Dict[str, Any]) -> ElementTree:
    article = Element("article")

    front = SubElement(article, "front")
    article_meta = SubElement(front, "article-meta")
    title_group = SubElement(article_meta, "title-group")
    article_title = SubElement(title_group, "article-title")
    article_title.text = meta.get("title", "Untitled")

    contrib_group = SubElement(article_meta, "contrib-group")
    authors: List[str] = list(meta.get("authors_list") or [])
    if authors:
        for person in authors:
            _add_contrib(contrib_group, person)
    else:
        # Fallback single author (legacy behavior)
        _add_contrib(contrib_group, f"{meta.get('author_given','Jane')} {meta.get('author_surname','Doe')}")

    body = SubElement(article, "body")
    p = SubElement(body, "p")
    p.text = meta.get("summary", "Scaffold body.")

    back = SubElement(article, "back")
    SubElement(back, "ref-list")
    return ElementTree(article)

def write_pretty(etree: ElementTree, out_path: str) -> None:
    xml_bytes = tostring(etree.getroot(), encoding="utf-8")
    pretty = minidom.parseString(xml_bytes).toprettyxml(indent="  ", encoding="utf-8")
    with open(out_path, "wb") as f:
        f.write(pretty)
