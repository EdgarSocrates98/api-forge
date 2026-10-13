# RetrievalStep/v1

One level attempted inside the §36 adaptive ladder.

| Field | Meaning |
|---|---|
| `level` | `L0` exact / `L1` lexical / `L2` graph / `L3` hybrid semantic / `L4` reranker |
| `hits` / `top_score` | Results found and top effective score after level weighting |
| `raw_top_score` | Highest source score before level weighting; diagnostic only |
| `escalated` | `true` when the level was insufficient and the ladder continued |
| `reason` | `sufficient`, `insufficient` or `adapter undeclared` |
