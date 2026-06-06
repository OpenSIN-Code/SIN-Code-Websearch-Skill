"""CLI: websearch-search — run a web search via SerpAPI.

Usage: websearch-search QUERY [--engine ENGINE] [--num-results N]
                            [--location LOC] [--language LANG]
"""
from __future__ import annotations

import argparse
import sys

from sin_websearch.mcp_server import websearch_search


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="websearch-search",
        description="Search the web using SerpAPI (single-key pool, with caching).",
    )
    parser.add_argument("query", help="Search query string.")
    parser.add_argument("--engine", default="google", help="Search engine (default: google).")
    parser.add_argument("--num-results", type=int, default=10, help="Number of results (default: 10).")
    parser.add_argument("--location", default=None, help="Optional location filter.")
    parser.add_argument("--language", default=None, help="Optional language code (e.g. 'en').")
    args = parser.parse_args(argv)

    result = websearch_search(
        query=args.query,
        engine=args.engine,
        num_results=args.num_results,
        location=args.location,
        language=args.language,
    )
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
