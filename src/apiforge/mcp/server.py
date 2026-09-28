"""FastMCP wiring — registers the full tool set or the compact gateway surface.

Imported lazily by ``apiforge.mcp.main`` so the ``mcp`` extra is only
required when the server actually runs.
"""

from __future__ import annotations

from typing import Any

MCP_OPTIONAL_UNAVAILABLE = "AF-MCP-OPTIONAL-UNAVAILABLE"


def build_server(surface: str = "full") -> Any:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError(
            f"{MCP_OPTIONAL_UNAVAILABLE}: install the 'mcp' extra to run local stdio"
        ) from exc

    from apiforge.mcp.surface import surface_tools

    tools = surface_tools(surface)
    instructions = (
        "Deterministic, offline API analysis. Every tool accepts "
        "detail_level (summary|normal|full); findings cite rule_id and "
        "fact_id; unresolved counts are always reported."
    )
    if surface == "compact":
        instructions = (
            "Deterministic, offline API analysis through six gateways. Ask "
            "apiforge_discover for the right tool, then apiforge_call it; every "
            "full capability stays reachable. Results drop null/empty fields only."
        )
    server = FastMCP("apiforge", instructions=instructions)
    for tool in tools:
        server.add_tool(tool)
    return server
