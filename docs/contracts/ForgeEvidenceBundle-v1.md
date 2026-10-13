# ForgeEvidenceBundle/v1

§46 the portable evidence set for a task — forge + governed artifacts with
their digests.

| Field | Meaning |
|---|---|
| `task_id` | owner |
| `artifacts` | `ForgeEvidenceArtifact` rows |
| `produced_at` | ISO-8601 stamp |
| `unresolved` | missing artifacts and broken links, named |

Invariant: the bundle carries addresses, not interpretations — consumers
verify by hash.
