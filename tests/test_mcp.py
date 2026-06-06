"""Tests for the FastMCP server.

Docs: test_mcp.doc.md
"""

import asyncio
import json
import os
import tempfile
from unittest.mock import patch

import pytest
import responses

from mcp_server import _get_client, mcp
from sin_websearch.cache import SearchCache
from sin_websearch.client import SerpAPIClient
from sin_websearch.pool import SerpAPIKeyPool


# ── Tool tests ──────────────────────────────────────

class TestMCPTools:
    @patch("mcp_server._get_client")
    async def test_websearch_search_tool(self, mock_get_client):
        with tempfile.TemporaryDirectory() as tmp:
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=SearchCache(db_path=os.path.join(tmp, "cache.db")))
            mock_get_client.return_value = client

            with responses.RequestsMock() as rsps:
                rsps.add(
                    responses.GET,
                    "https://serpapi.com/search",
                    json={"organic_results": [{"title": "R", "link": "L", "snippet": "S"}]},
                    status=200,
                )
                result = await mcp.call_tool("websearch_search", {"query": "openai"})
                data = json.loads(result.content[0].text)
                assert data["success"] is True
                assert data["source"] == "api"

    @patch("mcp_server._get_client")
    async def test_websearch_search_tool_cache(self, mock_get_client):
        with tempfile.TemporaryDirectory() as tmp:
            from sin_websearch.cache import SearchCache
            from sin_websearch.history import SearchHistory

            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)
            mock_get_client.return_value = client

            cache.set("openai", {"results": [{"title": "Cached", "link": "L", "snippet": "S"}]})
            result = await mcp.call_tool("websearch_search", {"query": "openai"})
            data = json.loads(result.content[0].text)
            assert data["success"] is True
            assert data["source"] == "cache"

    @patch("mcp_server._get_client")
    async def test_websearch_status_tool(self, mock_get_client):
        with tempfile.TemporaryDirectory() as tmp:
            pool = SerpAPIKeyPool(["k1", "k2"])
            pool.report_rate_limit("k1")
            client = SerpAPIClient(pool=pool)
            mock_get_client.return_value = client

            result = await mcp.call_tool("websearch_status", {})
            data = json.loads(result.content[0].text)
            assert data["total_keys"] == 2
            assert data["available_keys"] == 1

    @patch("mcp_server._get_client")
    async def test_websearch_cache_tool_get(self, mock_get_client):
        with tempfile.TemporaryDirectory() as tmp:
            from sin_websearch.cache import SearchCache
            from sin_websearch.history import SearchHistory

            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)
            mock_get_client.return_value = client

            cache.set("test", {"results": []})
            result = await mcp.call_tool("websearch_cache", {"action": "get", "query": "test"})
            data = json.loads(result.content[0].text)
            assert data["hit"] is True

    @patch("mcp_server._get_client")
    async def test_websearch_cache_tool_clear(self, mock_get_client):
        with tempfile.TemporaryDirectory() as tmp:
            from sin_websearch.cache import SearchCache
            from sin_websearch.history import SearchHistory

            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)
            mock_get_client.return_value = client

            cache.set("a", {"r": 1})
            result = await mcp.call_tool("websearch_cache", {"action": "clear"})
            data = json.loads(result.content[0].text)
            assert data["cleared"] == 1

    @patch("mcp_server._get_client")
    async def test_websearch_history_tool(self, mock_get_client):
        with tempfile.TemporaryDirectory() as tmp:
            from sin_websearch.cache import SearchCache
            from sin_websearch.history import SearchHistory

            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)
            mock_get_client.return_value = client

            history.add("query", "success")
            result = await mcp.call_tool("websearch_history", {"limit": 10})
            data = json.loads(result.content[0].text)
            assert len(data["entries"]) == 1
            assert data["entries"][0]["query"] == "query"

    @patch("mcp_server._get_client")
    async def test_websearch_rate_limit_tool(self, mock_get_client):
        with tempfile.TemporaryDirectory() as tmp:
            pool = SerpAPIKeyPool(["k1"])
            client = SerpAPIClient(pool=pool)
            mock_get_client.return_value = client

            result = await mcp.call_tool("websearch_rate_limit", {})
            data = json.loads(result.content[0].text)
            assert data["total_keys"] == 1

    @patch("mcp_server._get_client")
    async def test_websearch_cache_tool_size(self, mock_get_client):
        with tempfile.TemporaryDirectory() as tmp:
            from sin_websearch.cache import SearchCache
            from sin_websearch.history import SearchHistory

            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)
            mock_get_client.return_value = client

            result = await mcp.call_tool("websearch_cache", {"action": "size"})
            data = json.loads(result.content[0].text)
            assert data["size"] == 0

    @patch("mcp_server._get_client")
    async def test_websearch_cache_tool_list(self, mock_get_client):
        with tempfile.TemporaryDirectory() as tmp:
            from sin_websearch.cache import SearchCache
            from sin_websearch.history import SearchHistory

            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)
            mock_get_client.return_value = client

            cache.set("a", {"r": 1})
            result = await mcp.call_tool("websearch_cache", {"action": "list"})
            data = json.loads(result.content[0].text)
            assert "a" in data["queries"]

    @patch("mcp_server._get_client")
    async def test_websearch_cache_tool_unknown_action(self, mock_get_client):
        with tempfile.TemporaryDirectory() as tmp:
            from sin_websearch.cache import SearchCache
            from sin_websearch.history import SearchHistory

            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)
            mock_get_client.return_value = client

            result = await mcp.call_tool("websearch_cache", {"action": "foo"})
            data = json.loads(result.content[0].text)
            assert "error" in data

    @patch("mcp_server._get_client")
    async def test_websearch_cache_tool_get_missing_query(self, mock_get_client):
        with tempfile.TemporaryDirectory() as tmp:
            from sin_websearch.cache import SearchCache
            from sin_websearch.history import SearchHistory

            cache = SearchCache(db_path=os.path.join(tmp, "cache.db"))
            history = SearchHistory(db_path=os.path.join(tmp, "hist.db"))
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=cache, history=history)
            mock_get_client.return_value = client

            result = await mcp.call_tool("websearch_cache", {"action": "get"})
            data = json.loads(result.content[0].text)
            assert "error" in data

    @patch("mcp_server._get_client")
    async def test_websearch_search_with_engine(self, mock_get_client):
        with tempfile.TemporaryDirectory() as tmp:
            pool = SerpAPIKeyPool(["key1"])
            client = SerpAPIClient(pool=pool, cache=SearchCache(db_path=os.path.join(tmp, "cache.db")))
            mock_get_client.return_value = client

            with responses.RequestsMock() as rsps:
                rsps.add(
                    responses.GET,
                    "https://serpapi.com/search",
                    json={"organic_results": [{"title": "R", "link": "L", "snippet": "S"}]},
                    status=200,
                )
                result = await mcp.call_tool(
                    "websearch_search", {"query": "openai", "engine": "bing", "num_results": 5}
                )
                data = json.loads(result.content[0].text)
                assert data["success"] is True
                req = rsps.calls[0].request
                assert "engine=bing" in req.url
                assert "num=5" in req.url
