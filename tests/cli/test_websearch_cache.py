"""Tests for the `websearch-cache` CLI shim."""
from __future__ import annotations

import json
import subprocess
import sys


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "sin_websearch.cli_shims.websearch_cache", *args],
        capture_output=True, text=True, timeout=30,
    )


def test_websearch_cache_help():
    result = _run_cli("--help")
    assert result.returncode == 0
    out = result.stdout.lower()
    assert "usage" in out
    assert "--action" in out


def test_websearch_cache_size():
    """`--action size` returns a JSON object with a `size` key."""
    result = _run_cli("--action", "size")
    assert result.returncode == 0, f"stderr: {result.stderr}"
    data = json.loads(result.stdout)
    assert "size" in data
    assert isinstance(data["size"], int)


def test_websearch_cache_list():
    """`--action list` returns a JSON object with a `queries` list."""
    result = _run_cli("--action", "list")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "queries" in data
    assert isinstance(data["queries"], list)
