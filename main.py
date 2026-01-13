#!/usr/bin/env python3
# File: main.py
# Hierarchy: QuoteGenerator > main.py
# Description: Entry point for the Quote Generator application using a PyWebView-based GUI.

import logging
import sys
import os
import atexit
import signal
from pathlib import Path
from typing import Any

import webview

from config.config_manager import ConfigManager
from config.settings import Settings
from services.database_manager import DatabaseManager
from services.sync_service import SyncService
from models.quote_model import QuoteModel
from viewmodels.quote_viewmodel import QuoteViewModel
from views.pywebview_api import PyWebViewAPI

# ========== Standalone Save File Dialog Function ==========
def browse_save_file():
    """
    Opens a native Windows save file dialog and returns the selected path.
    This is used for letting the user choose the output path for generated Word documents.
    """
    import tkinter as tk
    from tkinter import filedialog

    # Use a hidden root window so only the dialog is shown
    root = tk.Tk()
    root.withdraw()
    # Windows-specific filetypes and dialog
    file_path = filedialog.asksaveasfilename(
        title="Select file to save",
        filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
    )
    root.destroy()
    return file_path

# ========== Logging Setup ==========
def setup_logging() -> None:
    """
    Sets up robust logging for the application.
    Logs are written to both the console and a rotating log file.
    """
    try:
        log_path: Path = Settings.LOCAL_STORAGE["log_path"]
        log_path.mkdir(parents=True, exist_ok=True)
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            str(log_path / "quote_generator.log"), maxBytes=5 * 1024 * 1024, backupCount=5
        )
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        # Configure the root logger with both file and console handlers.
        logging.basicConfig(level=logging.INFO, handlers=[file_handler, logging.StreamHandler()])
        logging.info("Logging configured successfully.")
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        sys.exit(1)

# ========== Shutdown Handler ==========
def register_shutdown_handler(sync_service: SyncService) -> None:
    """
    Registers shutdown handlers to gracefully stop background services.
    """
    def handle_shutdown(sig: Any, frame: Any) -> None:
        logging.info("Shutdown signal received. Stopping background services...")
        try:
            sync_service.stop_sync_thread()
        except Exception as ex:
            logging.error(f"Error during shutdown: {ex}", exc_info=True)
        sys.exit(0)

    atexit.register(lambda: logging.info("Application cleanup completed."))
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

# ========== Main Application Entry ==========
def main() -> None:
    setup_logging()
    logging.info("Starting Quote Generator Application.")

    # Initialize application paths and directories.
    Settings.initialize_paths()

    # Instantiate configuration and services.
    config_manager: ConfigManager = ConfigManager()
    db_manager: DatabaseManager = DatabaseManager(config_manager=config_manager, sync_service=None)
    sync_service: SyncService = SyncService(config_manager=config_manager, db_manager=db_manager)
    db_manager.sync_service = sync_service

    # Instantiate the domain Model and ViewModel.
    model: QuoteModel = QuoteModel(db_manager)
    viewmodel: QuoteViewModel = QuoteViewModel(model, db_manager, sync_service)

    # Expose the backend API to the web view.
    api: PyWebViewAPI = PyWebViewAPI(viewmodel)

    # After config_manager & db_manager exist, update runtime settings from database
    for key in Settings.get_visible_settings():
        val = db_manager.get_setting(key)
        if val is not None:
            setattr(Settings, key, val)

    # Register shutdown handlers.
    register_shutdown_handler(sync_service)

    # Start any required background services (e.g., synchronization).
    try:
        sync_service.start_sync_thread()
    except Exception as e:
        logging.error(f"Error starting sync service: {e}", exc_info=True)
        sys.exit(1)

    # Determine the path to index.html (assumed to be in views/web/)
    current_dir: str = os.path.dirname(os.path.abspath(__file__))
    index_html: str = os.path.join(current_dir, "views", "web", "index.html")

    # Create and display the PyWebView window.
    window = webview.create_window("Quote Generator", url=index_html, js_api=api)
    api._window = window

    # ========== EXPOSE ANY STANDALONE FUNCTIONS HERE ==========
    # Standalone save file dialog for output selection
    window.expose(browse_save_file)

    try:
        webview.start(debug=True)
    except Exception as e:
        logging.error(f"Error starting webview: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
