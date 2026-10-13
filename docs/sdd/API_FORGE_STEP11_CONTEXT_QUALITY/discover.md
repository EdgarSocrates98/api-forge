---
sdd: 1
feature: API_FORGE_STEP11_CONTEXT_QUALITY
phase: discover
profile: critical
status: done
approaches:
  - id: metrics-in-context-result
    summary: add quality fields onto ContextResult/ContextCapsule v1 contracts
    verdict: refused -- mutating frozen v1 contracts breaks backward compatibility
      and mixes transport shape with a measurement plane
  - id: ledger-only-counters
    summary: derive quality ad hoc inside economy report
    verdict: refused -- couples measurement to a different plane and hides the
      metric vocabulary from contracts and evals
  - id: context-quality-plane
    summary: new contracts + pure engine over capsule refs and recorded uses,
      metrics emitted with an explicit observed/estimated/unresolved basis
    verdict: chosen -- deterministic, additive, honest about missing inputs
chosen: context-quality-plane
---

# discover

`prompt_evo_step11.md` phase 1 asks for a Context Quality Engine
(`ContextQualityReport`, `ContextQualityMetric`, `ContextUseRecord`,
`ContextSufficiencyResult`), Minimum Sufficient Context evaluation and
RoleContext v2 policies with per-role telemetry.

The repository already ships `ContextCapsule`/`ContextRef`, the run ledger
(which records capsule admissions, `runtime role:<role>` assignments and
`context expand` rows) and `rules/role_context.yaml` v1 classes. The gap is a
named metric plane that turns those recorded rows into measured quality and a
deterministic minimum-sufficient decision.

Baseline: `docs/decisions/API_FORGE_STEP11_GAP_MATRIX.md` (1436 passed,
2 skipped on `main` at `7e75723`).
