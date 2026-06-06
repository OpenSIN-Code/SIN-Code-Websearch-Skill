"""SQLite-based cache for websearch results.

Docs: cache.doc.md
"""

import json
import os
import sqlite3
import time
from typing import Optional

# ── Constants ──────────────────────────────────────
DEFAULT_TTL_SECONDS = 3600  # 1 hour
DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "websearch_cache.db")


class SearchCache:
    """Persistent SQLite cache for search results.

    Attributes:
        db_path: Path to the SQLite database file.
        ttl: Time-to-live in seconds (default 1 hour).
    """

    def __init__(self, db_path: Optional[str] = None, ttl: int = DEFAULT_TTL_SECONDS):
        self.db_path = os.path.abspath(db_path or DEFAULT_DB_PATH)
        self.ttl = ttl
        self._ensure_table()

    def _ensure_table(self) -> None:
        """Create the cache table if it does not exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS search_cache (
                    query TEXT PRIMARY KEY,
                    result TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )

    def get(self, query: str) -> Optional[dict]:
        """Retrieve a cached result if it is not expired.

        Args:
            query: Normalized search query string.

        Returns:
            The cached result dict, or None if miss/expired.
        """
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT result, created_at FROM search_cache WHERE query = ?",
                (query,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            result_text, created_at = row
            if now - created_at > self.ttl:
                # Expired: delete
                conn.execute("DELETE FROM search_cache WHERE query = ?", (query,))
                return None
            return json.loads(result_text)

    def set(self, query: str, result: dict) -> None:
        """Store a result in the cache.

        Args:
            query: Normalized search query string.
            result: JSON-serializable dict.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO search_cache (query, result, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(query) DO UPDATE SET
                    result=excluded.result,
                    created_at=excluded.created_at
                """,
                (query, json.dumps(result), time.time()),
            )

    def clear(self) -> int:
        """Delete all cached entries. Returns number of rows deleted."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM search_cache")
            return cursor.rowcount

    def clear_expired(self) -> int:
        """Delete expired entries. Returns number of rows deleted."""
        cutoff = time.time() - self.ttl
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM search_cache WHERE created_at < ?", (cutoff,)
            )
            return cursor.rowcount

    def size(self) -> int:
        """Return the number of entries in the cache."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM search_cache")
            return cursor.fetchone()[0] or 0

    def list_queries(self, limit: int = 100) -> list[str]:
        """Return the most recently cached queries."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT query FROM search_cache ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
            return [row[0] for row in cursor.fetchall()]
