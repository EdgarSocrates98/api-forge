# ForgeTaskStatus/v1

§46 the wire-visible state of a submitted task and its governed link.

| Field | Meaning |
|---|---|
| `state` | `received`/`accepted`/`in_progress`/`completed`/`failed`/`refused`/`unresolved` |
| `governed_task_id`/`governed_state` | linked TaskSpec + its verbatim state |
| `revision`/`updated_at` | last persisted transition |
| `unresolved` | broken links or absent data — named, never inferred |

Invariant: `inspect` projects live governed state — the small wire
lifecycle never hides the real `governed_state`.
