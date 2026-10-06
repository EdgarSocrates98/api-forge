# TrustedRef/v1

A `ContextRef` paired with its `TrustUnit` annotation. The ref payload is
unchanged; trust travels beside it.

| Field | Meaning |
|---|---|
| `ref` | The original `ContextRef` (ctx:// content address, kind, origin, span) |
| `trust` | The `TrustUnit` derived from `REF_ORIGIN_MAP` + the ref's provenance/freshness |

`annotate_ref`/`annotate_capsule` produce these; v1 `ContextCapsule` payloads
stay byte-identical, so older consumers are unaffected.
