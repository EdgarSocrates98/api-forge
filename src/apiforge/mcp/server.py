"""MCP SDK wiring — registers the full tool set or the compact gateway surface.

Imported lazily by ``apiforge.mcp.main`` so the ``mcp`` extra is only
required when the server actually runs. The SDK is pinned ``mcp>=2.2,<3``;
in v2 the server class is ``MCPServer`` (``mcp.server.mcpserver``), the
v1 ``FastMCP`` import path no longer exists.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

MCP_OPTIONAL_UNAVAILABLE = "AF-MCP-OPTIONAL-UNAVAILABLE"


def build_server(surface: str = "full", protocol: str = "legacy") -> Any:
    if protocol == "modern":
        from apiforge.mcp.modern import build_modern_server

        return build_modern_server(surface)
    if protocol != "legacy":
        raise ValueError(f"unsupported MCP protocol {protocol!r}")
    try:
        MCPServer = import_module("mcp.server.mcpserver").MCPServer
    except (ImportError, AttributeError) as exc:
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
    server = MCPServer("apiforge", instructions=instructions)
    for tool in tools:
        server.add_tool(tool)
    return server
