# ToolDisclosure/v1

§41 task → capability router → active tool set (advisory; the host decides
what it actually loads).

| Field | Meaning |
|---|---|
| `task`/`task_class` | input task and the declared class routed to |
| `active_tools` | tools the declared class needs on this surface |
| `dropped_tools` | the rest of the surface |
| `basis` | `declared-policy` or `fallback-full` |
| `unresolved` | unknown declared names, unclassified tasks, off-surface tools |

Invariant: unclassified tasks fall back to the full surface and say so —
disclosure never silently narrows.
