# TrustUnit/v1

The transversal trust annotation carried by any context unit — capsule refs,
memory rows, blackboard entries, knowledge packs, tool results, MCP responses,
agent handoffs and external content (step11 §8–§9).

| Field | Meaning |
|---|---|
| `subject` | Identifier of the annotated unit (uri, memory_id, subject string) |
| `boundary` | Trust boundary: `context_capsule`, `memory`, `blackboard`, `knowledge`, `tool_result`, `mcp_response`, `agent_handoff`, `api_spec`, `external_content`, `log`, `ci_output`, `documentation`, `web` |
| `origin` | Closed `MemoryOrigin` vocabulary (`system` … `unknown`) |
| `trust_level` | Baseline trust assigned by `BASE_TRUST` unless evidence lifts it |
| `taint` | Sorted taint labels; union of `ORIGIN_TAINT` plus caller-supplied marks |
| `instruction_authority` | `system`, `policy` or `none` |
| `scope` / `provenance` / `freshness` / `evidence_refs` | Usual bounded context metadata |

Invariant — DATA IS NOT INSTRUCTION: `instruction_authority != "none"` is only
valid for origins `system` and `governed_policy`; every other origin raises
validation error rather than silently carrying authority.
