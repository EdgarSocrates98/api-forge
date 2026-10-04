# ModelEvaluation/v1

§34 one observed evaluation feeding a `ModelScorecard`.

| Field | Meaning |
|---|---|
| `provider` / `model` / `task_class` | The segmentation key (`analysis`, `generation`, `verification`, `extraction`, `routing`) |
| `quality` | Outcome quality `0..1` |
| `tool_selection_accuracy` | Right tool chosen `0..1` |
| `evidence_correctness` | Evidence cited correctly `0..1` |
| `structured_output_reliability` | Valid schema output `0..1` |
| `latency_ms` / `cost` / `failed` | Measured economics; `failed` is an outright failure |
| `recorded_at` / `evidence_refs` | When observed + backing refs |

Metrics with no observations stay `null` on the scorecard, named in
`unresolved` — never zeroed.
