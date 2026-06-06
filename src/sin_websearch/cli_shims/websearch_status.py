"""CLI: websearch-status — show SerpAPI key pool status.

Usage: websearch-status
"""
from __future__ import annotations

import argparse
import sys

from sin_websearch.mcp_server import websearch_status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="websearch-status",
        description="Show current SerpAPI pool status (keys, cooldown, suspension).",
    )
    args = parser.parse_args(argv)
    print(websearch_status())
    return 0


if __name__ == "__main__":
    sys.exit(main())
