# RoleContextPlan/v1

`RoleContextPlan/v1` records what each runtime role received from the run's
single shared capsule (`role-context.json`).

| Field | Meaning |
|---|---|
| `run_id` / `target` / `capsule_id` | Run, TaskSpec target and the capsule built once for it (null without a target) |
| `context_bytes` | Envelope budget for the profile |
| `roles[]` | `{role, capability, context_class, refs, artifact_refs, expertise, bytes, budget_bytes, trimmed}` |
| `total_bytes` / `naive_bytes` | Bytes shipped to all roles versus the full capsule sent to every role |
| `unresolved` | `capsule-unavailable:<reason>`, `capsule:<gap>`, `AF-ROLE-CONTEXT-BUDGET: ...` |

Classes (`rules/role_context.yaml`): `focused` (contract, schema, code, test),
`evidence_plus_delta` (contract, schema, policy + prior artifacts),
`decision_plus_evidence` (policy, contract + prior artifacts),
`disagreements_only` (debate deltas only).
