# File Hierarchy: services/connection_pool.py
# Description: This module provides an advanced connection pool for SQLite databases.
# It uses the "filelock" library to manage distributed file locks on the database file,
# ensuring that locks are acquired and released properly even in error conditions.
# The implementation follows MVVM principles, uses Python 3.12.9 with full type annotations,
# and includes comprehensive logging and error handling for production readiness.

from __future__ import annotations
import sqlite3
import logging
import time
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
import os
import socket
from typing import Optional, List
from filelock import FileLock, Timeout

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DatabaseConnection:
    """
    Enhanced database connection wrapper with metadata and thread-safe locking.

    Attributes:
        connection (sqlite3.Connection): The SQLite connection instance.
        server_path (Path): The path to the database file.
        created_at (datetime): Timestamp when the connection was created.
        last_used (datetime): Timestamp when the connection was last used.
        transaction_level (int): Current transaction depth.
        lock (threading.RLock): Reentrant lock for thread safety.
        in_use (bool): Flag indicating if the connection is in use.
    """
    def __init__(self, connection: sqlite3.Connection, server_path: Path) -> None:
        self.connection: sqlite3.Connection = connection
        self.server_path: Path = server_path
        self.created_at: datetime = datetime.now()
        self.last_used: datetime = datetime.now()
        self.transaction_level: int = 0
        self.lock: threading.RLock = threading.RLock()
        self.in_use: bool = False

class ConnectionPool:
    """
    Manages a pool of DatabaseConnection objects for an SQLite database.
    Provides thread-safe connection acquisition and release using file-based locking
    via the filelock library.
    """
    def __init__(self, server_path: str, max_connections: int = 20, logger_obj: Optional[logging.Logger] = None) -> None:
        self.server_path: Path = Path(server_path)
        self.max_connections: int = max_connections
        self.connections: List[DatabaseConnection] = []
        self.lock: threading.Lock = threading.Lock()
        self.connection_semaphore: threading.BoundedSemaphore = threading.BoundedSemaphore(max_connections)
        self.logger: logging.Logger = logger_obj if logger_obj is not None else logger

    def _acquire_server_lock(self, timeout: int = 30) -> FileLock:
        """
        Acquire a file lock using the filelock library.

        Args:
            timeout (int): Maximum time in seconds to wait for the lock.

        Returns:
            FileLock: An acquired FileLock object.

        Raises:
            TimeoutError: If the lock cannot be acquired within the timeout period.
        """
        lock_file: str = f"{self.server_path}.lock"
        file_lock: FileLock = FileLock(lock_file, timeout=timeout)
        try:
            file_lock.acquire()
            self.logger.info(f"Acquired lock on {self.server_path} using filelock.")
            return file_lock
        except Timeout:
            self.logger.error(f"Could not acquire lock for {self.server_path} within {timeout} seconds.")
            raise TimeoutError(f"Could not acquire lock for {self.server_path} within {timeout} seconds.")

    def _create_connection(self) -> DatabaseConnection:
        """
        Create a new DatabaseConnection with optimized settings, protecting the critical section
        with a file lock acquired via the filelock library.

        Returns:
            DatabaseConnection: A newly created and configured database connection.

        Raises:
            Exception: Propagates any errors encountered during connection creation.
        """
        file_lock: Optional[FileLock] = None
        try:
            file_lock = self._acquire_server_lock(timeout=30)
            connection: sqlite3.Connection = sqlite3.connect(
                str(self.server_path),
                timeout=30,
                isolation_level=None,
                uri=True,
                check_same_thread=False
            )
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.executescript("""
                PRAGMA journal_mode=WAL;
                PRAGMA synchronous=NORMAL;
                PRAGMA cache_size=-2000;
                PRAGMA temp_store=MEMORY;
                PRAGMA mmap_size=268435456;
                PRAGMA busy_timeout=30000;
            """)
            db_connection = DatabaseConnection(connection, self.server_path)
            db_connection.in_use = True
            self.logger.info(f"Created new database connection for {self.server_path}.")
            return db_connection
        except Exception as e:
            self.logger.error("Error creating database connection.", exc_info=True)
            raise
        finally:
            if file_lock:
                file_lock.release()
                self.logger.info(f"Released lock on {self.server_path} after connection creation.")

    def get_connection(self) -> sqlite3.Connection:
        """
        Acquire an available connection from the pool.

        Returns:
            sqlite3.Connection: The underlying SQLite connection instance.

        Raises:
            Exception: If no connection is available within the semaphore timeout.
        """
        if not self.connection_semaphore.acquire(timeout=5):
            raise Exception("Timeout acquiring a connection from the pool.")
        with self.lock:
            for conn in self.connections:
                if not conn.in_use:
                    conn.in_use = True
                    conn.last_used = datetime.now()
                    self.logger.info("Reusing existing connection.")
                    return conn.connection
            if len(self.connections) < self.max_connections:
                new_conn: DatabaseConnection = self._create_connection()
                self.connections.append(new_conn)
                return new_conn.connection
        self.connection_semaphore.release()
        raise Exception("No available connections in the pool.")

    def release_connection(self, connection: sqlite3.Connection) -> None:
        """
        Release a previously acquired connection back to the pool.

        Args:
            connection (sqlite3.Connection): The connection to release.
        """
        with self.lock:
            for conn in self.connections:
                if conn.connection == connection:
                    conn.in_use = False
                    conn.last_used = datetime.now()
                    self.connection_semaphore.release()
                    self.logger.info("Connection released back to the pool.")
                    return
        self.logger.warning("Attempted to release a connection not in the pool.")
