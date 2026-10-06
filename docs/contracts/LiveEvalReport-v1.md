# LiveEvalReport-v1

§23 one run of the live-eval layer.

| Field | Meaning |
|---|---|
| `layer` | the `LiveEvalLayer` in force |
| `deterministic` | per-eval pass/totals actually observed |
| `provider_status`/`provider_results` | tier state and results — results require `observed` |
| `unresolved` | why the provider tier did not run |

Invariant: provider results require `observed`; `deferred_external` must name the reason.
