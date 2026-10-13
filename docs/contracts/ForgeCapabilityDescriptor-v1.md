# ForgeCapabilityDescriptor/v1

§46 public capability projection — the `CapabilityRecord` row exposed on the
Forge wire so another engine can discover what API Forge offers.

| Field | Meaning |
|---|---|
| `capability_id`/`operation` | stable public identifier and verb |
| `state` | `supported`/`heuristic`/`unresolved`/`unsupported` — honest support level |
| `risk` | `read_only`/`local_reversible`/`sensitive`/`external_mutation` |
| `surfaces`/`evidence`/`limitations` | where it runs and what proves it |

Invariant: never upgraded — a `heuristic` capability stays `heuristic` on
the wire.
