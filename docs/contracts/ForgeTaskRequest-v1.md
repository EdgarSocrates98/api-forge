# ForgeTaskRequest/v1

§46 a task submitted over the Forge wire — intent plus declared
constraints, frozen at submit.

| Field | Meaning |
|---|---|
| `task_id` | `^[a-z0-9][a-z0-9-]{1,62}$`, unique under `.apiforge/forge/tasks/` |
| `capability_id`/`intent` | what to call and what it must achieve |
| `inputs` | frozen JSON object — never reinterpreted |
| `budgets` | governed `Budgets` (calls/rounds/deadline) |
| `risk` | `CapabilityRisk`; gated classes need `--acknowledge-risk` |
| `origin_engine`/`requested_by`/`requested_at` | provenance |

Invariant: immutable once persisted — updates create status events, never
rewrite the request.
