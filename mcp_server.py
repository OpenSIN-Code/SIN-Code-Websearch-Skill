"""Backwards-compatible entry point for the sin-websearch MCP server.

Docs: mcp_server.doc.md

The tool implementations live in `sin_websearch.mcp_server` (inside the
package) so they can be imported by the `cli_shims/` wrappers. This file
re-exports them and keeps the `python mcp_server.py` / `sin-websearch-server`
entry points working.
"""

from sin_websearch.mcp_server import _get_client, main, mcp  # noqa: F401

if __name__ == "__main__":
    main()
