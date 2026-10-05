# AdaptiveRetrievalResult/v1

§36 the ladder outcome — the level that sufficed, with the full trace.

| Field | Meaning |
|---|---|
| `level_used` | The level where the ladder stopped |
| `steps` | Every attempted level in order |
| `hits` | Top-5 ctx refs of the winning level |
| `semantic_available` | `false` when L3 was skipped for an undeclared adapter |
| `unresolved` | `semantic` and/or `no-passage-matched` |

The ladder never climbs past the first sufficient level — `L4` only runs
when L0–L3 all missed.
