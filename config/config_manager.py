# config/config_manager.py
# (only four tiny edits marked ★ CHANGED; everything else identical)

from __future__ import annotations
import os, json, logging
from pathlib import Path
from typing import Dict, Any
from config.settings import Settings


class ConfigManager:
    """
    Manages application configuration including server and local database settings.
    Handles environment-specific configurations and connection strings.
    """

    def __init__(self) -> None:
        self.config: Dict[str, Any] = {}
        self.server_config: Dict[str, Any] = {}
        self.setup_logging()
        self.load_config()

    # ------------------------------------------------------------------
    # Logging helpers (unchanged)
    # ------------------------------------------------------------------
    def setup_logging(self) -> None:
        try:
            log_path: Path = self.get_log_path()
            log_file: Path = log_path / "config.log"
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                filename=str(log_file)
            )
            self.logger: logging.Logger = logging.getLogger(__name__)
        except Exception as e:
            print(f"Error during setup_logging in ConfigManager: {e}")
            raise

    # ------------------------------------------------------------------
    # Config loader (unchanged)
    # ------------------------------------------------------------------
    def load_config(self) -> None:
        try:
            server_config_path: Path = (
                Path.home()
                / "Alliance Automation"
                / "Applications Engineering - Documents"
                / "Quote Writeup"
            )
            if server_config_path.exists():
                self.logger.info(f"Server configuration path verified: {server_config_path}")
                server_config_file: Path = server_config_path / "server_config.json"
                if server_config_file.exists():
                    with open(server_config_file, "r", encoding="utf-8") as f:
                        self.server_config = json.load(f)
                    self.logger.info(f"Server configuration loaded from {server_config_file}")
                else:
                    self.logger.warning(f"Server configuration file not found at {server_config_file}; proceeding with defaults.")
            else:
                self.logger.error(f"Server configuration path does not exist: {server_config_path}")
                raise FileNotFoundError(f"Server configuration path not found: {server_config_path}")
        except Exception as e:
            self.logger.error(f"Unexpected error loading configuration: {e}")
            raise

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------
    @staticmethod
    def get_app_data_path() -> Path:
        """Return the current application-data root folder."""
        return Path(Settings.LOCAL_STORAGE["root_path"])             # ★ CHANGED

    @staticmethod
    def get_log_path() -> Path:
        """Return (and create) the log directory."""
        log_path: Path = Path(Settings.LOCAL_STORAGE["log_path"])     # ★ CHANGED
        log_path.mkdir(parents=True, exist_ok=True)
        return log_path

    @staticmethod
    def get_environment() -> str:
        return os.getenv("QUOTE_GENERATOR_ENV", "development")

    # ------------------------------------------------------------------
    # Database config
    # ------------------------------------------------------------------
    def get_database_config(self, database_name: str) -> Dict[str, Any]:
        try:
            server_host: str = Settings.SERVER_CONFIG["host"]
            server_db_path: Path = Path(server_host) / "db" / f"{database_name}.db"
            local_db_path: Path  = Path(Settings.LOCAL_STORAGE["db_path"]) / f"{database_name}.db"  # ★ CHANGED
            return {
                "local_path"      : str(local_db_path),
                "server_path"     : str(server_db_path),
                "pool_size"       : 5,
                "connection_string": "",
            }
        except KeyError as e:
            self.logger.error(f"Missing configuration for database {database_name}: {e}")
            raise

    # ------------------------------------------------------------------
    # Sync, server, storage helpers (minimal change)
    # ------------------------------------------------------------------
    def get_sync_config(self) -> Dict[str, Any]:
        return self.config.get("sync", {
            "sync_interval"      : 300,
            "retry_attempts"     : 3,
            "retry_delay"        : 5,
            "conflict_resolution": "server_wins",
        })

    def get_server_config(self) -> Dict[str, Any]:
        return self.server_config

    def get_local_storage_config(self) -> Dict[str, Any]:
        return {                                                    # ★ CHANGED
            "root_path" : str(Settings.LOCAL_STORAGE["root_path"]),
            "temp_path" : str(Settings.LOCAL_STORAGE["temp_path"]),
            "max_storage_size": self.config.get("local_storage", {}).get("max_size", None),
        }

    # ------------------------------------------------------------------
    # Persistence helpers (unchanged)
    # ------------------------------------------------------------------
    def update_config(self, section: str, key: str, value: Any) -> None:
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.logger.info(f"Configuration updated: [{section}][{key}] = {value}")
        self.save_config()

    def save_config(self) -> None:
        config_file: Path = self.get_app_data_path() / "config.json"
        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
            self.logger.info(f"Configuration saved to {config_file}")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            raise
