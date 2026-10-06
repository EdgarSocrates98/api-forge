# EconomyMatrix/v1

`EconomyMatrix/v1` is `apiforge evals economy-matrix`: canonical contract
changes × `economy`/`balanced`/`deep`, with every axis kept apart (no blended
score).

| Field | Meaning |
|---|---|
| `rows[]` | Per case × profile: `quality {verdict, expected, verdict_ok, safety_ok, missing_roles}`, `evidence` (deterministic change ids), `cost {calls, invocations, fanout, trimmed_roles}`, `context_bytes`, `evidence_bytes`, `latency_ms`, `holdout`, `status` |
| `axes` | Per profile: `quality_rate`, `safety_violations`, `evidence_ids_mean`, `calls_mean`, `invocations_mean`, `fanout_mean`, `context_bytes_mean`, `latency_ms_median` |
| `mutation` | `{total, detected}` structural mutants that must turn compatible candidates breaking |
| `gates` | `quality_every_profile`, `safety_zero_violations`, `cost_monotone`, `mutation_score`, `holdout_pass` |
| `tokens` | Always `unresolved` — the matrix runs the fake adapter |

Quality is grounded offline: the deterministic verdict (OpenAPI diff or gRPC
compatibility) against ground truth, plus the safety invariant that every
risk-required role survives the economy trims.
| `claim_scope` | Always `deterministic-safety-economy`: the matrix proves deterministic contract correctness and mandatory role coverage per profile, not end-to-end agentic answer quality (see `evals agentic-quality`) |
