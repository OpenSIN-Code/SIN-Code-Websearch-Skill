"""Tests for the `websearch-status` CLI shim."""
from __future__ import annotations

import json
import subprocess
import sys


def _run_cli() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "sin_websearch.cli_shims.websearch_status"],
        capture_output=True, text=True, timeout=30,
    )


def test_websearch_status_help():
    result = subprocess.run(
        [sys.executable, "-m", "sin_websearch.cli_shims.websearch_status", "--help"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_websearch_status_returns_valid_json():
    """Real call returns JSON describing the key pool."""
    result = _run_cli()
    assert result.returncode == 0, f"stderr: {result.stderr}"
    data = json.loads(result.stdout)
    # Pool status is a dict with at least the key counters.
    assert isinstance(data, dict)
    assert "total_keys" in data
    assert "available_keys" in data
