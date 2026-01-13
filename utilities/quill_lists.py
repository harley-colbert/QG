# utilities/quill_lists.py
# Tools to normalize Quill lists and sanitize common paste artifacts.

from __future__ import annotations
import re
from typing import Optional, Tuple

from .constants import logger, LOG_PREFIX

try:
    # BeautifulSoup gives us robust HTML surgery. We fall back to a regex path if not present.
    from bs4 import BeautifulSoup, Tag  # type: ignore
except Exception:  # pragma: no cover
    BeautifulSoup = None  # type: ignore
    Tag = None  # type: ignore

_INDENT_RE = re.compile(r"\bql-indent-(\d+)\b")
_EMPTY_ANCHOR_RE = re.compile(r"<\s*a\b(?![^>]*\bhref=)[^>]*>(.*?)</a\s*>", re.I | re.S)

def _indent_of(tag) -> int:
    """
    Return indent level from class list (ql-indent-N). Defaults to 0.
    Works for Tag or dict-like with "class".
    """
    try:
        classes = tag.get("class", [])
    except Exception:
        classes = []
    if not classes:
        return 0
    for c in classes:
        m = _INDENT_RE.search(str(c))
        if m:
            return int(m.group(1))
    return 0

def _strip_indent_class(tag) -> None:
    try:
        classes = tag.get("class", [])
        if not classes:
            return
        tag["class"] = [c for c in classes if not _INDENT_RE.match(str(c))]
        if not tag["class"]:
            del tag["class"]
    except Exception:
        pass

def _bs_normalize_list(list_tag: Tag) -> Tag:
    """
    Given a <ul>/<ol> whose <li> children use ql-indent-N, rebuild it into
    a properly nested list tree. Returns a NEW list tag to replace the old one.
    """
    kind = list_tag.name  # "ul" or "ol"
    new_root = list_tag.__class__(name=kind)  # type: ignore
    stack: list[Tuple[int, Tag]] = [(0, new_root)]  # (level, list_tag)
    last_li_for_level: dict[int, Tag] = {}

    # Collect original <li> in order
    items = [child for child in list_tag.children if getattr(child, "name", None) == "li"]
    for li in items:
        level = _indent_of(li)
        _strip_indent_class(li)

        # Ensure stack depth == level
        while stack and stack[-1][0] > level:
            stack.pop()
        while stack and stack[-1][0] < level:
            # create an inner list under the last <li> at current top
            if stack[-1][0] not in last_li_for_level:
                # If user indented without a preceding parent <li>, create a stub
                stub_li = list_tag.__class__(name="li")  # type: ignore
                stub_li.append(list_tag.new_string(""))  # type: ignore
                stack[-1][1].append(stub_li)
                last_li_for_level[stack[-1][0]] = stub_li
            parent_li = last_li_for_level[stack[-1][0]]
            inner = list_tag.__class__(name=kind)  # type: ignore
            parent_li.append(inner)
            stack.append((stack[-1][0] + 1, inner))

        # Append a fresh LI (detach to avoid moving sublists twice)
        fresh_li = list_tag.__class__(name="li")  # type: ignore
        # Move children from original li to fresh_li
        for child in list(li.contents):
            fresh_li.append(child.extract())
        stack[-1][1].append(fresh_li)
        last_li_for_level[level] = fresh_li

    return new_root

def _regex_normalize_simple_quill_ul(html: str) -> str:
    """
    Fallback for environments without BeautifulSoup.
    Handles the common case where a single <ul> contains sibling <li class="ql-indent-N"> entries.
    """
    ul_pat = re.compile(r"(<ul[^>]*>)(.*?)(</ul>)", re.S | re.I)

    def rebuild(m):
        opener, inner, closer = m.group(1), m.group(2), m.group(3)
        lis = re.findall(r"<li([^>]*)>(.*?)</li>", inner, re.S | re.I)
        if not lis:
            return m.group(0)

        def level(attrs: str) -> int:
            mm = _INDENT_RE.search(attrs or "")
            return int(mm.group(1)) if mm else 0

        out = []
        cur_level = 0
        def open_lists(to_level):
            nonlocal cur_level
            while cur_level < to_level:
                out.append("<ul>")
                cur_level += 1
        def close_lists(to_level):
            nonlocal cur_level
            while cur_level > to_level:
                out.append("</ul>")
                cur_level -= 1

        out.append("<ul>")
        for attrs, body in lis:
            lvl = level(attrs)
            # strip ql-indent-* from attrs
            attrs = re.sub(r"\s*\bclass\s*=\s*\"([^\"]*)\"", lambda mm: _strip_ql_from_class(mm.group(0)), attrs)
            open_lists(lvl)
            close_lists(lvl)
            out.append(f"<li{attrs}>{body}</li>")
        close_lists(0)
        out.append("</ul>")
        return "".join(out)

    def _strip_ql_from_class(attr_text: str) -> str:
        # attr_text includes full class="..."
        cls_m = re.search(r"class\s*=\s*\"([^\"]*)\"", attr_text)
        if not cls_m:
            return attr_text
        classes = [c for c in cls_m.group(1).split() if not _INDENT_RE.match(c)]
        if classes:
            return f'class="{" ".join(classes)}"'
        # remove the whole class=""
        return ""

    return ul_pat.sub(rebuild, html)

def strip_orphan_anchors(html: str) -> str:
    """
    Remove <a> tags that do not have an href (Word renders them like links anyway).
    """
    if BeautifulSoup is not None:
        soup = BeautifulSoup(html, "html.parser")
        removed = 0
        for a in list(soup.find_all("a")):
            href = a.get("href")
            if href is None or str(href).strip() == "":
                a.unwrap()  # keep inner text
                removed += 1
        if removed:
            logger.debug(f"{LOG_PREFIX} quill_lists: stripped {removed} orphan anchors")
        return str(soup)
    # Regex fallback
    out = _EMPTY_ANCHOR_RE.sub(r"\1", html)
    if out != html:
        logger.debug(f"{LOG_PREFIX} quill_lists: stripped orphan anchors via regex")
    return out

def normalize_quill_lists(html: str) -> str:
    """
    Main entry: convert Quill's ql-indent-* markers on <li> into nested <ul>/<ol>
    and strip empty anchors. Idempotent: safe to run multiple times.
    """
    if not html:
        return html

    # First, strip empty anchors (fixes random 'a ' turning blue in Word)
    html = strip_orphan_anchors(html)

    if BeautifulSoup is not None:
        soup = BeautifulSoup(html, "html.parser")
        changed = 0
        for lst in list(soup.find_all(["ul", "ol"])):
            # If any child LI has ql-indent-*, rebuild this list
            li_children = [c for c in lst.children if getattr(c, "name", None) == "li"]
            if not li_children:
                continue
            if not any(_INDENT_RE.search(" ".join(c.get("class", []) or [])) for c in li_children):
                continue
            new_list = _bs_normalize_list(lst)
            lst.replace_with(new_list)
            changed += 1
        if changed:
            logger.debug(f"{LOG_PREFIX} quill_lists: normalized {changed} list(s) from ql-indent-* to nested lists")
        return str(soup)

    # Fallback: regex-based normalizer for the simple (flat-UL) case
    out = _regex_normalize_simple_quill_ul(html)
    if out != html:
        logger.debug(f"{LOG_PREFIX} quill_lists: regex-normalized lists (BeautifulSoup unavailable)")
    return out
