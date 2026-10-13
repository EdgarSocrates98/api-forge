# MemoryInvalidationPlan/v1

Advisory §16 invalidation candidates for one trigger — produced by
`suggest_invalidations()`; it never mutates the store.

| Field | Meaning |
|---|---|
| `trigger` | `runtime_change`, `framework_change`, `contract_change`, `policy_change`, `source_change`, `contradicting_evidence`, `outcome_invalid`, `dependency_change` |
| `memory_ids` | Live records the trigger probably invalidates |
| `rationale` | Per-id explanation (environment drift, touched provenance, named evidence) |
| `unresolved` | Inputs the planner needed but lacked (fingerprint, changed ids, memory ids) |

Environment triggers flag records whose `environment_fingerprint` predates the
current one; source/contract/policy/dependency triggers match `changed`
identifiers against provenance, evidence_refs and applicability; evidence and
outcome triggers take explicit `memory_ids`. Applying a plan is always a
separate `invalidate_memory` append — never a delete.
