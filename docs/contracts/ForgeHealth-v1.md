# ForgeHealth/v1

§46 engine health over the wire.

| Field | Meaning |
|---|---|
| `engine`/`protocol_version` | declared identity from `rules/forge_protocol.yaml` |
| `state` | `ok`/`degraded` — degraded when a stored row is corrupt |
| `capabilities` | public matrix size |
| `tasks_by_state` | live counts per forge state |

Invariant: counts are measured from the store, not remembered.
