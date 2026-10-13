# RetrievalComparison/v1

§38 per-strategy metrics over a gold corpus.

| Field | Meaning |
|---|---|
| `strategy` | `lexical`, `graph`, `semantic` or `hybrid` |
| `recall` / `precision` | Gold coverage / gold share of returned keys |
| `latency_ms` | Measured wall clock for the strategy |
| `tokens` | Returned passage bytes ÷ 4 (declared measure) |
| `cost` | `tokens × --cost-rate`, or `null` with `cost_rate` in `unresolved` |
