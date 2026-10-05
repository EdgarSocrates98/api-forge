# MemoryConflict/v1

`MemoryConflict/v1` records deterministic contradiction between two applicable,
trusted, fresh memory rows. `conflicting_paths` identifies disagreeing scalar
payload paths. `signals` preserves freshness, trust, evidence depth, outcome,
runtime compatibility, policy-version and source-authority inputs.

Outcomes: `prefer_a`, `prefer_b`, `review`, `quarantine` or `unresolved`.
Review remains visible in read-only retrieval; destructive retrieval excludes
both rows and returns `quarantine`. No model or semantic provider required.

Canonical schema: `apiforge contract show MemoryConflict/v1`.
