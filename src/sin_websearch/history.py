"""Search history tracking with SQLite persistence.

Docs: src/sin_websearch/history.doc.md
"""

import json
import os
import sqlite3
import time
from typing import Optional

# ── Constants ──────────────────────────────────────
DEFAULT_MAX_ENTRIES = 1000
DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "websearch_history.db"
)


class SearchHistory:
    """Persistent SQLite-backed search history.

    Attributes:
        db_path: Path to the SQLite database file.
        max_entries: Maximum number of entries to retain (default 1000).
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        max_entries: int = DEFAULT_MAX_ENTRIES,
    ):
        self.db_path = os.path.abspath(db_path or DEFAULT_DB_PATH)
        self.max_entries = max_entries
        self._ensure_table()

    def _ensure_table(self) -> None:
        """Create the history table if it does not exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    key_used TEXT,
                    status TEXT NOT NULL,
                    result_count INTEGER,
                    error_message TEXT,
                    created_at REAL NOT NULL
                )
                """
            )

    def add(
        self,
        query: str,
        status: str,
        key_used: Optional[str] = None,
        result_count: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Record a search attempt.

        Args:
            query: The search query string.
            status: One of "success", "error", "rate_limited", "cached".
            key_used: Masked key identifier (e.g., "key_1").
            result_count: Number of results returned.
            error_message: Error details if status != "success".
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO search_history
                (query, key_used, status, result_count, error_message, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    query,
                    key_used,
                    status,
                    result_count,
                    error_message,
                    time.time(),
                ),
            )
            # Prune old entries
            conn.execute(
                """
                DELETE FROM search_history
                WHERE id <= (
                    SELECT id FROM search_history
                    ORDER BY id DESC LIMIT 1 OFFSET ?
                )
                """,
                (self.max_entries,),
            )

    def list(
        self,
        limit: int = 50,
        offset: int = 0,
        query_filter: Optional[str] = None,
    ) -> list[dict]:
        """Return recent history entries.

        Args:
            limit: Max entries to return.
            offset: Pagination offset.
            query_filter: Optional substring filter on query.

        Returns:
            List of dicts with keys: id, query, key_used, status,
            result_count, error_message, created_at.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if query_filter:
                cursor = conn.execute(
                    """
                    SELECT * FROM search_history
                    WHERE query LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                    """,
                    (f"%{query_filter}%", limit, offset),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT * FROM search_history
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                    """,
                    (limit, offset),
                )
            return [dict(row) for row in cursor.fetchall()]

    def clear(self) -> int:
        """Delete all history entries. Returns number of rows deleted."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM search_history")
            return cursor.rowcount

    def stats(self) -> dict:
        """Return aggregated history statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
                    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error,
                    SUM(CASE WHEN status = 'rate_limited' THEN 1 ELSE 0 END) as rate_limited,
                    SUM(CASE WHEN status = 'cached' THEN 1 ELSE 0 END) as cached
                FROM search_history
                """
            )
            row = cursor.fetchone()
            return {
                "total": row[0] or 0,
                "success": row[1] or 0,
                "error": row[2] or 0,
                "rate_limited": row[3] or 0,
                "cached": row[4] or 0,
            }
