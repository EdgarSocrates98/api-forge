# ToolSurface/v1

`ToolSurface/v1` is `apiforge mcp surface`: what an MCP surface costs to
publish, measured rather than assumed.

| Field | Meaning |
|---|---|
| `surface` | `full` (every tool) or `compact` (six gateways) |
| `tools[]` | `{name, name_bytes, description_bytes, schema_bytes}` |
| `tool_count` / `total_bytes` | Totals for the surface |
| `reachable_capabilities` | Full tools reachable (compact reaches all of them through `apiforge_call`) |
| `schema_source` | `signature`: JSON schema derived with pydantic from the tool signature, as FastMCP does |

What a host actually loads (for example deferred tool schemas) is host
behavior, declared in `HostProjection/v1`.
