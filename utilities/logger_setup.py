# utilities/logger_setup.py
# File Hierarchy: utilities/logger_setup.py
# This module centralizes logging configuration for the Quote Generator application.
# It sets up both a console handler and a rotating file handler with robust formatting,
# error handling, and full type annotations. This module is part of Milestone 1 (Foundation Setup)
# and is designed to support the MVVM architecture by providing a consistent logging mechanism
# that all modules can utilize.

from __future__ import annotations
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any
from config.settings import Settings

def setup_logging() -> None:
    """
    Configure the global logging for the application.

    This function sets up logging with both console and rotating file handlers.
    The log file is stored in the directory specified by Settings.LOCAL_STORAGE['log_path'].
    Log formatting, level, and file size limits are read from Settings.LOGGING.
    """
    try:
        # Ensure the log directory exists
        log_dir: Path = Path(Settings.LOCAL_STORAGE["log_path"])
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file: Path = log_dir / "application.log"
        
        # Retrieve logging configuration from Settings
        log_level_str: str = Settings.LOGGING.get("level", "INFO").upper()
        log_level: int = getattr(logging, log_level_str, logging.INFO)
        log_format: str = Settings.LOGGING.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        max_bytes: int = Settings.LOGGING.get("max_size", 1024 * 1024)  # Default 1MB if not set
        backup_count: int = Settings.LOGGING.get("backup_count", 5)
        
        formatter: logging.Formatter = logging.Formatter(log_format)
        
        # Set up a rotating file handler
        file_handler: RotatingFileHandler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        
        # Set up a console (stream) handler
        console_handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        
        # Configure the root logger
        root_logger: logging.Logger = logging.getLogger()
        root_logger.setLevel(log_level)
        # Clear any existing handlers
        if root_logger.hasHandlers():
            root_logger.handlers.clear()
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        root_logger.info("Global logging configured successfully.")
        
    except Exception as e:
        print(f"Failed to configure logging: {e}")
        raise
        
def cleanup_logging() -> None:
    """Clean up and close all logging handlers."""
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)
