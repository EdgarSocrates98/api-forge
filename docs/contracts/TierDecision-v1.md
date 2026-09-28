# TierDecision/v1

`TierDecision/v1` is `apiforge economy tier --capability C --risk R [--family F]`.

| Field | Meaning |
|---|---|
| `tier` | T0 deterministic, T1 cheap/local, T2 strong, T3 strongest |
| `providers` | Declared providers of that tier |
| `reason` | T0 deterministic implementation; T3 high risk; T1 only with a fresh promoted scorecard `<family>@T1` at or above the quality floor; otherwise T2 "no benchmark evidence" |
