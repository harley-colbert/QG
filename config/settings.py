# config/settings.py
# File Hierarchy: config/settings.py
# This module defines global constants and default settings for the Quote Generator application.
# It includes file paths for local storage, logging configurations, database settings, UI dimensions, and sync parameters.
# The methods provided ensure that the required directories are created and that configuration values are accessible.
# This file adheres to MVVM architecture principles, uses Python 3.12.9 type annotations, and includes robust logging and error handling.

from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, Any, List

class Settings:
    """Application settings including database, storage, and UI configurations."""

    # Base application paths
    appPath: Path = Path.home() / "Alliance Automation" / "Applications Engineering - Documents" / "Quote Generator"
    appPathBack: Path = appPath / "backup"

    # Application Storage Paths
    LOCAL_STORAGE: Dict[str, Any] = {
        "root_path"  : appPathBack,
        "temp_path"  : appPathBack / "temp",
        "backup_path": appPathBack,
        "log_path"   : appPathBack / "logs",
        "db_path"    : appPathBack / "db",
        # 'max_size': 1024 * 1024 * 100  # Optional: 100MB limit
    }
    print("[LOCAL_STORAGE]", LOCAL_STORAGE)

    # ----------------------------------------------------------------------
    # NEW - user-configurable folder shortcuts
    # ----------------------------------------------------------------------
    DB_FOLDER_PATH : Path = LOCAL_STORAGE["db_path"]
    LOG_FOLDER_PATH: Path = LOCAL_STORAGE["log_path"]

    # Server Configuration
    SERVER_CONFIG: Dict[str, Any] = {
        "host": appPathBack,  # Network path to server
        "backup_path": appPathBack,
        "timeout": 30,        # Seconds
        "retry_attempts": 3
    }

    # Shelve Files mapping (for lightweight data storage)
    SHELVE_FILES: Dict[str, Dict[str, str]] = {
        "contacts": {
            "local": str(LOCAL_STORAGE["db_path"] / "contacts"),
            "server": str(SERVER_CONFIG["host"] / "contacts"),
            "backup": str(SERVER_CONFIG["backup_path"] / "contacts")
        }
    }

    # UI Settings
    ENTRY_WIDTH: int = 50
    PROJECT_RISKS_HEIGHT: int = 5
    SYSTEM_DESCRIPTION_HEIGHT: int = 10
    OPTION_DESCRIPTION_HEIGHT: int = 7

    # Template Settings
    TEMPLATE_FILENAME: str = ""
    CONTACTS_DB_FILENAME: str = "contacts.db"

    # Settings Visibility
    BROWSE_SETTINGS : List[str] = ["TEMPLATE_FILENAME", "DB_FOLDER_PATH", "LOG_FOLDER_PATH"]
    VISIBLE_SETTINGS: List[str] = ["TEMPLATE_FILENAME", "DB_FOLDER_PATH", "LOG_FOLDER_PATH"]

    # Database Settings
    DATABASES: Dict[str, Dict[str, Any]] = {
        "contacts": {
            "filename": "db/contacts.db",
            "pool_size": 5,
            "timeout": 30,
            "backup_count": 5
        },
        "settings": {
            "filename": "db/settings.db",
            "pool_size": 3,
            "timeout": 30,
            "backup_count": 3
        },
        "quotes": {
            "filename": "db/quotes.db",
            "pool_size": 5,
            "timeout": 30,
            "backup_count": 5
        }
    }

    # Sync Configuration
    SYNC_CONFIG: Dict[str, Any] = {
        "interval": 300,               # 5 minutes
        "conflict_resolution": "server_wins",
        "retry_attempts": 3,
        "retry_delay": 5,
        "auto_sync_threshold": 50
    }

    # Logging Configuration
    LOGGING: Dict[str, Any] = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        # "max_size": 1024 * 1024,    # Optional: 1MB per log file
        "backup_count": 5
    }

    @classmethod
    def initialize_paths(cls) -> None:
        """
        Ensures that all required directories exist by creating them if necessary.
        Directories include root, temp, backup, log, and db paths.
        """
        try:
            for key in ["root_path", "temp_path", "backup_path", "log_path", "db_path"]:
                path: Path = Path(cls.LOCAL_STORAGE[key])
                path.mkdir(parents=True, exist_ok=True)
                print("Path created/verified:", path)
        except Exception as e:
            raise Exception(f"Failed to initialize paths: {e}")

    @classmethod
    def initialize_defaults(cls) -> None:
        """
        Initializes default settings if they have not been explicitly set.
        For example, sets TEMPLATE_FILENAME to a default value if empty.
        """
        if not cls.TEMPLATE_FILENAME:
            cls.TEMPLATE_FILENAME = "default_template.docx"

    @classmethod
    def get_database_path(cls, database_name: str) -> Path:
        """
        Constructs and returns the local database file path for a given database.

        Args:
            database_name (str): The name of the database (e.g., 'contacts', 'settings', 'quotes').

        Returns:
            Path: The path to the local database file.
        """
        return Path(cls.LOCAL_STORAGE["db_path"]) / f"{database_name}.db"

    @classmethod
    def get_server_database_path(cls, database_name: str) -> Path:
        """
        Constructs and returns the server database file path for a given database.

        Args:
            database_name (str): The name of the database.

        Returns:
            Path: The path to the server database file.
        """
        return Path(cls.SERVER_CONFIG["host"]) / "db" / f"{database_name}.db"

    @classmethod
    def get_database_config(cls, database_name: str) -> dict:
        """
        Returns the complete configuration for the specified database, including
        local and server paths as well as connection parameters.

        Args:
            database_name (str): The database name.

        Returns:
            dict: A dictionary containing database configuration settings.
        """
        return {
            "local_path": str(Path(cls.LOCAL_STORAGE["db_path"]) / f"{database_name}.db"),
            "server_path": str(Path(cls.SERVER_CONFIG["host"]) / "db" / f"{database_name}.db"),
            "pool_size": cls.DATABASES[database_name].get("pool_size", 5),
            "timeout": cls.DATABASES[database_name].get("timeout", 30),
            "backup_count": cls.DATABASES[database_name].get("backup_count", 5),
        }

    @classmethod
    def get_log_path(cls) -> Path:
        """Returns the path where log files are stored."""
        return Path(cls.LOCAL_STORAGE["log_path"])

    @classmethod
    def get_temp_path(cls) -> Path:
        """Returns the path for temporary files."""
        return Path(cls.LOCAL_STORAGE["temp_path"])

    @classmethod
    def get_backup_path(cls) -> Path:
        """Returns the path for backup files."""
        return Path(cls.LOCAL_STORAGE["backup_path"])

    @classmethod
    def should_auto_sync(cls, change_count: int) -> bool:
        threshold: int = cls.SYNC_CONFIG.get("auto_sync_threshold", 50)
        return change_count >= threshold

    @classmethod
    def get_sync_interval(cls) -> int:
        return cls.SYNC_CONFIG.get("interval", 300)

    @classmethod
    def get_visible_settings(cls) -> List[str]:
        return cls.VISIBLE_SETTINGS.copy()

    # ----------------------------------------------------------------------
    # NEW – single helper to move all runtime-generated files
    # ----------------------------------------------------------------------
    @classmethod
    def update_storage_root(cls, new_root: str) -> None:
        """
        Update every LOCAL_STORAGE folder to live under *new_root*,
        then recreate the directory tree.
        """
        root = Path(new_root).expanduser().resolve()
        cls.LOCAL_STORAGE["root_path"]   = root
        cls.LOCAL_STORAGE["temp_path"]   = root / "temp"
        cls.LOCAL_STORAGE["backup_path"] = root
        cls.LOCAL_STORAGE["log_path"]    = root / "logs"
        cls.LOCAL_STORAGE["db_path"]     = root / "db"

        cls.DB_FOLDER_PATH  = cls.LOCAL_STORAGE["db_path"]
        cls.LOG_FOLDER_PATH = cls.LOCAL_STORAGE["log_path"]

        cls.initialize_paths()
