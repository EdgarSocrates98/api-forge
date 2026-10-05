---
sdd: 1
feature: API_FORGE_STEP11_CONTEXT_QUALITY
phase: architecture
profile: critical
status: done
upstream:
  path: contract.md
  sha256: "1b8822a6b5c6fe644607e8ed81659a6f059b558af44604adc9a4cb6be51be917"
files:
  - src/apiforge/contracts/context_quality.py
  - src/apiforge/contracts/registry.py
  - src/apiforge/context/quality.py
  - src/apiforge/context/sufficiency.py
  - src/apiforge/context/role_policy.py
  - src/apiforge/runtime/role_context.py
  - src/apiforge/rules/role_context.yaml
  - src/apiforge/application/context.py
  - src/apiforge/cli_context.py
  - src/apiforge/cli.py
  - src/apiforge/evals/context_quality.py
  - evals/corpus/context-quality/
  - tests/context/test_quality.py
  - tests/context/test_sufficiency.py
  - tests/context/test_role_policy.py
decisions:
  - metrics are derived only from recorded inputs (capsule refs, use records,
    caller-declared required sets and cache counters); any missing denominator
    yields an unresolved metric with no value
  - use records are produced by replaying the measured run ledger instead of a
    parallel telemetry stream
  - required_kinds means delivery priority plus a violation only when the kind
    existed in the capsule but never arrived; absent kinds conjure nothing
  - minimum trust is provenance rank derived from ContextRef.origin, never a
    model-asserted score
---

# architecture

`context quality --capsule <recorded.json> --run-id <id>` loads a
`ContextCapsule/v1`, replays the run ledger into `ContextUseRecord`s
(`context *` -> loaded, `runtime role:<role>` -> assigned, `context expand` ->
expanded), evaluates the 13-metric catalog and runs the deterministic
minimum-sufficient pass in the same call. Per-role telemetry is emitted
alongside the report.

`plan_roles` keeps the v1 class shares untouched; the v2 policy layer filters
the class-eligible refs (denied kinds, origin rank floor), orders required
kinds first inside the same budget and emits explicit unresolved notes with
`AF-*` codes instead of silently degrading.
