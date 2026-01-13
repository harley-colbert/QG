import pytest
from tests.helpers.factories import delta_bullets_base, delta_mixed, html_mixed
from tests.conftest import resolve_module

m_quill = None

@pytest.fixture(scope="module", autouse=True)
def _import_quill():
    global m_quill
    m_quill = resolve_module("quill_delta")

def test_parse_quill_delta_with_delta(cap_word_log):
    blocks = m_quill.parse_quill_delta(delta_bullets_base())
    assert isinstance(blocks, list)
    assert blocks == [
        {"type":"bullet", "indent":0, "text":"A"},
        {"type":"bullet", "indent":1, "text":"A.1"},
        {"type":"bullet", "indent":2, "text":"A.2"},
    ]
    assert any("[WORD]" in r.message and "[DELTA]" in r.message for r in cap_word_log.records)

def test_parse_quill_delta_mixed_and_html(cap_word_log):
    blocks = m_quill.parse_quill_delta(delta_mixed())
    assert [b["type"] for b in blocks] == ["bullet", "ordered", "ordered", "bullet", "paragraph"]
    html_blocks = m_quill.parse_quill_delta(html_mixed())
    assert any(b["type"] == "ordered" for b in html_blocks)
