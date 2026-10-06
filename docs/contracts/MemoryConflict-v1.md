# MemoryConflict/v1

`MemoryConflict/v1` records deterministic contradiction between two applicable,
trusted, fresh memory rows. `conflicting_paths` identifies disagreeing scalar
payload paths. `signals` preserves freshness, trust, evidence depth, outcome,
runtime compatibility, policy-version and source-authority inputs.

Outcomes: `prefer_a`, `prefer_b`, `review`, `quarantine` or `unresolved`.
`preferred_memory_id` and `conflicting_memory_id` name the preferred and losing
rows whenever the outcome is `prefer_*`; `admission_effect` states what the
retriever is allowed to do:

- `admit_preferred` — only the preferred row is served; the losing row stays in
  the conflict record (audit) but not in the result set.
- `review_only` — both rows stay visible and the result is `unresolved`;
  neither row may feed a decision.
- `exclude_both` — both rows are withheld. `risk=destructive` always resolves
  to `quarantine`/`exclude_both` before preference scoring: `prefer_*` is an
  advisory preference and never authorizes a destructive action.

No model or semantic provider required.

Canonical schema: `apiforge contract show MemoryConflict/v1`.
