# EvolutionPolicy/v1

Bounded local policy for a routing evolution wave.

| Field | Shape | Meaning |
|---|---|---|
| `active_wave` | `int` | Current non-negative wave |
| `mode` | `local \| replay \| shadow \| external-read` | Explicit policy mode |
| `promotion` | `evidence_gated` | Promotion strategy |
| `fallback` | `str` | Static route used when promotion is refused |
| `allow_external_mutation` | `bool` | Must remain `false` in the core |
| `require_rollback_ref` | `bool` | Whether active local execution needs rollback evidence |
| `unknown_evidence` | `unresolved` | Required handling for unknown evidence |
| `adaptive_plan_enabled` | `bool` | Future adaptive-plan switch |
| `adaptive_plan_max_steps` | `int \| null` | Mandatory bound when adaptive planning is enabled |

Wave 0 loads this policy from the versioned local YAML rule and refuses
external mutation or unbounded adaptive planning. It does not discover
provider capabilities or contact external systems.
