"""CLI: websearch-cache — inspect/manipulate the search result cache.

Usage: websearch-cache [--query QUERY] [--action get|set|clear|list|size]
"""
from __future__ import annotations

import argparse
import sys

from sin_websearch.mcp_server import websearch_cache


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="websearch-cache",
        description="Interact with the sin-websearch result cache.",
    )
    parser.add_argument("--query", default=None, help="Query string (required for get/set).")
    parser.add_argument(
        "--action",
        default="get",
        choices=["get", "set", "clear", "list", "size"],
        help="Cache action (default: get).",
    )
    args = parser.parse_args(argv)

    print(websearch_cache(query=args.query, action=args.action))
    return 0


if __name__ == "__main__":
    sys.exit(main())
