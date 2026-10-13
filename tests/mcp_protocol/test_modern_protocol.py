"""Offline MCP modern-era client/server conformance proof."""

from apiforge.mcp.modern import MCP_MODERN_PROTOCOL, ModernMcpClient, build_modern_server


def test_modern_client_discover_list_and_call_are_local_and_stateless() -> None:
    client = ModernMcpClient(build_modern_server())
    discovered = client.discover()
    assert discovered["protocolVersion"] == MCP_MODERN_PROTOCOL
    assert discovered["transport"] == {"stateless": True, "surface": "compact"}

    listed = client.list_tools()
    names = {item["name"] for item in listed["tools"]}
    assert {"apiforge_discover", "apiforge_call"} <= names
    assert all("inputSchema" in item for item in listed["tools"])

    discovery = client.call("apiforge_discover", {"query": "rules"})
    assert discovery["isError"] is False
    assert discovery["structuredContent"]["query"] == "rules"

    called = client.call(
        "apiforge_call",
        {"tool": "rules_list", "arguments": {"limit": 1}},
    )
    assert called["isError"] is False
    assert called["structuredContent"]["count"] >= 0


def test_modern_client_preserves_unknown_target_refusal() -> None:
    client = ModernMcpClient(build_modern_server())
    result = client.call(
        "apiforge_call",
        {"tool": "not-a-declared-tool", "arguments": {}},
    )
    assert result["isError"] is True
    assert result["error"]["code"] == "AF-MCP-TOOL-UNKNOWN"
