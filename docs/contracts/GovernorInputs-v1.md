# GovernorInputs/v1

The declared inputs for an §23 governor decision (step11 phase 4).

| Field | Meaning |
|---|---|
| `profile` | `economy`, `balanced` or `deep` — the declared preference |
| `risk` | `DecisionRisk` — the risk floor, never lowered |
| `confidence` / `evidence_completeness` / `context_sufficiency` | Optional `0..1` signals; absent values land in `GovernorDecision.unresolved` |
| `budget_remaining` | Declared leftovers; `observed_tokens`/`cost`/`calls` clamp ceilings |
| `security_state` | `clean`, `tainted` or `quarantined` — applies declared clamps |
| `task_complexity` | Optional `micro`/`low`/`medium`/`high` |
