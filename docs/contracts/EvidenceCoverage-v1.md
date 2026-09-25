# EvidenceCoverage/v1

Deterministic summary of the evidence required and available for one routing
decision. `missing` is always `required - available`; unknown or unresolved
limitations remain explicit and never become a success signal.

| Field | Shape | Meaning |
|---|---|---|
| `required` | `tuple[str, ...]` | Evidence references needed by the gate |
| `available` | `tuple[str, ...]` | Evidence references actually present |
| `missing` | `tuple[str, ...]` | Required references not present |
| `state` | `complete \| partial \| missing \| unresolved` | Coverage result |
| `limitations` | `tuple[str, ...]` | Known gaps that prevent a stronger claim |

The evaluator is pure and offline. No provider, model, database or network
call is implied by this contract. A coverage result of `complete` only means
that the declared references exist; promotion still requires the separate
`PromotionGate/v1` policy and rollback checks.
