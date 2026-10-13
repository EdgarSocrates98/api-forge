# ForgeEvidenceArtifact/v1

One content-addressed artifact inside a `ForgeEvidenceBundle`.

| Field | Meaning |
|---|---|
| `path` | repo-relative path |
| `sha256` | file digest — the address |
| `kind` | `request`/`status`/`ledger`/`governed` |

Invariant: every carried artifact is hashed; a missing declared artifact
lands in the bundle's `unresolved`.
