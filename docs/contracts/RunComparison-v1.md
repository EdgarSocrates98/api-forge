# RunComparison/v1

§55 deterministic a/b of two runs — the JSON projection of
`apiforge agentops compare A B`.

| Field | Meaning |
|---|---|
| `run_a`/`run_b` | Baseline and candidate run ids |
| `axes` | `quality`, `tokens`, `cost`, `latency`, `context`, `evidence`, `tools`, `agents` — the declared axis set |
| `unresolved` | Axes that could not decide and per-run unresolved items |

Invariant: an axis whose either side lacks a numeric value is `unresolved`,
never a tie by absence.
