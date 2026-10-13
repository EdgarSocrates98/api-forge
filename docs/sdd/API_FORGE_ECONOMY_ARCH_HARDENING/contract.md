---
sdd: 1
feature: API_FORGE_ECONOMY_ARCH_HARDENING
phase: contract
profile: critical
status: draft
upstream:
  path: intent.md
  sha256: "cc06eca4a2585a3f65d5abeaa32c5882c2c75015837a63ad41451430ecbd4a83"
covers:
- ProofReceipt/v1
- RoleContextPlan/v1
- ShadowDecision/v1
- PhaseBudgetPlan/v1
- EconomyMatrix/v1
- EvidenceNode/v1
- DeltaSlice/v1
api_ir:
  input: case directories, fact/graph paths, workspace manifest, role mixes, ledger rows, task run steps, cache entries, knowledge packs
  output: refused refs, bounded role plans, accounted calls, token coverage, L0/L1 decisions, statuses and scoped eval reports
---
# contract

Additive only: `RoleContext.pool_bytes` + validators, `ShadowDecision.mode`, `PhaseBudgetPlan.quality_status`/`budget_status`, `EconomyMatrix.claim_scope`, `EvidenceNode.unresolved`, `DeltaSlice.status: degraded`, `CacheEntry` timestamp validation and the new `ProofReceipt/v1`.
