# LiveEvalLayer-v1

§23 the declared periodic eval layer.

| Field | Meaning |
|---|---|
| `profiles` | `economy`/`balanced`/`deep` |
| `metrics` | the nine §23 measurement axes |
| `deterministic_evals`/`corpus_refs` | declared tier membership and corpora |
| `provider_tier` | `deferred_external`/`declared`/`observed` |

Invariant: the layer is declared data — `rules/live_evals.yaml` is the source of truth.
