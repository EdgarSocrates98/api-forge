# ForgeTaskResult/v1

§46 the outcome projection of a forge task — the governed `OutcomeBrief`
mapped to the wire.

| Field | Meaning |
|---|---|
| `status` | `ok`/`review`/`blocked`/`failed`/`unresolved` |
| `payload` | outcome, subject, governed_task_id, human_action when pending |
| `evidence`/`gaps`/`limitations` | proof refs and named gaps |
| `error_code` | `AF-*` when the projection itself fails |

Invariant: no governed link or no brief means `unresolved` — never a
fabricated `ok`.
