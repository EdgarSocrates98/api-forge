---
sdd: 1
feature: API_FORGE_STEP11_CONTEXT_QUALITY
phase: contract
profile: critical
status: done
upstream:
  path: intent.md
  sha256: "dd66f8b1cbc2b8d5717e01d2d9e50d8732f9bbdb48c7f37ddf33070969c0a09a"
covers:
  - context-quality-contracts
  - context-quality-engine
  - minimum-sufficient-context
  - role-context-v2
  - context-quality-evals
---

# contract

- `ContextUseRecord/v1` — one recorded ref interaction: `loaded`, `assigned`,
  `expanded`, `cited`, `artifact`; tokens only `observed` from transcripts.
- `ContextQualityMetric/v1` — closed `ContextMetricKind` catalog (14 metrics),
  `basis` enforced: unresolved metrics carry no value, observed metrics
  require one.
- `ContextQualityReport/v1` — must emit every metric kind; status
  `ready|degraded|unresolved` follows the unresolved-metric count.
- `ContextSufficiencyResult/v1` — kept/pruned refs, pruned bytes, before/after
  metric snapshots, gate and an explicit `sufficient` flag.
- `RoleContextPolicy/v1` — required/denied kinds, visibility levels
  (`none|summary|full`) for memory/knowledge/artifact, tool allowlist,
  deterministic `minimum_origin_rank`, byte/token caps, `required_evidence`.
- `RoleContextTelemetry/v1` — per-role loaded/expanded/cited/tokens/evidence/
  cache/duplicates/unused counters.

Refusals (cataloged): `AF-CONTEXT-QUALITY-CAPSULE`,
`AF-CONTEXT-QUALITY-GATE`, `AF-ROLE-CONTEXT-DENIED`, `AF-ROLE-CONTEXT-TRUST`,
`AF-ROLE-CONTEXT-REQUIRED`, `AF-ROLE-CONTEXT-TOOL`.
