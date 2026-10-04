# ModelScorecard/v1

§34 quality history per provider/model, segmented by task class.

| Field | Meaning |
|---|---|
| `evaluation_count` | How many `ModelEvaluation` rows fed this card — drives `insufficient-evaluations` |
| `quality` / `tool_selection_accuracy` / `evidence_correctness` / `structured_output_reliability` | Means over observed rows; `null` when nothing was observed |
| `latency_p50_ms` / `cost_mean` / `failure_rate` | Median latency, mean cost, failed share |
| `freshness_state` | `fresh`/`stale`/`unresolved`/`unknown` — stale/unresolved blocks quality claims |
| `unresolved` | Metrics never observed |

A scorecard is a *constraint*: below `quality_floor` with enough evaluations,
the candidate cannot compete on cost.
