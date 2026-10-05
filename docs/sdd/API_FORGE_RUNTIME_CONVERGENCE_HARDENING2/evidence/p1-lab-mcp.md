# P1 Lab/MCP evidence

M1: `ModernMcpClient` → `server/discover` → `tools/list` → `tools/call`.
MCP SDK absent in default environment; proof uses local stateless adapter and
does not claim wire/provider support.

Proof:

- `uv run pytest tests/mcp/test_modern_protocol.py -q --basetemp=E:/pytest-apiforge-hardening2-mcp-modern`
- result: `2 passed`
- unknown dynamic target preserves `AF-MCP-TOOL-UNKNOWN`
- existing `apiforge lab scenarios`: `21/21` catalog cells covered

Artifacts:

- `src/apiforge/mcp/modern.py`
- `tests/mcp/test_modern_protocol.py`
- `docs/mcp-compliance.md`

Unresolved: optional FastMCP SDK handshake and HTTP transport remain external;
legacy `initialize` stays separately classified.
