# services/word/handler.py
from __future__ import annotations

import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List

import jinja2
from docxtpl import DocxTemplate, Subdoc
from docx import Document

from .constants import logger, LOG_PREFIX  # your app-level logger + prefix
from .sanitize import sanitize_except_exceptions, strip_markup
from .images import replace_image_markers_xml
from .html_shim import ensure_html_wrapper_initialized, add_html_wrapper
from .quill_convert import to_semantic_html

# -------------------------------------------------------------------
# Config
# -------------------------------------------------------------------
# Convert ANY string that looks like HTML <ul>/<ol>/<li> into a Subdoc,
# in addition to the explicit EXCEPTION_HTML_FIELDS list in constants.
ENABLE_HTML_LIST_HEURISTIC = True

logger = logging.getLogger(__name__)
LOG_PREFIX = "[WORD]"

# -------------------------------------------------------------------
# Jinja helper: keep unknown placeholders as-is across passes
# -------------------------------------------------------------------
class PreserveUndefined(jinja2.Undefined):
    """
    Jinja Undefined that renders back into its original placeholder form,
    so unprovided variables persist across multi-pass/doc operations.
    """
    def _render_name(self) -> str:
        name = getattr(self, "_undefined_name", None)
        if name:
            return f"{{{{ {name} }}}}"
        hint = getattr(self, "_undefined_hint", None)
        if hint:
            return f"{{{{ {hint} }}}}"
        return "{{ undefined }}"

    def __str__(self) -> str:
        return self._render_name()

    def __unicode__(self) -> str:
        return self._render_name()

    def __html__(self) -> str:
        return self._render_name()

# -------------------------------------------------------------------
# Main handler
# -------------------------------------------------------------------
class WordSubmissionHandler:
    """
    Pipeline:
      1) Sanitize context (except whitelisted rich fields)
      2) Convert rich strings (HTML) into Subdocs
      3) Render ALL fields (plain + Subdocs) in ONE PASS
      4) Save a 'noimage - <finalname>.docx' copy
      5) Replace image markers at XML level
      6) Final save
    """

    def __init__(
        self,
        template_path: str,
        status_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.template_path = template_path
        self.status_callback = status_callback
        self.doc: Optional[Document] = None
        self.tpl: Optional[DocxTemplate] = None
        ensure_html_wrapper_initialized()
        logger.debug(f"{LOG_PREFIX} __init__: template_path={template_path!r}")

    # ---------------- misc ----------------
    def send_status(self, message: str) -> None:
        msg = f"{LOG_PREFIX} {message}"
        if self.status_callback:
            self.status_callback(msg)
        logger.info(msg)

    def load_template(self) -> None:
        self.send_status("Loading Word template...")
        if not os.path.isfile(self.template_path):
            raise FileNotFoundError(f"Template file not found: {self.template_path}")
        self.tpl = DocxTemplate(self.template_path)
        self.send_status("Template loaded successfully.")

    def _ensure_parent_dir(self, path_str: str) -> None:
        try:
            out_path = Path(path_str)
            out_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"{LOG_PREFIX} could not ensure parent dir for {path_str!r}: {e}")

    def _atomic_save_to(self, src_doc: Document, final_path: str) -> None:
        tmp_local = Path(tempfile.gettempdir()) / "docx_out_tmp.docx"
        src_doc.save(tmp_local)
        shutil.copy2(tmp_local, final_path)

    # ---------------- helpers: Subdoc build & heuristics ----------------
    def _build_preserve_env(self) -> jinja2.Environment:
        env = jinja2.Environment(autoescape=False, trim_blocks=True, lstrip_blocks=True)
        env.undefined = PreserveUndefined
        return env

    def _new_subdoc(self) -> Subdoc:
        if not self.tpl:
            raise RuntimeError("Template not loaded.")
        return self.tpl.new_subdoc()

    @staticmethod
    def _looks_like_html_list(val: Any) -> bool:
        if not ENABLE_HTML_LIST_HEURISTIC or not isinstance(val, str):
            return False
        v = val.lower()
        return ("<ul" in v) or ("<ol" in v) or ("<li" in v)

    def _build_subdoc_from_html(self, html: str) -> Subdoc:
        ensure_html_wrapper_initialized()
        sub = self._new_subdoc()
        add_html_wrapper(sub, html)
        return sub

    def _to_subdoc_html(self, value: str, path_label: str) -> Subdoc:
        """Convert rich HTML string to Subdoc; fall back to stripped <p> on errors."""
        try:
            html = to_semantic_html(value)
            logger.debug(
                f"{LOG_PREFIX} [HTML_CONVERSION] path={path_label} "
                f"len_in={len(value)}"
            )
        except Exception as e:
            logger.warning(f"{LOG_PREFIX} to_semantic_html failed at {path_label}: {e}; falling back to plain.")
            html = f"<p>{strip_markup(value)}</p>"
        return self._build_subdoc_from_html(html)

    def _transform_exceptions_to_subdocs(self, obj: Any, path: Optional[List[str]] = None) -> Any:
        """
        Recursively convert whitelisted rich fields (EXCEPTION_HTML_FIELDS)
        and values that look like HTML lists into Subdoc objects.
        """
        from .constants import EXCEPTION_HTML_FIELDS  # paths compared in lowercase
        if path is None:
            path = []

        if isinstance(obj, dict):
            out = {}
            for k, v in obj.items():
                preserved_path = ".".join(path + [k])      # keep casing in logs
                compare_path = preserved_path.lower()      # membership test only
                if isinstance(v, str) and (
                    compare_path in EXCEPTION_HTML_FIELDS or self._looks_like_html_list(v)
                ):
                    out[k] = self._to_subdoc_html(v, preserved_path)
                else:
                    out[k] = self._transform_exceptions_to_subdocs(v, path + [k])
            return out

        if isinstance(obj, list):
            return [self._transform_exceptions_to_subdocs(v, path) for v in obj]

        return obj

    @staticmethod
    def _flatten(obj: Any, prefix: str = "") -> Dict[str, Any]:
        """Flatten nested dict/list to dotted paths for debugging."""
        out: Dict[str, Any] = {}
        if isinstance(obj, dict):
            for k, v in obj.items():
                key = f"{prefix}.{k}" if prefix else k
                out.update(WordSubmissionHandler._flatten(v, key))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                key = f"{prefix}.{i}" if prefix else str(i)
                out.update(WordSubmissionHandler._flatten(v, key))
        else:
            out[prefix] = obj
        return out

    # ---------------- core ----------------
    def render_document(self, context: dict, output_path: str) -> None:
        logger.info(f"{LOG_PREFIX} [Render_Content] keys={list(context.keys())} output_path={output_path!r}")

        # 1) Sanitize (preserves EXCEPTION_HTML_FIELDS untouched)
        self.send_status("Step 1: Sanitizing context...")
        sanitized_context = sanitize_except_exceptions(context)

        # 2) Load template (single DocxTemplate instance for entire run)
        self.send_status("Step 2: Loading DOCX template...")
        self.load_template()
        assert self.tpl is not None

        # 3) Convert rich fields to Subdocs
        self.send_status("Step 3: Converting rich fields to Subdocs...")
        context_for_tpl = self._transform_exceptions_to_subdocs(sanitized_context)

        # Debug: which paths actually became Subdocs?
        flat = self._flatten(context_for_tpl)
        subdoc_paths = [k for k, v in flat.items() if isinstance(v, Subdoc)]
        self.send_status(f"Subdoc paths resolved: {subdoc_paths}")

        # 4) ONE-PASS RENDER (critical for keeping Subdoc rels intact)
        self.send_status("Step 4: Rendering all fields (including subdocs) in one pass...")
        preserve_env = self._build_preserve_env()
        logger.warning(f"{LOG_PREFIX} Content sent to jinja: {context_for_tpl}")
        self.tpl.render(context_for_tpl, jinja_env=preserve_env)

        # Save to a temp file (this version already contains rendered Subdocs)
        temp_doc_path = os.path.join(tempfile.gettempdir(), "temp_rendered.docx")
        self.tpl.save(temp_doc_path)

        # Save a pre-image copy next to the final file
        try:
            final_dir = os.path.dirname(output_path)
            final_name = os.path.basename(output_path)
            noimage_path = os.path.join(final_dir, f"noimage - {final_name}")
            self._ensure_parent_dir(noimage_path)
            shutil.copy2(temp_doc_path, noimage_path)
            self.send_status(f"Saved pre-image document to {noimage_path}")
        except Exception as e:
            logger.warning(f"{LOG_PREFIX} could not save pre-image document: {e}")

        # 5) Replace [[ Image: key ]] markers at the XML level
        self.send_status("Step 5: Replacing image markers (XML)...")
        replace_image_markers_xml(temp_doc_path, context)

        # 6) Final save
        self.doc = Document(temp_doc_path)
        self._ensure_parent_dir(output_path)
        try:
            self.doc.save(output_path)
        except FileNotFoundError:
            logger.warning(f"{LOG_PREFIX} save failed; retrying atomic copy.")
            self._atomic_save_to(self.doc, output_path)

        self.send_status(f"Document fully processed and saved to {output_path}")
