# SemanticCheckpoint/v1

`SemanticCheckpoint/v1` is resumable state, not transcript compaction. It
records the objective, accepted/rejected decisions, still-valid facts,
assumptions, unresolved gaps, working set, artifact/memory refs, tool/routing/
budget/risk state and next actions. `equivalent()` compares effective state
without identity or timestamp so a fresh process can prove a safe round trip.

