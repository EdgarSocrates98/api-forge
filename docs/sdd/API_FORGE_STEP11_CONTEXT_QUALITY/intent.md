---
sdd: 1
feature: API_FORGE_STEP11_CONTEXT_QUALITY
phase: intent
profile: critical
status: done
risk_class: high
upstream:
  path: discover.md
  sha256: "4f3e248671faf630d28b709f306f0d4a62c86bcafdf7de9525c7e39b541d00bc"
problem: >
  Context economy is measured in bytes but never in quality: there is no
  metric for whether the selected context was used, recalled, duplicated,
  stale or sufficient, and role budgets cannot declare required/denied kinds,
  visibility, provenance floors or evidence requirements.
success:
  - context-quality-contracts
  - context-quality-engine
  - minimum-sufficient-context
  - role-context-v2
  - context-quality-evals
out_of_scope: >
  Live-model context evaluation, semantic/vector scoring, and any trust plane
  taxonomy beyond deterministic provenance rank (phase 2 scope).
---

# intent

Deliver a measured context-quality plane:

1. Registered closed contracts: `ContextUseRecord`, `ContextQualityMetric`,
   `ContextQualityReport`, `ContextSufficiencyResult`, `RoleContextPolicy`,
   `RoleContextQuality`, `RoleContextTelemetry`.
2. `context/quality.py`: the full 13-metric catalog, every metric carrying an
   `observed|estimated|unresolved` basis — unresolved metrics carry no value.
3. `context/sufficiency.py`: deterministic prune -> re-measure -> compare with
   `strict|evidence|permissive` gates.
4. `rules/role_context.yaml` v2 `policies:` block parsed into
   `RoleContextPolicy` contracts and enforced in `plan_roles`; v1 files keep
   loading unchanged.
5. `evals context-quality` corpus + `context quality --capsule --run-id` verb.
