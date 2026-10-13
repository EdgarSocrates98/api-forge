---
sdd: 1
feature: API_FORGE_RUNTIME_CONVERGENCE_HARDENING2
phase: discover
profile: critical
status: done
approaches:
  - id: runtime-rewrite
    summary: replace the existing runtime and planes with a new unified runtime
    verdict: refused -- violates the prompt's no-new-runtime rule and increases rollback risk
  - id: feature-islands
    summary: add isolated metrics and fixtures without changing execute_run
    verdict: refused -- does not close the capability-to-governing gap
  - id: governed-convergence
    summary: fix P0 semantic defects, then integrate existing planes through bounded adapters and receipts
    verdict: chosen -- preserves deterministic control, local-first evidence and rollback
chosen: governed-convergence
---

# discover

The phase-0 baseline, gap matrix and ownership matrix are recorded in
`docs/decisions/API_FORGE_HARDENING2_BASELINE.md`,
`docs/decisions/API_FORGE_HARDENING2_GAP_MATRIX.md` and
`docs/decisions/API_FORGE_HARDENING2_OWNERSHIP.md`. The implementation audit
confirmed that this is a convergence wave, not a greenfield feature wave.

