# GovernorDecision/v1

§23 ceilings a run must respect: the effective profile is
`max(declared profile, risk floor)` — never lowered.

| Field | Meaning |
|---|---|
| `profile` / `risk` | The effective profile and declared risk |
| `max_agents` / `max_reviewers` / `max_debates` / `max_retries` / `max_replans` | Orchestration ceilings |
| `max_tokens` / `max_cost` | Numeric caps; `null` means the policy row set none (and no budget clamp applied) |
| `allowed_execution_modes` | `deterministic`/`sandbox`/`provider` subset after security clamps |
| `allowed_tools` | Tool-risk labels the run may use |
| `clamped_by` | Every clamp applied (`risk:…`, `security:…`, `budget:…`) |
| `unresolved` | Input signals the caller did not supply — named, never guessed |
