import pytest
from tests.conftest import resolve_module

m_handler = None

@pytest.fixture(scope="module", autouse=True)
def _import_handler():
    global m_handler
    m_handler = resolve_module("handler")

@pytest.mark.skip(reason="Enable after integrating inspector/parser/renderer in handler.")
def test_handler_wiring_contract():
    assert hasattr(m_handler, "WordSubmissionHandler")
