---
sdd: 1
feature: API_FORGE_ECONOMY_ARCH_HARDENING
phase: discover
profile: critical
status: draft
approaches:
- id: invariants-in-contracts
  summary: one source resolver, one case reader, validators for budgets and accounting, structured proofs
  verdict: chosen -- guarantees live in code; removes duplicated loaders
- id: guard-at-the-edges
  summary: post-filter capsule and evidence output
  verdict: refused -- keeps the duplicated case loader and invalid contract states
- id: rewrite-with-budget-ledger
  summary: new unified budget service and rebuilt gateway
  verdict: refused -- re-architecture, high regression risk
chosen: invariants-in-contracts
---
# discover

Source: `prompt_evo_new_economy_arch.md`, an external review of the economy program (verdict `REVIEW`): four P1 and ten P2/P3 findings on trust boundaries, budget invariants, accounting completeness and proof semantics.
