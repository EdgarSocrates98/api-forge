# EconomyPlan/v1

`EconomyPlan/v1` (`schema: apiforge/economy-plan/v1`) is attached to
`RoutingDecision.economy` and persisted as `economy.json` beside the routing
artifacts of a runtime run.

| Field | Meaning |
|---|---|
| `requested` / `requested_source` | Profile asked for and where it came from: `flag`, `manifest` or `policy` |
| `floor` | Minimum profile imposed by risk (complexity, task risk, gate state) |
| `effective` | `max(requested, floor)` — risk can escalate, never downgrade |
| `escalation_reason` | Risk signals that raised the profile, when it was raised |
| `envelope` | `BudgetEnvelope/v1` of the effective profile |
| `minimum_roles` | Role kinds required by risk and graph impact |
| `trimmed_roles` | Optional capabilities removed from the plan (parallel, fallbacks, challengers) |
| `escalation_reviewer` | Unused reviewer reserved for an L3 escalation, if any |
| `stop_when` | Deterministic stop conditions |
| `diagnostics` | e.g. `AF-ECONOMY-ESCALATED` |
