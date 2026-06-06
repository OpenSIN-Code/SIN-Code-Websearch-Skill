"""Tests for the `websearch-rate-limit` CLI shim."""
from __future__ import annotations

import json
import subprocess
import sys


def _run_cli() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "sin_websearch.cli_shims.websearch_rate_limit"],
        capture_output=True, text=True, timeout=30,
    )


def test_websearch_rate_limit_help():
    result = subprocess.run(
        [sys.executable, "-m", "sin_websearch.cli_shims.websearch_rate_limit", "--help"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_websearch_rate_limit_returns_valid_json():
    result = _run_cli()
    assert result.returncode == 0, f"stderr: {result.stderr}"
    data = json.loads(result.stdout)
    # Pool status contains the key counters.
    assert isinstance(data, dict)
    assert "total_keys" in data
    assert "available_keys" in data
