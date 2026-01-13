# word/quill_convert.py
from __future__ import annotations
import json
import re
from typing import Any, Dict, List, Tuple, Union
from .constants import logger, LOG_PREFIX

def looks_like_quill_delta(s: str) -> bool:
    test = s.strip()
    looks = test.startswith("{") and '"ops"' in test
    logger.debug(f"{LOG_PREFIX} looks_like_quill_delta: looks={looks} sample={test[:80].replace(chr(10),' ')}...")
    return looks

# ---------- NEW: public entry that handles Delta OR Quill-HTML OR plain HTML ----------
def to_semantic_html(value: Union[str, Dict[str, Any]]) -> str:
    """
    Accepts:
      - Quill Delta (dict or JSON string with {"ops":[...]})
      - Quill HTML (with class="ql-indent-N" on <li>)
      - Plain HTML
    Returns HTML with proper nested lists that html4docx understands.
    """
    # 1) Quill Delta?
    if isinstance(value, dict) and "ops" in value:
        return delta_to_html(value)
    if isinstance(value, str) and looks_like_quill_delta(value):
        try:
            return delta_to_html(value)
        except Exception as e:
            logger.warning(f"{LOG_PREFIX} to_semantic_html: delta_to_html failed; {e}. Falling back to escaped <p>.")
            return f"<p>{_esc(_safe_str(value))}</p>"

    # 2) Quill HTML classes?
    s = _safe_str(value)
    if "ql-indent-" in s:
        return _normalize_quill_html_lists(s)

    # 3) Plain HTML
    return s

# ---------- Your existing Delta → HTML (keep if you have a fuller version) ----------
def delta_to_html(delta: Union[str, Dict[str, Any]]) -> str:
    """
    Convert a Quill Delta to HTML with true nested lists.
    NOTE: This placeholder only validates the input and punts to your existing logic if present.
    Replace this with your own full implementation.
    """
    if isinstance(delta, str):
        try:
            raw_preview = delta[:200].replace("\n", "\\n")
            logger.debug(f"{LOG_PREFIX} delta_to_html: str input preview={raw_preview!r}")
            delta = json.loads(delta)
            logger.debug(f"{LOG_PREFIX} delta_to_html: parsed JSON ok")
        except Exception as e:
            from .sanitize import strip_markup
            logger.warning(f"{LOG_PREFIX} delta_to_html: invalid JSON; fallback to escaped paragraph. err={e}")
            return f"<p>{strip_markup(delta)}</p>"

    ops: List[Dict[str, Any]] = list(delta.get("ops", []))
    logger.debug(f"{LOG_PREFIX} delta_to_html: ops_count={len(ops)}")
    # If you have a complete implementation, put it here.
    # For now, join plain text lines as paragraphs:
    paras: List[str] = []
    buf: List[str] = []
    for op in ops:
        ins = op.get("insert")
        if isinstance(ins, str):
            parts = ins.split("\n")
            for i, part in enumerate(parts):
                if i < len(parts) - 1:
                    buf.append(part)
                    paras.append("<p>" + _esc("".join(buf)) + "</p>")
                    buf = []
                else:
                    buf.append(part)
        else:
            # embeds ignored here
            pass
    if buf:
        paras.append("<p>" + _esc("".join(buf)) + "</p>")
    return "".join(paras)

# ---------- Quill-HTML normalizer (ql-indent-* → nested UL, inside prior <li>) ----------
_INDENT_RE = re.compile(r"\bql-indent-(\d+)\b", re.IGNORECASE)

def _normalize_quill_html_lists(html: str) -> str:
    """
    Convert a single top-level UL/OL containing <li class="ql-indent-N"> into true nesting.
    If multiple lists exist, you can call this per field (your pipeline does per-field conversion).
    Keeps UL even if original used <ol> + classes (extend as needed).
    """
    # Extract all <li ...> ... </li> in order
    items: List[Tuple[int, str]] = []
    pos = 0
    while True:
        li_start = html.find("<li", pos)
        if li_start < 0:
            break
        tag_end = html.find(">", li_start)
        if tag_end < 0:
            break
        close = html.find("</li>", tag_end)
        if close < 0:
            break
        head = html[li_start:tag_end+1]
        body = html[tag_end+1:close].replace("\xa0", " ").strip()
        depth = 0
        m = _INDENT_RE.search(head)
        if m:
            try:
                depth = max(0, int(m.group(1)))
            except ValueError:
                depth = 0
        items.append((depth, _strip_tags(body)))
        pos = close + 5

    if not items:
        return html  # nothing to change

    out: List[str] = []
    current_depth = -1
    open_lists = 0

    def open_list():
        nonlocal open_lists
        out.append("<ul>")
        open_lists += 1

    def close_list():
        nonlocal open_lists
        out.append("</ul>")
        open_lists -= 1

    def open_li(text: str):
        out.append(f"<li>{_esc(text)}")

    def close_li():
        out.append("</li>")

    for depth, text in items:
        if depth > current_depth:
            while current_depth < depth:
                if current_depth >= 0:
                    out.append("<ul>")
                    open_lists += 1
                else:
                    open_list()
                current_depth += 1
        elif depth < current_depth:
            close_li()
            while current_depth > depth:
                close_list()
                current_depth -= 1
        else:
            # same level
            if out and out[-1] != "<ul>":
                close_li()
        open_li(text)

    close_li()
    while open_lists > 0:
        close_list()
        open_lists -= 1

    return "".join(out)

# ---------- utils ----------
def _safe_str(v: Any) -> str:
    return v if isinstance(v, str) else str(v)

def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

_TAG_RE = re.compile(r"<(/?)([a-zA-Z0-9]+)(\s[^>]*)?>")
def _strip_tags(s: str) -> str:
    # Very light inline cleanup: remove wrapping tags but keep inner text. Good enough for Quill list items.
    # If you need robust HTML handling, you can switch to BeautifulSoup here.
    return re.sub(_TAG_RE, "", s).strip()
