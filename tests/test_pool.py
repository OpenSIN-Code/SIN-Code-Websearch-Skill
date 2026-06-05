"""Tests for the SerpAPI key pool.

Docs: tests/test_pool.doc.md
"""

import time
from unittest.mock import patch

import pytest

from sin_websearch.pool import KeyInfo, SerpAPIKeyPool


# ── KeyInfo ──────────────────────────────────────

class TestKeyInfo:
    def test_is_available_default(self):
        ki = KeyInfo("secret", 0)
        assert ki.is_available is True

    def test_is_available_cooldown(self):
        ki = KeyInfo("secret", 0)
        ki.mark_cooldown(seconds=60)
        assert ki.is_available is False

    def test_is_available_after_cooldown_expires(self):
        ki = KeyInfo("secret", 0)
        ki.mark_cooldown(seconds=1)
        time.sleep(1.1)
        assert ki.is_available is True

    def test_is_available_suspended(self):
        ki = KeyInfo("secret", 0)
        ki.mark_suspended()
        assert ki.is_available is False

    def test_reset(self):
        ki = KeyInfo("secret", 0)
        ki.mark_cooldown()
        ki.mark_suspended()
        ki.reset()
        assert ki.is_available is True
        assert ki.cooldown_until == 0.0
        assert ki.suspended is False


# ── SerpAPIKeyPool ──────────────────────────────────────

class TestSerpAPIKeyPool:
    def test_next_key_round_robin(self):
        pool = SerpAPIKeyPool(["k1", "k2", "k3"])
        assert pool.next_key() == "k1"
        assert pool.next_key() == "k2"
        assert pool.next_key() == "k3"
        assert pool.next_key() == "k1"

    def test_next_key_empty_pool(self):
        pool = SerpAPIKeyPool([])
        assert pool.next_key() is None

    def test_next_key_all_cooldown(self):
        pool = SerpAPIKeyPool(["k1", "k2"])
        pool.report_rate_limit("k1")
        pool.report_rate_limit("k2")
        assert pool.next_key() is None

    def test_next_key_one_available(self):
        pool = SerpAPIKeyPool(["k1", "k2"])
        pool.report_rate_limit("k1")
        assert pool.next_key() == "k2"

    def test_report_rate_limit(self):
        pool = SerpAPIKeyPool(["k1"])
        pool.report_rate_limit("k1")
        assert pool.keys[0].is_available is False

    def test_report_suspended(self):
        pool = SerpAPIKeyPool(["k1"])
        pool.report_suspended("k1")
        assert pool.keys[0].is_available is False
        assert pool.keys[0].suspended is True

    def test_reset_key(self):
        pool = SerpAPIKeyPool(["k1"])
        pool.report_rate_limit("k1")
        pool.reset_key("k1")
        assert pool.keys[0].is_available is True

    def test_reset_all(self):
        pool = SerpAPIKeyPool(["k1", "k2"])
        pool.report_rate_limit("k1")
        pool.report_suspended("k2")
        pool.reset_all()
        assert all(k.is_available for k in pool.keys)

    def test_status(self):
        pool = SerpAPIKeyPool(["k1", "k2"])
        pool.report_rate_limit("k1")
        pool.report_suspended("k2")
        status = pool.status()
        assert status["total_keys"] == 2
        assert status["available_keys"] == 0
        assert status["cooldown_keys"] == 1
        assert status["suspended_keys"] == 1

    def test_use_count_increments(self):
        pool = SerpAPIKeyPool(["k1"])
        pool.next_key()
        assert pool.keys[0].use_count == 1

    def test_load_from_infisical_success(self):
        pool = SerpAPIKeyPool()
        with patch("sin_websearch.pool._infisical_get", side_effect=["val1", "val2", None, None]):
            loaded = pool.load_from_infisical(key_names=["A", "B", "C", "D"])
        assert loaded == 2
        assert len(pool.keys) == 2

    def test_load_from_infisical_none(self):
        pool = SerpAPIKeyPool()
        with patch("sin_websearch.pool._infisical_get", return_value=None):
            loaded = pool.load_from_infisical(key_names=["A"])
        assert loaded == 0

    def test_next_key_reactivates_after_cooldown(self):
        pool = SerpAPIKeyPool(["k1"])
        pool.report_rate_limit("k1")
        assert pool.next_key() is None
        time.sleep(1.1)
        pool.keys[0].mark_cooldown(seconds=1)
        time.sleep(1.1)
        assert pool.next_key() == "k1"

    def test_status_key_masked(self):
        pool = SerpAPIKeyPool(["abcdef123456"])
        status = pool.status()
        assert status["keys"][0]["masked"].startswith("abcd")
        assert status["keys"][0]["masked"].endswith("3456")
