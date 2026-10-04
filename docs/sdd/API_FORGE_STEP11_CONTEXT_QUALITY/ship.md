---
sdd: 1
feature: API_FORGE_STEP11_CONTEXT_QUALITY
phase: ship
profile: critical
status: ready
upstream:
  path: benchmark.md
  sha256: "df110b6617429c56787e3f99d710061f0a485aced79db225e55839be5c5d353b"
deviations: []
evidence:
  - path: sdd/API_FORGE_STEP11_CONTEXT_QUALITY/evidence/G1.txt
    sha256: "d577f2061e6e3ad307d8cb62d06d77998cee53c6c5f155024fd0e7c7da1a21ca"
  - path: sdd/API_FORGE_STEP11_CONTEXT_QUALITY/evidence/G2.txt
    sha256: "9c55917a1b5576585b9e517dc3402224f46769f0978ce812e94933c195f4afff"
  - path: sdd/API_FORGE_STEP11_CONTEXT_QUALITY/evidence/G3.txt
    sha256: "8f16aa65c3474b5c0f81d87f8e2c3fd58b219baf7e249fa1f096a895c14f53be"
rollback: >
  revert the feature commit; v1 role_context.yaml remains valid and no
  persisted artifact format changed (the run ledger and ctx store are
  untouched).
---

# ship

Phase 1 of `prompt_evo_step11.md`: Context Quality Engine, Minimum Sufficient
Context and RoleContext v2.

- contracts: ContextUseRecord, ContextQualityMetric, ContextQualityReport,
  ContextSufficiencyResult, RoleContextPolicy, RoleContextQuality,
  RoleContextTelemetry (all v1, registered)
- engine: `context/quality.py` + `context/sufficiency.py` + `context quality`
  verb + `evals context-quality`
- role v2: `rules/role_context.yaml` `policies:` block + enforcement inside
  `plan_roles` with cataloged AF notes
- unresolved honesty: every metric states its basis; nothing is estimated
  silently
