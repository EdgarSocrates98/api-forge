# ForgeHandoff/v1

§46/§48 the portable cross-engine handoff bundle.

| Field | Meaning |
|---|---|
| `handoff_id` | `<task_id>-to-<engine>` |
| `from_engine`/`to_engine` | declared peers only (`AF-FORGE-ENGINE-UNKNOWN`) |
| `request`/`status` | embedded task + current projection |
| `evidence_refs`/`context_refs` | `path#sha256:` + `ctx://` pointers |
| `delivery` | always `prepared` — v1 never performs a live call |

Invariant: `unresolved` always names the human/transport delivery step —
the bundle proves packaging, never delivery.
