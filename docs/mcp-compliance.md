# MCP compliance matrix — spec revision 2026-07-28

Scope: `apiforge-mcp`, the local FastMCP server (`src/apiforge/mcp/server.py`)
that exposes the API Forge read tools over stdio. Evaluated against the official
MCP specification revision **2026-07-28**. The repository requires the optional
SDK range `mcp>=2.2,<3`; the exact installed SDK and protocol set are observed
by `scripts/mcp_protocol_probe.py`, never inferred from a dependency label.

States: `SUPPORTED` · `PARTIAL` · `NOT_IMPLEMENTED` · `NOT_APPLICABLE`.

| Feature | Specification | Status | Evidence | Gap |
|---|---|---|---|---|
| transport | JSON-RPC 2.0 over stdio; streamable HTTP optional | `SUPPORTED` | `server.run()` uses the FastMCP default stdio transport | no streamable HTTP — deliberate: the server is local-first |
| authorization | OAuth 2.1 for HTTP transports | `NOT_APPLICABLE` | stdio transport carries no HTTP authorization layer | n/a — revisit if an HTTP transport is ever exposed |
| stateless core | requests complete independently | `SUPPORTED` (local proof) | `mcp/modern.py` handles each request independently and declares `stateless=true`; FastMCP stdio remains a separate optional transport | HTTP transport remains out of scope |
| routing | method routing to declared handlers | `SUPPORTED` | SDK routes `tools/call` by name; `apiforge_discover` + `apiforge_call` add a semantic router; §41 `mcp_disclose` routes task → declared tool set | none |
| multi-round-trip | elicitation / multi-step conversations | `NOT_IMPLEMENTED` | no elicitation or sampling use; tools answer in one round-trip | not needed for the read plane; the governed run stays in the runtime |
| cacheable list responses | list results SHOULD be deterministic and bounded | `PARTIAL` | `limit` param on `rules_list`, `capabilities_list`, `contract_list`, `knowledge_list`, `memory_quarantine_list`, `context_delta`, `context_gc`, `economy_pricing`, `perf_chaos`, `perf_memory_search`; §42 `ToolPage`/`paged`/`bound_collections` standardizes windows | no `icons`/cache hints emitted; audit reports `unbounded_list: 0` |
| extensions | protocol extensions negotiated via capabilities | `NOT_APPLICABLE` | no extensions declared or required | none |
| capability negotiation | legacy `initialize`; modern `server/discover` | `SUPPORTED` (modern local proof) / `PARTIAL` (optional SDK) | `tests/mcp/test_modern_protocol.py` drives `server/discover`; FastMCP SDK handshake stays optional and separately probed | no claim that the optional SDK is installed in the default environment |
| resources | `resources/list`, `resources/read` | `NOT_IMPLEMENTED` | no `@mcp.resource` registered — the tool surface covers reads | deliberate: artifacts live behind `ctx://` refs exposed via tools, not the resources primitive |
| tools | `tools/list`, `tools/call` with JSON-Schema args | `SUPPORTED` | 152 tools are registered locally with pydantic-derived schemas; §40 audit measures schema/description bytes and §43 benchmark measures response cost | none |
| error model | JSON-RPC error objects; protocol errors | `SUPPORTED` | refusals raise `ContractError`/`AnalysisError` → SDK error; payload carries `error_code` (`AF-*`), `field` and `unlock` per the catalog | none |
| security | spec security best practices | `SUPPORTED` | read-only tools; no provider SDK imports in `src/`; sensitive-attribute refusal; secrets never enter payloads | none |

## Era-specific protocol proof

Legacy FastMCP clients use `initialize` through the optional SDK transport.
Modern local proof uses `server/discover`, then `tools/list`, then
`tools/call`; these paths are not conflated. `ModernMcpServer` is an
in-process deterministic adapter for offline conformance and does not claim
wire-level HTTP or provider behavior.

```text
ModernMcpClient -> server/discover -> tools/list -> tools/call
```

Proof: `uv run pytest tests/mcp/test_modern_protocol.py -q` → `2 passed`.
Unknown dynamic targets retain `AF-MCP-TOOL-UNKNOWN`; gateway, target and
inner domain gates remain active.

## Version compatibility (§45)

The optional FastMCP server does not hard-code a protocol revision — the SDK
negotiates during legacy `initialize`; the exact local result belongs to the
probe receipt. The offline modern adapter pins its proof contract to
`2026-07-28`. The tool surface itself is additive-versioned: new tools are
appended to the `TOOLS` tuple (never renamed silently), tool names are the
stable public contract, and `agent_aliases.yaml`-style compatibility notes
are recorded when a name must change. Breaking tool-name changes are
refusals with `AF-MCP-TOOL-UNKNOWN` + unlock, not silent drops.

## Tool surface engineering v2 (§40–§43)

- `apiforge mcp audit [--surface full|compact]` — `ToolSurfaceAudit` over the
  measured surface: `oversized_schema`, `poor_description`,
  `unbounded_list`, `overlapping`, `redundant`, `oversized_output` (the last
  only when benchmark bytes are supplied), each labeled
  `observed`/`hypothesis`; thresholds live in `rules/tool_surface.yaml`,
  and the file's `accepted:` list declares reviewed exceptions that land in
  the audit's `accepted` field with their reason — recorded, never dropped.
- `apiforge mcp disclose --task "..."` — §41 advisory router: task text →
  declared task class (`rules/tool_disclosure.yaml`) → active tool set +
  dropped set; unclassified tasks keep the full surface and say so.
- `apiforge mcp benchmark [--repeats N]` — §43 measured median/p95 response
  bytes + chars/4 token estimate (always labeled `estimated`) for the
  declared sample set in `rules/tool_benchmark.yaml`, ranked most expensive
  first; `usefulness` compares medians against declared `max_bytes`.
- §42 output contract — `ToolPage`/`paged()`/`bound_collections()` in
  `output/page.py` gives the standard
  `summary`/`items`/`refs`/`evidence`/`unresolved`/`pagination` shape;
  adopted incrementally on list tools via `limit` parameters (CLI and MCP
  carry the same bound — parity is contractual).

## Local protocol observation

Run `uv run --extra mcp python scripts/mcp_protocol_probe.py`. The probe is
read-only and reports the installed SDK version, its declared latest protocol
revision and whether the target `2026-07-28` is observed. A missing or older
SDK is `unresolved`; it is never upgraded implicitly by the application.

## Compact gateway trust boundary

The six compact gateways use subject `mcp-gateway` in offline tool-risk
policy. Unknown subjects or missing gateway grants fail closed with an `AF-*`
refusal carrying `field` and `unlock`; dynamic dispatch keeps inner API Forge
policy checks intact.
