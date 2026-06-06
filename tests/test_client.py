"""Tests for the SerpAPI client.

Docs: test_client.doc.md
"""

import json
import os
import tempfile

import pytest
import responses

from sin_websearch.cache import SearchCache
from sin_websearch.client import SerpAPIClient, _extract_results
from sin_websearch.history import SearchHistory
from sin_websearch.pool import SerpAPIKeyPool


# ── _extract_results ──────────────────────────────────────

class TestExtractResults:
    def test_organic_results(self):
        data = {
            "organic_results": [
                {"title": "T1", "link": "L1", "snippet": "S1"},
                {"title": "T2", "link": "L2", "snippet": "S2"},
            ]
        }
        results = _extract_results(data)
        assert len(results) == 2
        assert results[0]["title"] == "T1"

    def test_fallback_results(self):
        data = {
            "results": [
                {"title": "T1", "link": "L1"},
            ]
        }
        results = _extract_results(data)
        assert len(results) == 1

    def test_empty(self):
        assert _extract_results({}) == []


# ── SerpAPIClient ──────────────────────────────────────

class TestSerpAPIClient:
    @responses.activate
    def test_search_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)

            responses.add(
                responses.GET,
                "https://serpapi.com/search",
                json={"organic_results": [{"title": "R1", "link": "L1", "snippet": "S1"}]},
                status=200,
            )

            result = client.search("openai")
            assert result["success"] is True
            assert result["source"] == "api"
            assert len(result["results"]) == 1
            assert result["results"][0]["title"] == "R1"

    @responses.activate
    def test_search_cache_hit(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)

            # Pre-populate cache
            cache.set("openai", {"results": [{"title": "Cached", "link": "L", "snippet": "S"}]})

            result = client.search("openai")
            assert result["success"] is True
            assert result["source"] == "cache"
            assert result["results"][0]["title"] == "Cached"

    @responses.activate
    def test_search_429_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1", "key2"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)

            # First key returns 429
            responses.add(
                responses.GET,
                "https://serpapi.com/search",
                json={"error": "rate limited"},
                status=429,
            )
            # Second key returns 200
            responses.add(
                responses.GET,
                "https://serpapi.com/search",
                json={"organic_results": [{"title": "OK", "link": "L", "snippet": "S"}]},
                status=200,
            )

            result = client.search("openai")
            assert result["success"] is True
            assert result["source"] == "api"
            assert result["results"][0]["title"] == "OK"
            assert pool.keys[0].is_available is False  # key1 in cooldown

    @responses.activate
    def test_search_401_suspension(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1", "key2"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)

            responses.add(
                responses.GET,
                "https://serpapi.com/search",
                json={"error": "invalid"},
                status=401,
            )
            responses.add(
                responses.GET,
                "https://serpapi.com/search",
                json={"organic_results": [{"title": "OK", "link": "L", "snippet": "S"}]},
                status=200,
            )

            result = client.search("openai")
            assert result["success"] is True
            assert pool.keys[0].suspended is True

    @responses.activate
    def test_search_all_keys_cooldown(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)

            responses.add(
                responses.GET,
                "https://serpapi.com/search",
                json={"error": "rate limited"},
                status=429,
            )

            result = client.search("openai")
            assert result["success"] is False
            assert "All keys in cooldown" in result["error"]

    @responses.activate
    def test_search_500_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)

            responses.add(
                responses.GET,
                "https://serpapi.com/search",
                json={"error": "server error"},
                status=500,
            )

            result = client.search("openai")
            assert result["success"] is False
            assert "500" in result["error"]

    @responses.activate
    def test_search_network_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)

            # No mock registered inside @responses.activate → ConnectionError
            result = client.search("openai")
            assert result["success"] is False
            assert "Network error" in result["error"]

    def test_search_records_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)

            with responses.RequestsMock() as rsps:
                rsps.add(
                    responses.GET,
                    "https://serpapi.com/search",
                    json={"organic_results": [{"title": "R", "link": "L", "snippet": "S"}]},
                    status=200,
                )
                client.search("openai")

            entries = history.list()
            assert len(entries) == 1
            assert entries[0]["status"] == "success"
            assert entries[0]["query"] == "openai"

    def test_rate_limit_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1", "key2"])
            pool.report_rate_limit("key1")
            client = SerpAPIClient(pool=pool, cache=cache, history=history)
            status = client.rate_limit_status()
            assert status["total_keys"] == 2
            assert status["available_keys"] == 1

    def test_search_with_params(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)

            with responses.RequestsMock() as rsps:
                rsps.add(
                    responses.GET,
                    "https://serpapi.com/search",
                    json={"organic_results": [{"title": "R", "link": "L", "snippet": "S"}]},
                    status=200,
                )
                result = client.search(
                    "openai",
                    engine="bing",
                    num_results=5,
                    location="Berlin",
                    language="de",
                )
                assert result["success"] is True
                # Verify request params were sent
                req = rsps.calls[0].request
                assert "engine=bing" in req.url
                assert "num=5" in req.url
                assert "location=Berlin" in req.url
                assert "hl=de" in req.url

    @responses.activate
    def test_search_empty_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)

            responses.add(
                responses.GET,
                "https://serpapi.com/search",
                json={"organic_results": []},
                status=200,
            )

            result = client.search("openai")
            assert result["success"] is True
            assert result["results"] == []
