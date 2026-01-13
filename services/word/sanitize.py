# services/word/sanitize.py
from typing import Any, List, Optional
import re
import warnings
from bs4 import BeautifulSoup
from bs4 import MarkupResemblesLocatorWarning

from .constants import logger, LOG_PREFIX

# Silence: "The input looks more like a filename than markup."
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


_BLOCK_CLOSE_RE = re.compile(r"</\s*(p|div|li|ul|ol|h[1-6])\s*>", re.IGNORECASE)
_BREAK_RE = re.compile(r"<\s*br\s*/?\s*>", re.IGNORECASE)


def _normalize_markup_newlines(text: str) -> str:
    normalized = _BREAK_RE.sub("\n", text)
    normalized = _BLOCK_CLOSE_RE.sub("\n", normalized)
    return normalized


def strip_markup(text: Any) -> Any:
    """
    Remove all HTML markup from a string.
    Non-strings are returned unchanged.
    """
    if not isinstance(text, str):
        return text
    normalized = _normalize_markup_newlines(text)
    stripped = BeautifulSoup(normalized, "html.parser").get_text(separator="\n")
    stripped = stripped.replace("\r\n", "\n").replace("\r", "\n")
    stripped = re.sub(r"\n{3,}", "\n\n", stripped)
    logger.debug(
        f"{LOG_PREFIX} strip_markup: in_len={len(text)} out_len={len(stripped)}"
    )
    return stripped


def sanitize_plain_text(obj: Any, parent_path: Optional[List[str]] = None) -> Any:
    """
    Recursively sanitize strings in a nested structure to plain text.

    - Dict keys are preserved exactly as provided (no forced lowercase).
    - All strings are passed through strip_markup().
    """
    if parent_path is None:
        parent_path = []

    if isinstance(obj, dict):
        clean = {}
        for k, v in obj.items():
            path = parent_path + [k]
            clean[k] = sanitize_plain_text(v, path)
        return clean

    elif isinstance(obj, list):
        return [sanitize_plain_text(item, parent_path) for item in obj]

    elif isinstance(obj, str):
        s = strip_markup(obj)
        if s != obj:
            logger.debug(
                f"{LOG_PREFIX} sanitize: STRIPPED len_in={len(obj)} len_out={len(s)}"
            )
        return s

    else:
        return obj
