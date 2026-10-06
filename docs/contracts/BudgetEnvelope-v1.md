# BudgetEnvelope/v1

`BudgetEnvelope/v1` holds the hard execution limits of one economy profile,
loaded from `src/apiforge/rules/economy_profiles.yaml`.

| Field | Meaning |
|---|---|
| `profile` | `economy`, `balanced` or `deep` |
| `provider_calls` | Upper bound on agent calls; the supervisor uses `min(policy, TaskSpec, envelope)` |
| `fanout` | Parallel specialist slots kept in the plan |
| `fallbacks` | Sequential fallbacks kept in the plan |
| `debate_rounds` | Rounds allowed when a debate room opens (0 disables non-forced debate) |
| `challenger_slots` | Challenger slots kept in the plan |
| `verification_share` | Share of calls reserved for escalation review (never spent on investigation) |
| `ladder_ceiling` | Highest escalation level the profile may reach without risk forcing it |
| `on_exhaustion` | Always `unresolved` |
| `silent_downgrade` | Always `false` — rejected at validation if set |
