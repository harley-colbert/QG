# File: services/database_manager.py
# Description: Manages SQLite databases for the Quote Generator application,
# ensuring files and schemas exist, providing connection pooling, and handling
# robust initialization and cleanup.

import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Generator
from contextlib import contextmanager
import os
import socket
import threading
import time
import psutil
import msvcrt

from services.connection_pool import ConnectionPool

# Module‑level logger
logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DatabaseManager:
    """
    DatabaseManager handles all database operations including creation, schema initialization,
    connection pooling, synchronization support, and cleanup routines.
    """

    def __init__(self, config_manager: Any, sync_service: Optional[Any]) -> None:
        self.config_manager: Any = config_manager
        self.sync_service: Optional[Any] = sync_service
        self.connection_pools: Dict[str, ConnectionPool] = {}
        self.logger: logging.Logger = logger
        self._connection_lock: threading.Lock = threading.Lock()
        self.initialize_databases()

    def initialize_databases(self) -> None:
        """
        Ensure that all configured databases exist and have their schemas initialized.
        """
        try:
            for db_name in ["contacts", "settings", "quotes"]:
                db_config: Dict[str, Any] = self.config_manager.get_database_config(db_name)
                local_db_path: Path = Path(db_config["local_path"])
                # Ensure directory exists
                local_db_path.parent.mkdir(parents=True, exist_ok=True)
                # Create file if missing
                if not local_db_path.exists():
                    self.logger.info(f"Database file {local_db_path} not found. Creating new database.")
                    conn = sqlite3.connect(str(local_db_path))
                    conn.close()
                # Set up connection pool
                pool: ConnectionPool = ConnectionPool(
                    server_path=str(local_db_path),
                    max_connections=db_config.get("pool_size", 5)
                )
                self.connection_pools[db_name] = pool
                # Initialize schema for this database
                self._initialize_schema(db_name)
            self.logger.info("Databases initialized successfully.")
        except Exception as e:
            self.logger.error("Error initializing databases.", exc_info=True)
            raise

    def _initialize_schema(self, db_name: str) -> None:
        """
        Initialize the database schema for the specified database.
        """
        try:
            with self.get_connection(db_name) as conn:
                if db_name == "contacts":
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS contacts (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            email TEXT NOT NULL,
                            title TEXT,
                            phone TEXT
                        );
                    """)
                elif db_name == "settings":
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS settings (
                            key TEXT PRIMARY KEY,
                            value TEXT
                        );
                    """)
                elif db_name == "quotes":
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS quotes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            quote_number TEXT,
                            customer_name TEXT,
                            created_at TEXT,
                            data TEXT
                        );
                    """)
                conn.commit()
                self.logger.info(f"Schema initialized for database: {db_name}")
        except Exception as e:
            self.logger.error(f"Error initializing schema for {db_name}: {e}", exc_info=True)
            raise

    def get_raw_contacts_connection(self) -> sqlite3.Connection:
        """
        Return a direct, un-pooled connection to the contacts database.
        """
        db_conf = self.config_manager.get_database_config("contacts")
        db_path = Path(db_conf["local_path"])
        return sqlite3.connect(str(db_path))

    @contextmanager
    def get_connection(self, db_name: str) -> Generator[sqlite3.Connection, None, None]:
        """
        Provide a context-managed connection from the pool for the specified database.
        """
        if db_name not in self.connection_pools:
            raise ValueError(f"Unknown database: {db_name}")
        pool: ConnectionPool = self.connection_pools[db_name]
        connection: sqlite3.Connection = pool.get_connection()
        try:
            yield connection
        except Exception as e:
            try:
                connection.rollback()
            except Exception:
                pass
            self.logger.error(f"Error during connection operation for {db_name}: {e}", exc_info=True)
            raise
        finally:
            try:
                pool.release_connection(connection)
            except Exception as e:
                self.logger.error(f"Error releasing connection for {db_name}: {e}", exc_info=True)

    def force_close_database_handles(self, db_name: str) -> bool:
        """
        Force close any open file handles to the specified database.
        """
        try:
            db_conf: Dict[str, Any] = self.config_manager.get_database_config(db_name)
            db_path: str = str(Path(db_conf["local_path"]).resolve())
            self.logger.info(f"Attempting to force close handles for database: {db_name}")
            handle = msvcrt.open_osfhandle(os.open(db_path, os.O_RDWR), 0)
            msvcrt.locking(handle, msvcrt.LK_NBLCK, 1)
            msvcrt.locking(handle, msvcrt.LK_UNLCK, 1)
            os.close(handle)
            self.logger.info(f"Successfully forced close handles for {db_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to force close handles for {db_name}: {e}", exc_info=True)
            return False

    def wait_for_handles_close(self, db_name: str, timeout: int = 30) -> bool:
        """
        Wait until all file handles to the database are released.
        """
        start_time: float = time.time()
        while time.time() - start_time < timeout:
            if not self._are_handles_open(db_name):
                return True
            time.sleep(0.5)
        self.logger.error(f"Timeout waiting for database {db_name} handles to close.")
        return False

    def _are_handles_open(self, db_name: str) -> bool:
        """
        Check if there are open file handles to the database.
        """
        try:
            db_conf: Dict[str, Any] = self.config_manager.get_database_config(db_name)
            db_path: str = str(Path(db_conf["local_path"]).resolve())
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    for open_file in proc.open_files():
                        if open_file.path == db_path:
                            return True
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
            return False
        except Exception as e:
            self.logger.error(f"Error checking open handles for {db_name}: {e}", exc_info=True)
            return True

    def cleanup_temporary_files(self, db_name: str) -> bool:
        """
        Clean up temporary files related to the specified database.
        """
        try:
            db_conf: Dict[str, Any] = self.config_manager.get_database_config(db_name)
            local_db_path: Path = Path(db_conf["local_path"])
            patterns = ["*.tmp", "*.bak", "*.old"]
            for pattern in patterns:
                for temp_file in local_db_path.parent.glob(f"{local_db_path.stem}{pattern}"):
                    try:
                        temp_file.unlink()
                        self.logger.info(f"Deleted temporary file: {temp_file}")
                    except Exception as inner_e:
                        self.logger.warning(f"Failed to delete temporary file {temp_file}: {inner_e}", exc_info=True)
            return True
        except Exception as e:
            self.logger.error(f"Error cleaning up temporary files for {db_name}: {e}", exc_info=True)
            return False

    def compact_database(self, db_name: str) -> bool:
        """
        Compact the database using VACUUM to reclaim space.
        """
        try:
            with self.get_connection(db_name) as conn:
                conn.execute("VACUUM")
                cursor = conn.execute("PRAGMA integrity_check")
                result = cursor.fetchone()[0]
                if result != "ok":
                    raise Exception("Integrity check failed after compaction.")
                self.logger.info(f"Database {db_name} compacted successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Error compacting database {db_name}: {e}", exc_info=True)
            return False

    def close_all_connections(self) -> None:
        """
        Close all connections in every connection pool.
        """
        with self._connection_lock:
            for db_name, pool in self.connection_pools.items():
                for conn_wrapper in pool.connections:
                    try:
                        conn_wrapper.connection.close()
                        self.logger.info(f"Closed connection for database {db_name}.")
                    except Exception as e:
                        self.logger.error(f"Error closing connection for {db_name}: {e}", exc_info=True)
                pool.connections.clear()
            self.logger.info("All database connections have been closed.")

    def get_contact_by_id(self, contact_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch a contact record by its database ID.
        Returns a dict with keys: id, name, email, title, phone (or None if not found).
        """
        try:
            with self.get_connection("contacts") as conn:
                row = conn.execute(
                    "SELECT id, name, email, title, phone FROM contacts WHERE id = ?",
                    (contact_id,)
                ).fetchone()
                if row:
                    return {
                        "id": row[0],
                        "name": row[1],
                        "email": row[2],
                        "title": row[3],
                        "phone": row[4],
                    }
                return None
        except Exception as e:
            self.logger.error(f"Error fetching contact by ID {contact_id}", exc_info=True)
            return None

    def add_contact(self, name: str, title: str, phone: str, email: str) -> int:
        """
        Add a new contact. Returns the new contact ID.
        """
        try:
            with self.get_connection("contacts") as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO contacts (name, title, phone, email)
                    VALUES (?, ?, ?, ?)
                    """,
                    (name, title, phone, email)
                )
                conn.commit()
                contact_id = cursor.lastrowid
            self.logger.info(f"Added new contact ID {contact_id}.")
            return contact_id
        except Exception as e:
            self.logger.error(f"Error adding contact: {e}", exc_info=True)
            return -1

    def update_contact(self, contact_id: int, name: str, title: str, phone: str, email: str) -> bool:
        """
        Update an existing contact by ID.
        """
        try:
            with self.get_connection("contacts") as conn:
                conn.execute(
                    """
                    UPDATE contacts
                    SET name = ?, title = ?, phone = ?, email = ?
                    WHERE id = ?
                    """,
                    (name, title, phone, email, contact_id)
                )
                conn.commit()
            self.logger.info(f"Updated contact ID {contact_id} successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Error updating contact {contact_id}: {e}", exc_info=True)
            return False

    def get_setting(self, key: str) -> Optional[str]:
        """
        Read a single setting from the settings table.
        """
        try:
            with self.get_connection("settings") as conn:
                row = conn.execute(
                    "SELECT value FROM settings WHERE key = ?",
                    (key,)
                ).fetchone()
                return row[0] if row else None
        except Exception as e:
            self.logger.error(f"Error reading setting {key}", exc_info=True)
            return None

    def set_setting(self, key: str, value: str) -> None:
        """
        Insert or update a setting in the settings table.
        """
        try:
            with self.get_connection("settings") as conn:
                conn.execute("""
                    INSERT INTO settings (key, value) VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value=excluded.value;
                """, (key, value))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error writing setting {key}", exc_info=True)
            raise
