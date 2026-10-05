# ModelRouteInputs/v1

§33 the declared inputs for a model routing decision — model routing stays
separate from capability and agent routing.

| Field | Meaning |
|---|---|
| `task_complexity` / `risk` / `reasoning_needs` | Task shape; `reasoning_needs` is `none`/`light`/`deep` |
| `context_size` | Tokens the task needs; a smaller `context_window` makes the candidate ineligible |
| `needs_tool_support` / `needs_structured_output` | Hard requirements — not preferences |
| `max_latency_ms` / `max_cost` | Declared ceilings candidates may not cross |
| `budget_remaining` | Declared leftovers; absent values land in `unresolved` |

Absent signals are named in `ModelRouteDecision.unresolved`, never inferred.
