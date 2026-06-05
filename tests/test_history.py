"""Tests for the SQLite search history.

Docs: tests/test_history.doc.md
"""

import os
import tempfile

import pytest

from sin_websearch.history import SearchHistory


class TestSearchHistory:
    def test_add_and_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            hist = SearchHistory(db_path=os.path.join(tmp, "hist.db"), max_entries=100)
            hist.add("openai", "success", result_count=10)
            entries = hist.list()
            assert len(entries) == 1
            assert entries[0]["query"] == "openai"
            assert entries[0]["status"] == "success"
            assert entries[0]["result_count"] == 10

    def test_list_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            hist = SearchHistory(db_path=os.path.join(tmp, "hist.db"), max_entries=100)
            for i in range(5):
                hist.add(f"q{i}", "success")
            entries = hist.list(limit=3)
            assert len(entries) == 3

    def test_list_offset(self):
        with tempfile.TemporaryDirectory() as tmp:
            hist = SearchHistory(db_path=os.path.join(tmp, "hist.db"), max_entries=100)
            for i in range(5):
                hist.add(f"q{i}", "success")
            entries = hist.list(limit=2, offset=2)
            assert len(entries) == 2
            assert entries[0]["query"] == "q2"

    def test_list_query_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            hist = SearchHistory(db_path=os.path.join(tmp, "hist.db"), max_entries=100)
            hist.add("openai", "success")
            hist.add("google", "success")
            entries = hist.list(query_filter="open")
            assert len(entries) == 1
            assert entries[0]["query"] == "openai"

    def test_clear(self):
        with tempfile.TemporaryDirectory() as tmp:
            hist = SearchHistory(db_path=os.path.join(tmp, "hist.db"), max_entries=100)
            hist.add("a", "success")
            hist.add("b", "success")
            count = hist.clear()
            assert count == 2
            assert hist.list() == []

    def test_stats(self):
        with tempfile.TemporaryDirectory() as tmp:
            hist = SearchHistory(db_path=os.path.join(tmp, "hist.db"), max_entries=100)
            hist.add("a", "success")
            hist.add("b", "error")
            hist.add("c", "rate_limited")
            hist.add("d", "cached")
            stats = hist.stats()
            assert stats["total"] == 4
            assert stats["success"] == 1
            assert stats["error"] == 1
            assert stats["rate_limited"] == 1
            assert stats["cached"] == 1

    def test_max_entries_pruning(self):
        with tempfile.TemporaryDirectory() as tmp:
            hist = SearchHistory(db_path=os.path.join(tmp, "hist.db"), max_entries=3)
            for i in range(5):
                hist.add(f"q{i}", "success")
            entries = hist.list()
            assert len(entries) == 3
            # Most recent kept
            assert entries[0]["query"] == "q4"
            assert entries[1]["query"] == "q3"
            assert entries[2]["query"] == "q2"

    def test_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, "hist.db")
            hist = SearchHistory(db_path=db_path, max_entries=100)
            hist.add("persist", "success")
            hist2 = SearchHistory(db_path=db_path, max_entries=100)
            entries = hist2.list()
            assert len(entries) == 1
            assert entries[0]["query"] == "persist"
