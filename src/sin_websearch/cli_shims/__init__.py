"""CLI shims for sin-websearch MCP tools.

Docs: cli_shims/__init__.doc.md

Each module in this package wraps one MCP tool as a standalone
argparse-based binary so sub-agents and shell users can call them
without an MCP server.

The shims import directly from `sin_websearch.mcp_server` — the same
module the MCP server itself uses — so behavior stays in lock-step.
"""
