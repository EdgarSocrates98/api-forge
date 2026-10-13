# RoleContextPolicy/v1

RoleContext v2 policy row declared in `rules/role_context.yaml` under
`policies:`; absent fields keep permissive v1 defaults.

| Field | Meaning |
|---|---|
| `required_kinds` | Kinds delivered first inside the role budget; a kind present in the capsule but undelivered is `AF-ROLE-CONTEXT-REQUIRED` |
| `denied_kinds` | Kinds hard-trimmed with `AF-ROLE-CONTEXT-DENIED` even when the class allows them |
| `memory_visibility` / `knowledge_visibility` / `artifact_visibility` | `none`, `summary` or `full` per plane |
| `tool_visibility` | Tool allowlist once non-empty; empty means unrestricted (v1) |
| `minimum_origin_rank` | Deterministic provenance floor over `ContextRef.origin` (`filesystem` < `knowledge` < `code` < `graph` < `contract`); violators carry `AF-ROLE-CONTEXT-TRUST` |
| `max_context_bytes` / `max_context_tokens` | Additional caps on top of the class share |
| `required_evidence` | Declared evidence-citation requirement for role outputs |

Invariant: `required_kinds` and `denied_kinds` must be disjoint.
