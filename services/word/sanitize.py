# services/word/sanitize.py
from typing import Any, List, Optional
import warnings
from bs4 import BeautifulSoup
from bs4 import MarkupResemblesLocatorWarning

from .constants import EXCEPTION_HTML_FIELDS, logger, LOG_PREFIX

# Silence: "The input looks more like a filename than markup."
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


def strip_markup(text: Any) -> Any:
    """
    Remove all HTML markup from a string.
    Non-strings are returned unchanged.
    """
    if not isinstance(text, str):
        return text
    stripped = BeautifulSoup(text, "html.parser").get_text()
    logger.debug(
        f"{LOG_PREFIX} strip_markup: in_len={len(text)} out_len={len(stripped)}"
    )
    return stripped


def sanitize_except_exceptions(obj: Any, parent_path: Optional[List[str]] = None) -> Any:
    """
    Recursively sanitize strings in a nested structure, except for those fields
    explicitly listed in EXCEPTION_HTML_FIELDS.

    - Dict keys are preserved exactly as provided (no forced lowercase).
    - Full dotted path is compared against EXCEPTION_HTML_FIELDS using lowercase.
    - Rich fields (in the exception list) are left untouched.
    - Strings elsewhere are passed through strip_markup().
    """
    if parent_path is None:
        parent_path = []

    if isinstance(obj, dict):
        clean = {}
        for k, v in obj.items():
            # Preserve the actual key casing when building the new dict
            path = parent_path + [k]
            dotted_preserve = ".".join(path)
            dotted_lower = dotted_preserve.lower()

            if dotted_lower in EXCEPTION_HTML_FIELDS:
                logger.debug(f"{LOG_PREFIX} sanitize: KEEP-RICH path={dotted_preserve}")
                clean[k] = v
            else:
                clean[k] = sanitize_except_exceptions(v, path)
        return clean

    elif isinstance(obj, list):
        return [sanitize_except_exceptions(item, parent_path) for item in obj]

    elif isinstance(obj, str):
        s = strip_markup(obj)
        if s != obj:
            logger.debug(
                f"{LOG_PREFIX} sanitize: STRIPPED len_in={len(obj)} len_out={len(s)}"
            )
        return s

    else:
        return obj
