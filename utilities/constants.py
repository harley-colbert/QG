# services/word/constants.py
import logging

LOG_PREFIX = "[QUILL2DOC]"
WD_WITHIN_TABLE = 12  # WdInformation.wdWithInTable

# Only these exact dotted paths remain rich (HTML/Delta) – everything else becomes plain text.
EXCEPTION_HTML_FIELDS = {
    "data.zonefunctions.guardingdescription",
    "data.riskdescription.1",
    "data.zonefunctions.controlsdescription",
}

# Sizing rules for images keyed by content key (mm)
IMAGE_SIZE_LIMITS = {
    "customercontact.logo": (127, 45.72),
    "titleImage": (95.25, 57.15),
    "systemLayout.elevation": (158.75, 152.4),
    "systemLayout.end": (158.75, 152.4),
    "systemLayout.iso": (158.75, 152.4),
    "systemLayout.top": (158.75, 152.4),
    "systemLayout.title": (95.25, 57.15),
}

# --- ASCII-only filter to avoid UnicodeEncodeError on Windows cp1252 consoles ---
_ASCII_MAP = {
    "→": "->",
    "←": "<-",
    "↔": "<->",
    "⇒": "=>",
    "⇐": "<=",
    "⇔": "<=>",
    "—": "-",   # em dash
    "–": "-",   # en dash
    "•": "*",
    "·": "*",
    "“": '"',
    "”": '"',
    "„": '"',
    "’": "'",
    "‘": "'",
    "…": "...",
    "×": "x",
    "✓": "ok",
    "✔": "ok",
    "✗": "x",
    "✘": "x",
    "·": ".",
    "•": "*",
}

def _safe_ascii(s: str) -> str:
    # fast path
    try:
        s.encode("ascii")
        return s
    except UnicodeEncodeError:
        pass
    # replace known chars
    for k, v in _ASCII_MAP.items():
        if k in s:
            s = s.replace(k, v)
    # final guard: replace remaining non-ascii chars
    return s.encode("ascii", "replace").decode("ascii")

class AsciiSanitizerFilter(logging.Filter):
    """
    Logging filter that forces record message and args to ASCII-safe strings,
    preventing UnicodeEncodeError on cp1252 consoles.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = _safe_ascii(str(record.msg))
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: _safe_ascii(str(v)) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(_safe_ascii(str(a)) for a in record.args)
            else:
                record.args = _safe_ascii(str(record.args))
        return True

logger = logging.getLogger("quill2doc")
logger.setLevel(logging.DEBUG)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.addFilter(AsciiSanitizerFilter())  # <--- ASCII only
    formatter = logging.Formatter(
        f"%(asctime)s - {LOG_PREFIX} - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
