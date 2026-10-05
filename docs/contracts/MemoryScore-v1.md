# MemoryScore/v1

Score decomposition for one retrieved memory record (step11 §15).

| Field | Meaning |
|---|---|
| `memory_id` | The ranked record |
| `score` | Weighted sum of the signals, plus optional semantic bonus |
| `signals` | Named components: `exact`, `lexical`, `env_compat`, `runtime_compat`, `freshness`, `trust`, `outcome`, `evidence`, and `semantic` only when the caller supplies a score |

Deterministic weights sum to 1.0; ties break on `memory_id`. Semantic
similarity is an additive caller-supplied bonus, never a dependency — without
it the ranking is fully offline and reproducible.
