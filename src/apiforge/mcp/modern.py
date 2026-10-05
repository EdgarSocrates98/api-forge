"""In-process modern MCP protocol proof.

This adapter keeps protocol-shape verification independent from the optional
MCP SDK. It exercises the local server contract for ``server/discover``,
``tools/list`` and ``tools/call`` without network access or provider state.
The FastMCP stdio server remains the production transport when the extra is
installed.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from typing import Any

from apiforge.contracts.base import ContractError
from apiforge.mcp.gateway import apiforge_call
from apiforge.mcp.surface import surface_tools, tool_schema

MCP_MODERN_PROTOCOL = "2026-07-28"


def _error(error: Exception) -> dict[str, Any]:
    code = getattr(error, "code", "AF-MCP-MODERN-REQUEST")
    field = getattr(error, "field", "request")
    unlock = getattr(error, "unlock", "inspect the local MCP contract")
    return {
        "isError": True,
        "error": {
            "code": str(code),
            "detail": str(error),
            "field": str(field),
            "unlock": str(unlock),
        },
    }


class ModernMcpServer:
    """Stateless local handler for modern MCP request shapes."""

    def __init__(self, surface: str = "compact") -> None:
        self.surface = surface
        self._tools = {tool.__name__: tool for tool in surface_tools(surface)}

    def request(self, method: str, params: Mapping[str, Any] | None = None) -> dict[str, Any]:
        values = dict(params or {})
        try:
            if method == "server/discover":
                return {
                    "protocolVersion": MCP_MODERN_PROTOCOL,
                    "serverInfo": {"name": "apiforge", "version": "0.1.0"},
                    "capabilities": {"tools": {"listChanged": False}},
                    "transport": {"stateless": True, "surface": self.surface},
                }
            if method == "tools/list":
                return {
                    "tools": [
                        {
                            "name": name,
                            "description": (tool.__doc__ or "").splitlines()[0],
                            "inputSchema": tool_schema(tool),
                        }
                        for name, tool in sorted(self._tools.items())
                    ]
                }
            if method == "tools/call":
                return self._call(values)
            raise ContractError("AF-MCP-MODERN-METHOD", f"unsupported MCP method {method!r}")
        except (ContractError, ValueError, TypeError) as exc:
            return _error(exc)

    def _call(self, params: dict[str, Any]) -> dict[str, Any]:
        name = params.get("name")
        arguments = params.get("arguments", {})
        if not isinstance(name, str) or name not in self._tools:
            raise ContractError(
                "AF-MCP-TOOL-UNKNOWN",
                f"tool {name!r} is not declared on the {self.surface} surface",
            )
        if not isinstance(arguments, Mapping):
            raise ContractError("AF-MCP-TOOL-ARGS", "arguments must be an object")
        result = (
            apiforge_call(arguments.get("tool", ""), dict(arguments.get("arguments") or {}))
            if name == "apiforge_call"
            else self._tools[name](**dict(arguments))
        )
        structured = result if isinstance(result, dict) else {"value": result}
        return {
            "isError": False,
            "structuredContent": structured,
            "content": [{"type": "text", "text": json.dumps(structured, sort_keys=True)}],
        }

    def run(self) -> None:
        """Serve newline-delimited local JSON-RPC requests over stdio."""
        for line in sys.stdin:
            if not line.strip():
                continue
            request = json.loads(line)
            response = self.request(str(request.get("method", "")), request.get("params"))
            print(
                json.dumps(
                    {"jsonrpc": "2.0", "id": request.get("id"), "result": response},
                    sort_keys=True,
                ),
                flush=True,
            )


class ModernMcpClient:
    """Tiny local client used by the offline conformance proof."""

    def __init__(self, server: ModernMcpServer) -> None:
        self.server = server

    def discover(self) -> dict[str, Any]:
        return self.server.request("server/discover")

    def list_tools(self) -> dict[str, Any]:
        return self.server.request("tools/list")

    def call(self, name: str, arguments: Mapping[str, Any] | None = None) -> dict[str, Any]:
        return self.server.request("tools/call", {"name": name, "arguments": arguments or {}})


def build_modern_server(surface: str = "compact") -> ModernMcpServer:
    """Build the local modern proof server; production transport stays FastMCP."""
    return ModernMcpServer(surface)


__all__ = ["MCP_MODERN_PROTOCOL", "ModernMcpClient", "ModernMcpServer", "build_modern_server"]
