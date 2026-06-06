"""Tests for the SQLite search cache.

Docs: test_cache.doc.md
"""

import os
import tempfile
import time

import pytest

from sin_websearch.cache import SearchCache


class TestSearchCache:
    def test_cache_hit(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"), ttl=60)
            cache.set("openai", {"results": [1, 2]})
            assert cache.get("openai") == {"results": [1, 2]}

    def test_cache_miss(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"), ttl=60)
            assert cache.get("openai") is None

    def test_cache_expiration(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"), ttl=1)
            cache.set("openai", {"results": [1]})
            time.sleep(1.1)
            assert cache.get("openai") is None

    def test_cache_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"), ttl=60)
            cache.set("openai", {"results": [1]})
            cache.set("openai", {"results": [2]})
            assert cache.get("openai") == {"results": [2]}

    def test_cache_clear(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"), ttl=60)
            cache.set("a", {"r": 1})
            cache.set("b", {"r": 2})
            count = cache.clear()
            assert count == 2
            assert cache.get("a") is None
            assert cache.get("b") is None

    def test_cache_clear_expired(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"), ttl=1)
            cache.set("old", {"r": 1})
            time.sleep(1.1)
            cache.set("new", {"r": 2})
            count = cache.clear_expired()
            assert count == 1
            assert cache.get("old") is None
            assert cache.get("new") == {"r": 2}

    def test_cache_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"), ttl=60)
            assert cache.size() == 0
            cache.set("a", {"r": 1})
            assert cache.size() == 1

    def test_cache_list_queries(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"), ttl=60)
            cache.set("zebra", {"r": 1})
            cache.set("apple", {"r": 2})
            queries = cache.list_queries()
            # Most recent first
            assert queries[0] == "apple"
            assert queries[1] == "zebra"

    def test_cache_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "cache.db")
            cache = SearchCache(db_path=db_path, ttl=60)
            cache.set("persist", {"r": 42})
            # Re-open
            cache2 = SearchCache(db_path=db_path, ttl=60)
            assert cache2.get("persist") == {"r": 42}
