# word/helpers/jinja_list_levels.py
from __future__ import annotations
import re, zipfile
from dataclasses import dataclass
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET

W_NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
RE_VAR = re.compile(r'{{\s*(.*?)\s*}}')
RE_TAG = re.compile(r'{%\s*(.*?)\s*%}')
RE_IDENTIFIER = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')

@dataclass
class MarkerDetail:
    para_index: int
    paragraph_style: Optional[str]
    ilvl_zero_based: Optional[int]
    token_type: str
    token_raw: str
    key: str
    list_bullet_level: Optional[int]

class DocxJinjaListInspector:
    def __init__(self, details: List[MarkerDetail]) -> None:
        self.details = details
        self.marker_levels: Dict[str, int] = self._aggregate_levels(details)

    @classmethod
    def from_file(cls, docx_path: str) -> "DocxJinjaListInspector":
        with zipfile.ZipFile(docx_path, 'r') as zf:
            parts = cls._collect_xml_parts(zf)
            details: List[MarkerDetail] = []
            para_counter = 0
            for part in parts:
                xml = zf.read(part)
                root = ET.fromstring(xml)
                for p in root.findall('.//w:p', W_NS):
                    p_text = cls._paragraph_text(p)
                    p_style = cls._paragraph_style(p)
                    p_ilvl = cls._paragraph_ilvl(p)
                    any_token = False
                    for token_type, token_raw, key in cls._find_tokens(p_text):
                        any_token = True
                        level = cls._resolve_bullet_level(p_style, p_ilvl)
                        details.append(MarkerDetail(
                            para_index=para_counter,
                            paragraph_style=p_style,
                            ilvl_zero_based=p_ilvl,
                            token_type=token_type,
                            token_raw=token_raw,
                            key=key,
                            list_bullet_level=level
                        ))
                    if any_token:
                        para_counter += 1
        return cls(details)

    @staticmethod
    def _collect_xml_parts(zf: zipfile.ZipFile) -> List[str]:
        out = []
        for name in zf.namelist():
            low = name.lower()
            if not low.endswith('.xml'):
                continue
            if low in ('word/document.xml','word/footnotes.xml','word/endnotes.xml') or low.startswith('word/header') or low.startswith('word/footer'):
                out.append(name)
        out.sort(key=lambda p: (p != 'word/document.xml', p))
        return out

    @staticmethod
    def _paragraph_text(p_el: ET.Element) -> str:
        return ''.join((t.text or '') for t in p_el.findall('.//w:t', W_NS))

    @staticmethod
    def _paragraph_style(p_el: ET.Element) -> Optional[str]:
        pPr = p_el.find('w:pPr', W_NS)
        if pPr is None: return None
        pStyle = pPr.find('w:pStyle', W_NS)
        if pStyle is None: return None
        return pStyle.get('{%s}val' % W_NS['w'])

    @staticmethod
    def _paragraph_ilvl(p_el: ET.Element) -> Optional[int]:
        pPr = p_el.find('w:pPr', W_NS)
        if pPr is None: return None
        numPr = pPr.find('w:numPr', W_NS)
        if numPr is None: return None
        ilvl = numPr.find('w:ilvl', W_NS)
        if ilvl is None: return None
        val = ilvl.get('{%s}val' % W_NS['w'])
        if val is None: return None
        try: return int(val)
        except ValueError: return None

    @staticmethod
    def _find_tokens(text: str):
        for m in RE_VAR.finditer(text):
            inner = m.group(1)
            key = DocxJinjaListInspector._first_identifier(inner) or inner.strip()
            yield ('var', m.group(0), key)
        for m in RE_TAG.finditer(text):
            inner = m.group(1)
            key = DocxJinjaListInspector._first_identifier(inner) or inner.strip()
            yield ('tag', m.group(0), key)

    @staticmethod
    def _first_identifier(s: str) -> Optional[str]:
        m = RE_IDENTIFIER.search(s)
        return m.group(0) if m else None

    @staticmethod
    def _resolve_bullet_level(paragraph_style: Optional[str], ilvl_zero_based: Optional[int]) -> Optional[int]:
        if paragraph_style:
            norm = paragraph_style.strip().lower()
            if 'list' in norm and 'bullet' in norm:
                m = re.search(r'(\\d+)\\s*$', paragraph_style.strip())
                if m:
                    try:
                        lvl = int(m.group(1))
                        if 1 <= lvl <= 4:
                            return lvl
                    except ValueError:
                        pass
                return 1
        if ilvl_zero_based is not None and 0 <= ilvl_zero_based <= 3:
            return ilvl_zero_based + 1
        return None

    @staticmethod
    def _aggregate_levels(details: List[MarkerDetail]) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for d in details:
            if d.list_bullet_level is None: continue
            if d.key not in out:
                out[d.key] = d.list_bullet_level
        return out

def detect_marker_list_levels(docx_path: str) -> Dict[str, int]:
    return DocxJinjaListInspector.from_file(docx_path).marker_levels
