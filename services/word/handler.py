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
from .sanitize import sanitize_plain_text
from .images import replace_image_markers_xml

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
      1) Sanitize context to plain text
      2) Convert multiline strings into Subdocs
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

    # ---------------- helpers: Subdoc build ----------------
    def _build_preserve_env(self) -> jinja2.Environment:
        env = jinja2.Environment(autoescape=False, trim_blocks=True, lstrip_blocks=True)
        env.undefined = PreserveUndefined
        return env

    def _new_subdoc(self) -> Subdoc:
        if not self.tpl:
            raise RuntimeError("Template not loaded.")
        return self.tpl.new_subdoc()

    def _build_subdoc_from_lines(self, value: str) -> Subdoc:
        sub = self._new_subdoc()
        lines = value.splitlines() or [""]
        for line in lines:
            sub.add_paragraph(line)
        return sub

    def _transform_multiline_to_subdocs(self, obj: Any, path: Optional[List[str]] = None) -> Any:
        """
        Recursively convert multiline strings into Subdoc objects.
        Single-line strings remain unchanged.
        """
        if path is None:
            path = []

        if isinstance(obj, dict):
            out = {}
            for k, v in obj.items():
                if isinstance(v, str) and "\n" in v:
                    label = ".".join(path + [k])
                    logger.debug(f"{LOG_PREFIX} [MULTILINE] path={label} len_in={len(v)}")
                    out[k] = self._build_subdoc_from_lines(v)
                else:
                    out[k] = self._transform_multiline_to_subdocs(v, path + [k])
            return out

        if isinstance(obj, list):
            return [self._transform_multiline_to_subdocs(v, path) for v in obj]

        if isinstance(obj, str) and "\n" in obj:
            label = ".".join(path)
            logger.debug(f"{LOG_PREFIX} [MULTILINE] path={label} len_in={len(obj)}")
            return self._build_subdoc_from_lines(obj)

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

        # 1) Sanitize (strip markup to plain text)
        self.send_status("Step 1: Sanitizing context...")
        sanitized_context = sanitize_plain_text(context)

        # 2) Load template (single DocxTemplate instance for entire run)
        self.send_status("Step 2: Loading DOCX template...")
        self.load_template()
        assert self.tpl is not None

        # 3) Convert multiline strings to Subdocs
        self.send_status("Step 3: Converting multiline fields to Subdocs...")
        context_for_tpl = self._transform_multiline_to_subdocs(sanitized_context)

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
