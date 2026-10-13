# PromotionEvidence/v1

§31 the five requirements for an `active` promotion — each a declared fact,
never inferred from the request text.

| Field | Meaning |
|---|---|
| `eval_thresholds_passed` | The route's evals cleared the declared thresholds |
| `security_gates_passed` | Security gates cleared |
| `evidence_complete` | The evidence trail (incl. shadow records) is complete |
| `rollback_exists` | A rollback path is declared and tested |
| `approval_id` | An `ApprovalGate` id that must resolve to `approved` |
| `evidence_refs` | Backing refs for the claims |

For `shadow → assisted` only `evidence_complete` is required; `assisted →
active` requires all five plus the matching approved gate.
