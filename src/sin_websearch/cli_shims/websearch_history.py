"""CLI: websearch-history — list recent search history entries.

Usage: websearch-history [--limit N] [--offset N] [--query-filter SUBSTR]
"""
from __future__ import annotations

import argparse
import sys

from sin_websearch.mcp_server import websearch_history


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="websearch-history",
        description="List recent sin-websearch search history entries.",
    )
    parser.add_argument("--limit", type=int, default=50, help="Max entries to return (default: 50).")
    parser.add_argument("--offset", type=int, default=0, help="Pagination offset (default: 0).")
    parser.add_argument("--query-filter", default=None, help="Substring filter on query.")
    args = parser.parse_args(argv)

    print(
        websearch_history(
            limit=args.limit,
            offset=args.offset,
            query_filter=args.query_filter,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
