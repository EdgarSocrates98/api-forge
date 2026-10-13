# MemoryQuery/v1

`MemoryQuery/v1` is an explicit bounded retrieval request. It carries terms,
scopes, exact or structured environment compatibility, minimum trust, freshness
clock, invalidation visibility, configurable minimum term coverage and a
maximum result count. Missing clocks or environment mismatch remain visible as
unresolved retrieval state. A default coverage of `0.5` gives an OR-like
search while callers can require `1.0` for all terms.

Structured `runtime` matching evaluates `runtime_requirements` and
`runtime_constraints` directly; query terms never satisfy runtime constraints.
`risk` + `stale_handling` govern stale/expired memory: read-only can include,
sensitive can require review, destructive excludes it. Tainted records remain
excluded unless `include_tainted=true`. Conflict detection defaults on.

Canonical schema: `apiforge contract show MemoryQuery/v1`.
