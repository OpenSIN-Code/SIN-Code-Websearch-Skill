"""CLI: websearch-rate-limit — show current rate-limit status.

Usage: websearch-rate-limit
"""
from __future__ import annotations

import argparse
import sys

from sin_websearch.mcp_server import websearch_rate_limit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="websearch-rate-limit",
        description="Check current rate limits and SerpAPI key availability.",
    )
    args = parser.parse_args(argv)
    print(websearch_rate_limit())
    return 0


if __name__ == "__main__":
    sys.exit(main())
