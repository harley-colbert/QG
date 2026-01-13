import pytest
from tests.conftest import resolve_module

m_map = None

@pytest.fixture(scope="module", autouse=True)
def _import_mapper():
    global m_map
    m_map = resolve_module("list_mapper")

@pytest.mark.parametrize("base,indent,expected", [
    (1, 0, "List Bullet"),
    (1, 2, "List Bullet 3"),
    (3, 0, "List Bullet 3"),
    (3, 1, "List Bullet 4"),
])
def test_bullets(base, indent, expected, cap_word_log):
    block = {"type":"bullet","indent":indent,"text":"X"}
    style = m_map.compute_style(block, base, None)
    assert style == expected
    assert any("[WORD]" in r.message and "[MAP]" in r.message for r in cap_word_log.records)

def test_ordered(cap_word_log):
    block = {"type":"ordered","indent":1,"text":"X"}
    assert m_map.compute_style(block, 2, None) == "List Number 3"

def test_clamp_warn(cap_word_log):
    block = {"type":"bullet","indent":3,"text":"X"}
    style = m_map.compute_style(block, 8, None)
    assert style == "List Bullet 9"
    assert any("clamped to 9" in r.message for r in cap_word_log.records)

def test_paragraph_inherits_marker_style(cap_word_log):
    block = {"type":"paragraph","indent":0,"text":"Para"}
    style = m_map.compute_style(block, 1, "Heading 3")
    assert style == "Heading 3"
