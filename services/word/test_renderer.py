import pytest
from tests.conftest import resolve_module
from tests.helpers.fakes import FakeTemplate, FakeSubdoc

m_renderer = None

@pytest.fixture(scope="module", autouse=True)
def _import_renderer():
    global m_renderer
    m_renderer = resolve_module("renderer")

def test_render_quill_into_subdoc_with_fakes(cap_word_log):
    tpl = FakeTemplate()
    blocks = [
        {"type":"bullet","indent":0,"text":"A"},
        {"type":"bullet","indent":1,"text":"A.1"},
        {"type":"bullet","indent":2,"text":"A.2"},
    ]
    subdoc = m_renderer.render_quill_into_subdoc(tpl, blocks, base=3, marker_style="List Bullet 3")
    assert isinstance(subdoc, FakeSubdoc)
    assert subdoc.calls == [
        ("List Bullet 3", "A"),
        ("List Bullet 4", "A.1"),
        ("List Bullet 5", "A.2"),
    ]
    assert any("[WORD]" in r.message and "[RENDER]" in r.message for r in cap_word_log.records)
