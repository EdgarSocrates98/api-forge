# EvidenceRef/v1

Typed, non-authoritative reference to an evidence artifact. The reference
identifies provenance without upgrading a declaration, observation or receipt
into a verification claim.

| Field | Shape | Meaning |
|---|---|---|
| `ref` | `str` | Stable local artifact or receipt reference |
| `kind` | `trace \| receipt \| evaluation \| fixture \| policy \| rollback \| knowledge` | Evidence category |
| `level` | `observed \| declared \| inferred \| heuristic \| verified \| unknown` | Strength of the claim |
| `limitations` | `tuple[str, ...]` | Explicit limits on interpretation |

This contract is descriptive only. It does not grant execution, provider or
external mutation authority.
