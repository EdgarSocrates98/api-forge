"""Real MCP SDK proof — ``initialize`` + ``tools/list`` + ``tools/call``.

Runs the production ``MCPServer`` (mcp>=2.2) over in-memory bidirectional
streams with a real ``ClientSession`` — genuine JSON-RPC round-trips, not the
contract-shape adapter. The test skips (never fakes) when the optional SDK is
absent.
"""

from __future__ import annotations

import asyncio
import json

import pytest

pytest.importorskip("mcp", reason="optional MCP SDK not installed")

from mcp import ClientSession
from mcp.shared.memory import create_client_server_memory_streams


async def _sdk_roundtrip() -> dict[str, object]:
    from apiforge.mcp.server import build_server

    server = build_server("compact")
    low = server._lowlevel_server  # MCPServer keeps the protocol engine private
    async with (
        create_client_server_memory_streams() as (client_streams, server_streams),
        ClientSession(*client_streams) as session,
    ):
        serve = asyncio.create_task(
            low.run(
                server_streams[0],
                server_streams[1],
                low.create_initialization_options(),
            )
        )
        try:
            init = await session.initialize()
            tools = await session.list_tools()
            discover = await session.call_tool("apiforge_discover", {"query": "rules"})
            call = await session.call_tool(
                "apiforge_call",
                {"tool": "rules_list", "arguments": {"limit": 1}},
            )
            denied = await session.call_tool(
                "apiforge_call",
                {"tool": "memory_persist", "arguments": {}},
            )
        finally:
            serve.cancel()
            await asyncio.wait([serve])
    return {
        "server_name": init.server_info.name,
        "protocol_version": str(init.protocol_version),
        "tool_names": sorted(tool.name for tool in tools.tools),
        "discover_is_error": bool(discover.is_error),
        "call_is_error": bool(call.is_error),
        "call_payload": json.loads(call.content[0].text),
        "denied_is_error": bool(denied.is_error),
    }


def test_real_sdk_initialize_list_and_call() -> None:
    result = asyncio.run(_sdk_roundtrip())
    assert result["server_name"] == "apiforge"
    assert {"apiforge_discover", "apiforge_call"} <= set(result["tool_names"])
    assert result["discover_is_error"] is False
    assert result["call_is_error"] is False
    # risk-aware target authorization applies inside the real SDK dispatch too
    assert result["denied_is_error"] is True
