# word/list_level_probe.py
from __future__ import annotations
from typing import Dict

try:
    from .helpers.jinja_list_levels import detect_marker_list_levels
except Exception:
    from word.helpers.jinja_list_levels import detect_marker_list_levels  # type: ignore

def probe_marker_levels(template_path: str) -> Dict[str, int]:
    levels = detect_marker_list_levels(template_path)
    return {k: v for k, v in levels.items() if isinstance(v, int) and 1 <= v <= 4}
