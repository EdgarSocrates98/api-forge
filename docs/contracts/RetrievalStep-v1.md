# RetrievalStep/v1

One level attempted inside the §36 adaptive ladder.

| Field | Meaning |
|---|---|
| `level` | `L0` exact / `L1` lexical / `L2` graph / `L3` hybrid semantic / `L4` reranker |
| `hits` / `top_score` | Results found and the raw top score (scale follows the level) |
| `escalated` | `true` when the level was insufficient and the ladder continued |
| `reason` | `sufficient`, `insufficient` or `adapter undeclared` |
