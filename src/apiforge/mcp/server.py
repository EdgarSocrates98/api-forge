"""FastMCP wiring — registers every tool in ``tools.TOOLS``.

Imported lazily by ``apiforge.mcp.main`` so the ``mcp`` extra is only
required when the server actually runs.
"""

from __future__ import annotations

from typing import Any

MCP_OPTIONAL_UNAVAILABLE = "AF-MCP-OPTIONAL-UNAVAILABLE"


def build_server() -> Any:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError(
            f"{MCP_OPTIONAL_UNAVAILABLE}: install the 'mcp' extra to run local stdio"
        ) from exc

    from apiforge.mcp.tools import GRPC_TOOLS, MIGRATION_TOOLS, OBSERVABILITY_TOOLS, TOOLS

    server = FastMCP(
        "apiforge",
        instructions=(
            "Deterministic, offline API analysis. Every tool accepts "
            "detail_level (summary|normal|full); findings cite rule_id and "
            "fact_id; unresolved counts are always reported."
        ),
    )
    for tool in TOOLS + OBSERVABILITY_TOOLS + GRPC_TOOLS + MIGRATION_TOOLS:
        server.add_tool(tool)
    return server
