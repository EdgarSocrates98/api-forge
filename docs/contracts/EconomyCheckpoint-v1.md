# EconomyCheckpoint/v1

`EconomyCheckpoint/v1` is `economy_checkpoint.json` in a runtime run directory, shown by `apiforge runtime checkpoint <task> <run>` (§104). `runtime run` writes it; `runtime resume` reads it, pins the profile and rewrites it with the cumulative spend.

| Field | Meaning |
|---|---|
| `requested` / `effective` | Profiles of the run; a resume keeps at least `effective` (`AF-ECONOMY-RESUME-PINNED` when a lower one is requested) |
| `max_calls` / `calls_used` / `calls_remaining` | Call budget and spend carried across resumes |
| `stopped_at` | Ladder level the run stopped at |
| `resumes` | How many times the run was resumed |
| `updated_at` | Clock of the last write |
| `status` / `codes` | `unresolved` with `AF-BUDGET-EXHAUSTED` when the budget is spent |
