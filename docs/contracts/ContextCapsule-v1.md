# ContextCapsule/v1

`ContextCapsule/v1` (`schema: apiforge/context-capsule/v1`) is the minimal
sufficient evidence for one operation, emitted by `apiforge context capsule`
and the `context_capsule` MCP tool.

| Field | Meaning |
|---|---|
| `capsule_id` | `ctx://sha256/<hex>` of the canonical body (without `capsule_id`, `run_id`, `serialized_bytes`) |
| `run_id` | Attribution key in `economy.jsonl`; defaults to `run-<last 16 hex of capsule_id>` |
| `intent` | L0 — action, normalized target (`METHOD /path`), optional objective |
| `scope` | `ContextScope/v1` with `scope: target` and root `.` |
| `fingerprint` | L1 — case id, contract, project, frameworks, operation count |
| `impact` | L2 — `direct` graph edges and `transitive` findings reached |
| `refs` | L3/L4 — ordered, unique `ContextRef/v1` entries |
| `policies` | Rule ids of findings reached from the target's route facts |
| `budget` | `CapsuleBudget/v1` |
| `refusals` | Cataloged `CapsuleRefusal/v1` entries for partial results |
| `unresolved` | Explicit gaps such as `code-route-missing:<op>` or `graph-unavailable` |
| `status` | `ready`, `degraded` (no case graph) or `unresolved` (budget exhausted) |

The capsule is byte-identical for the same case, target, budget and level.
Transport drops default-valued fields; `schema`, `version` and `status` are
always present. Refs are admitted whole or not at all.
