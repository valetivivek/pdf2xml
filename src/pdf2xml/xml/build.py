
from __future__ import annotations
from typing import Dict, Any
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
import xml.dom.minidom as minidom

def build_minimal_article(meta: Dict[str, Any]) -> ElementTree:
    article = Element("article")
    front = SubElement(article, "front")
    article_meta = SubElement(front, "article-meta")
    title_group = SubElement(article_meta, "title-group")
    article_title = SubElement(title_group, "article-title")
    article_title.text = meta.get("title", "Untitled")
    contrib_group = SubElement(article_meta, "contrib-group")
    contrib = SubElement(contrib_group, "contrib")
    name = SubElement(contrib, "name")
    surname = SubElement(name, "surname"); surname.text = meta.get("author_surname", "Doe")
    given = SubElement(name, "given-names"); given.text = meta.get("author_given", "Jane")
    body = SubElement(article, "body")
    p = SubElement(body, "p"); p.text = meta.get("summary", "Scaffold body.")
    back = SubElement(article, "back")
    SubElement(back, "ref-list")
    return ElementTree(article)

def write_pretty(etree: ElementTree, out_path: str) -> None:
    xml_bytes = tostring(etree.getroot(), encoding="utf-8")
    pretty = minidom.parseString(xml_bytes).toprettyxml(indent="  ", encoding="utf-8")
    with open(out_path, "wb") as f:
        f.write(pretty)
