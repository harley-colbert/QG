\
import pytest
import zipfile
from tests.conftest import resolve_module
from tests.helpers.fakes import FakeZipFile

m_inspector = None

@pytest.fixture(scope="module", autouse=True)
def _import_inspector():
    global m_inspector
    m_inspector = resolve_module("template_inspector")

NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

def _doc_xml(style=None, ilvl=None):
    pstyle = ""
    numpr = ""
    if style:
        pstyle = f'<w:pStyle w:val="{style}"/>'
    if ilvl is not None:
        numpr = f'<w:numPr><w:ilvl w:val="{ilvl}"/></w:numPr>'
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="{NS}">
  <w:body>
    <w:p>
      <w:pPr>
        {pstyle}
        {numpr}
      </w:pPr>
      <w:r><w:t>{{{{ requirements }}}}</w:t></w:r>
    </w:p>
  </w:body>
</w:document>'''
    return xml.encode("utf-8")

def test_style_list_bullet_3(monkeypatch, cap_word_log, tmp_path):
    xml = _doc_xml(style="List Bullet 3")
    fake = FakeZipFile(xml)
    monkeypatch.setattr(zipfile, "ZipFile", lambda *a, **k: fake)
    meta = m_inspector.discover_markers_and_levels(tmp_path/"dummy.docx")
    assert "requirements" in meta
    assert meta["requirements"]["base"] == 3

def test_style_listparagraph_ilvl2(monkeypatch, cap_word_log, tmp_path):
    xml = _doc_xml(style="List Paragraph", ilvl=2)
    fake = FakeZipFile(xml)
    monkeypatch.setattr(zipfile, "ZipFile", lambda *a, **k: fake)
    meta = m_inspector.discover_markers_and_levels(tmp_path/"dummy.docx")
    assert meta["requirements"]["base"] == 3

def test_no_style_no_ilvl_warns_base1(monkeypatch, cap_word_log, tmp_path):
    xml = _doc_xml(style=None, ilvl=None)
    fake = FakeZipFile(xml)
    monkeypatch.setattr(zipfile, "ZipFile", lambda *a, **k: fake)
    meta = m_inspector.discover_markers_and_levels(tmp_path/"dummy.docx")
    assert meta["requirements"]["base"] == 1
    assert any("WARN" in r.levelname for r in cap_word_log.records) or any("WARN" in r.message for r in cap_word_log.records)
