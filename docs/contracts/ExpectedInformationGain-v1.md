# ExpectedInformationGain/v1

§24 pre-action expected gain — evaluated *before* `spawn_agent`,
`call_reviewer`, `start_debate`, `expand_context` or
`expensive_retrieval`.

| Field | Meaning |
|---|---|
| `action` | The §24 action being priced |
| `score` | Weighted mean over present signals (`0..1`); `null` when nothing measurable was supplied |
| `level` | `low`/`medium`/`high` band of the score, or `unresolved` |
| `signals` | Gain terms per signal: agreement/coverage/confidence inputs are inverted into gap terms; absent inputs stay `null` |
| `unresolved` | Signals never supplied — dropped from the mean, never treated as zero |
