# PromotionGate/v1

Evidence-gated authorization state for one routing decision.

| Field | Shape | Meaning |
|---|---|---|
| `decision_id` | `str` | Routing decision being evaluated |
| `mode` | `local \| replay \| shadow \| external-read` | Explicit execution/evidence mode |
| `state` | `planned \| observed \| simulated \| active \| blocked` | Result of the gate |
| `coverage` | `EvidenceCoverage/v1` | Required/available evidence summary |
| `evidence_refs` | `tuple[str, ...]` | References carried into the gate |
| `gaps` | `tuple[str, ...]` | Missing evidence or unresolved policy reasons |
| `fallback` | `str` | Safe route used when active promotion is refused |
| `policy_version` | `str` | Evolution policy identity |
| `rollback_ref` | `str \| null` | Reversible local execution reference |
| `limitations` | `tuple[str, ...]` | Explicit limitations on interpretation |

Only `local/active` authorizes the supervisor to invoke capabilities. It
requires complete coverage, at least one evidence reference and a rollback
reference. `replay` is `simulated`; `shadow` and `external-read` are
`observed`; incomplete coverage is `blocked`. All states are persisted in
`evolution.json` and in the append-only trajectory.
