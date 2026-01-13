#!/usr/bin/env python3
# File: views/pywebview_api.py

import logging
import os
import traceback
import datetime
import webview
from typing import Optional
from services.oee_service import compute_oee
from pathlib import Path
from config.settings import Settings
from viewmodels.quote_viewmodel import QuoteViewModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class PyWebViewAPI:
    def __init__(self, viewmodel: QuoteViewModel) -> None:
        self.vm = viewmodel
        # Will be set in main.py after window creation:
        self._window: Optional[webview.Window] = None
        self.logger = logger

    # -------------------------
    # Flat view‐store bridge
    # -------------------------
    def get_all_fields(self) -> dict:
        """
        Return a flat map of every field in quote.data:
          "data.Category.fieldName" → "value"
        """
        return self.vm.get_all_fields()

    def set_all_fields(self, flat_map: dict) -> None:
        """
        Accept a flat map from the front-end and merge it into quote.data.
        """
        self.vm.set_all_fields(flat_map)


    def browse_save_file(self, default_filename="Quote.docx", title="Save As...", filetypes=None):
        import webview
        import os

        if filetypes is None:
            filetypes = [["Word Document", "*.docx"]]
        # Call the dialog
        file_paths = webview.windows[0].create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename=default_filename,
            file_types=filetypes,
            allow_multiple=False,
            title=title
        )
        if not file_paths:
            return None  # User cancelled
        if not filename.lower().endswith('.docx'):
            return filename + '.docx'
        return filename



    def get_quote_type(self) -> str:
        """
        Let JS know whether we're in 'budgetary' or 'final' mode.
        """
        return self.vm.quote_type

    def get_optional_categories(self) -> list:
        """
        Return the list of category names that should be marked `.optional`.
        Sourced from headers.py (or wherever your VM exposes it).
        """
        return self.vm.get_optional_categories()
        
    # -------------------------
    # Quote persistence & lifecycle
    # -------------------------
    def save_quote(self, quote_type) -> dict:
        """
        Prompt Save As, then persist all fields from the JS store and write XML.
        Assumes JS has already called set_all_fields(viewStore).
        """
        if not self._window:
            self.logger.error("Window not set for save_quote()")
            return

        # (unchanged) Show Save dialog...
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_dir = str(Settings.get_backup_path())
        paths = self._window.create_file_dialog(
            webview.SAVE_DIALOG,
            directory=default_dir,
            file_types=["XML files (*.xml)"],
            allow_multiple=False
        )
        if not paths:
            self.logger.info("User cancelled save dialog")
            return {}

        xml_path = paths[0] if isinstance(paths, (list, tuple)) else paths
        try:
            # Persist XML from the one Quote.data map
            self.vm.save_quote(xml_path, quote_type)
            self.logger.info(f"Quote saved to {xml_path}")
            return {
                "path": xml_path,
                "savedAt": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to save quote to {xml_path}: {e}", exc_info=True)
            raise

    
    def spell_check_categories(self) -> dict:
        """
        Returns a map of field‐keys → misspelled words for all spellcheck categories.
        """
        return self.vm.spell_check_categories()

    def new_quote(self) -> None:
        self.vm.model.quotes.clear()
        self.logger.info("Initialized new quote")

    # views/pywebview_api.py
    def submit_quote(self, template_path: str, output_path: str) -> None:
        """
        Generate a Word document from the given template using the current quote data.
        Exposed to JS via pywebview.
        """
        try:
            # Here is the key: define a callback to call JS
            def status_callback(msg):
                import json
                if self._window:
                    # Uses evaluate_js to update the modal live
                    safe_msg = json.dumps(str(msg))
                    self._window.evaluate_js(f"window.updateSubmissionStatus({safe_msg})")

            self.logger.info(f"Generating Word document: {output_path}")
            # Pass the status_callback to the handler
            self.vm.submit_quote(template_path, output_path, status_callback=status_callback)
            self.logger.info(f"Word document generated: {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to generate Word document: {e}\n{traceback.format_exc()}")
            raise

            
    # views/pywebview_api.py

    def open_quote(self) -> dict:
        """
        Prompt Open, load XML into the VM, then return:
          - quoteType:   "budgetary" or "final"
          - quotes:      the flat quotes dict for headers/UI lists
          - fields:      the flat field→value map for viewStore
        """
        if not self._window:
            self.logger.error("Window not set for open_quote()")
            return {}

        default_dir = str(Settings.get_backup_path())
        paths = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            directory=default_dir,
            file_types=["XML files (*.xml)"],
            allow_multiple=False
        )
        if not paths:
            return {}

        filename = paths[0] if isinstance(paths, (list, tuple)) else paths
        # 1) load into the single Quote instance
        quotes_data = self.vm.load_quote(filename)

        # 2) ask VM which view we should show
        quote_type = self.vm.quote_type

        # 3) grab every field so JS can repopulate its store
        all_fields = self.vm.get_all_fields()

        return {
            "quoteType": quote_type,
            "quotes": quotes_data,
            "fields": all_fields,
            "path": filename
        }

    # -------------------------
    # Rich‑text / data fields
    # -------------------------
    def set_field(self, full_key: str, value: str) -> None:
        self.vm.set_field(full_key, value)

    def get_field(self, full_key: str) -> Optional[str]:
        return self.vm.get_field(full_key)

    # -------------------------
    # Business logic endpoints
    # -------------------------
    
    # ↓↓↓ ADD THIS BLOCK ↓↓↓
    def calc_oee(self, payload: dict) -> dict:
        """
        Front-end helper: expects a JSON/dict with the six raw numbers
        exactly as produced by the OEE form.  Hands the dict straight
        to services.oee_service.compute_oee() and returns its result.
        """
        try:
            return compute_oee(payload)
        except Exception as exc:
            self.logger.error("OEE calculation failed", exc_info=True)
            return {}
    # ↑↑↑ END NEW BLOCK ↑↑↑


    def clear_field(self, key: str) -> bool:
        """
        Clears (resets to empty) the value for a specific field key.
        """
        try:
            logging.info(f"Clearing field: {key}")
            self.vm.set_field(key, "")  # ✅ Direct call, no await
            return True
        except Exception as e:
            logging.error(f"Error clearing field {key}: {e}")
            return False



    def compute_milestones(self, cost_grid_file: str) -> dict:
        return self.vm.compute_milestones(cost_grid_file)

    def spell_check_quote(self, text: Optional[str] = None) -> dict:
        return self.vm.spell_check_quote(text)

    # -------------------------
    # Expose project cost retrieval
    # -------------------------
    def get_project_cost(self, cost_grid_file: str) -> str:
        try:
            project_cost = self.vm.get_project_cost(cost_grid_file)
            self.logger.info(f"Project cost obtained from {cost_grid_file}: {project_cost}")
            return project_cost
        except Exception as e:
            self.logger.error(f"Error retrieving project cost: {e}", exc_info=True)
            return -1.0

    # -----------------------------------------------------------------
    # Folder-browsing helpers – NEW
    # -----------------------------------------------------------------
    def _browse_folder(self) -> str:
        """Open a folder-selection dialog and return the chosen path."""
        if not self._window:
            self.logger.error("Window not set for folder dialog")
            return ""
        paths = self._window.create_file_dialog(webview.FOLDER_DIALOG, allow_multiple=False)
        return paths[0] if paths else ""

    def browse_db_folder(self) -> str:
        """Return a folder chosen to store *database* files."""
        return self._browse_folder()

    def browse_log_folder(self) -> str:
        """Return a folder chosen to store *log* files."""
        return self._browse_folder()


    # -------------------------
    # Category metadata endpoints
    # -------------------------
    def get_file_browse_fields(self):
        # Convert the dictionary to a JSON-serializable format if necessary.
        return self.vm.get_file_browse_fields()
    
    def get_categories(self, quote_type: str) -> list:
        return self.vm.get_categories(quote_type)

    def get_category_fields(self, category: str) -> list:
        return self.vm.get_category_fields(category)

    def category_can_add(self, category: str) -> list:
        return self.vm.category_can_add(category)

    def get_special_lists(self) -> dict:
        return self.vm.get_special_lists()

    def browse_file_field(self) -> str:
        """
        Opens a file open dialog for file browsing fields.
        Returns the selected file path.
        """
        if not self._window:
            self.logger.error("Window not set for browse_file_field()")
            return ""
        paths = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            file_types=["All Files (*.*)"],
            allow_multiple=False
        )
        if not paths:
            self.logger.info("User cancelled file browsing dialog")
            return ""
        return paths[0]








    # -------------------------
    # Alliance Contacts CRUD
    # -------------------------
    def get_alliance_contacts(self) -> dict:
        return self.vm.get_alliance_contacts()

    def add_alliance_contact(self, contact_data: dict) -> None:
        self.vm.add_alliance_contact(contact_data)

    def update_alliance_contact(self, contact_data: dict) -> None:
        self.vm.update_alliance_contact(contact_data)

    def delete_alliance_contact(self, contact_id: int) -> None:
        self.vm.delete_alliance_contact(contact_id)

    # -------------------------
    # Application Settings CRUD
    # -------------------------
    def get_app_settings(self) -> dict:
        return self.vm.get_app_settings()

    def update_app_settings(self, new_settings: dict) -> None:
        self.vm.update_app_settings(new_settings)

    # -------------------------
    # Word‑template file dialog
    # -------------------------
    def browse_template_file(self) -> str:
        """
        Prompt the user to select a .docx template file.
        """
        if not self._window:
            self.logger.error("Window not set for browse_template_file()")
            return ""

        paths = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            file_types=["Word documents (*.docx)"],
            allow_multiple=False
        )
        return paths[0] if paths else ""
