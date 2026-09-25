# RoutingEvolution/v1

Typed snapshot for one routing evolution wave. It binds a deterministic
`RoutingDecision/v1` to its `PromotionGate/v1` result and the policy version
that produced it.

| Field | Shape | Meaning |
|---|---|---|
| `decision_id` | `str` | Stable routing decision identity |
| `wave` | `int` | Non-negative evolution wave |
| `policy_version` | `str` | Versioned evolution policy reference |
| `gate` | `PromotionGate/v1` | Evidence and promotion result |
| `plan_digest` | `str \| null` | Optional digest of a future bounded plan proposal |

Wave 0 persists the gate directly in the run store. Later waves may populate
`plan_digest`, but cannot use this field to bypass evidence coverage,
rollback or the static fallback.
