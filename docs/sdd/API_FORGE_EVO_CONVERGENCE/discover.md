---
sdd: 1
feature: API_FORGE_EVO_CONVERGENCE
phase: discover
profile: critical
status: done
approaches:
  - id: big-bang-runtime-rewrite
    summary: replace the existing runtime and all planes in one change
    verdict: refused -- violates backward compatibility, evidence boundaries and rollback
  - id: feature-islands
    summary: add isolated capabilities without making execute_run use them
    verdict: refused -- the prompt prioritizes integration over feature count
  - id: governed-convergence
    summary: fix correctness first, then integrate existing primitives through small adapters, shadow records and explicit receipts
    verdict: chosen -- preserves the deterministic core and makes every promotion reversible
chosen: governed-convergence
---

# discover

The baseline and gap matrix are recorded in
`docs/decisions/API_FORGE_EVO_CONVERGENCE_BASELINE.md` and
`docs/decisions/API_FORGE_EVO_CONVERGENCE_GAP_MATRIX.md`. The repository is a
large, already-evolved platform; the primary risk is divergence between
standalone primitives and the real execution path.

