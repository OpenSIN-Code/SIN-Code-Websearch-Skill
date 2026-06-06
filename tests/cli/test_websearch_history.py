"""Tests for the `websearch-history` CLI shim."""
from __future__ import annotations

import json
import subprocess
import sys


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "sin_websearch.cli_shims.websearch_history", *args],
        capture_output=True, text=True, timeout=30,
    )


def test_websearch_history_help():
    result = _run_cli("--help")
    assert result.returncode == 0
    out = result.stdout.lower()
    assert "usage" in out
    assert "--limit" in out


def test_websearch_history_default_limit():
    """No args returns a JSON object with an `entries` list."""
    result = _run_cli()
    assert result.returncode == 0, f"stderr: {result.stderr}"
    data = json.loads(result.stdout)
    assert "entries" in data
    assert isinstance(data["entries"], list)


def test_websearch_history_limit_three():
    """`--limit 3` returns at most 3 entries (or fewer if the history is short)."""
    result = _run_cli("--limit", "3")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data["entries"]) <= 3
