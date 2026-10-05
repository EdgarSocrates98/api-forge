---
sdd: 1
feature: API_FORGE_EVO_CONVERGENCE
phase: ship
profile: critical
status: draft
deviations:
  - id: external-freshness
    status: unresolved
    reason: vulnerability databases, provider freshness and deployment safety require external evidence
  - id: merge-automation
    status: pending
    reason: push, CI, PR and automatic merge are separate host-controlled gates
evidence:
  - path: sdd/API_FORGE_EVO_CONVERGENCE/evidence/baseline.md
  - path: sdd/API_FORGE_EVO_CONVERGENCE/evidence/p0-agentops.md
  - path: sdd/API_FORGE_EVO_CONVERGENCE/evidence/runtime-governance.md
  - path: sdd/API_FORGE_EVO_CONVERGENCE/evidence/retrieval-memory.md
  - path: sdd/API_FORGE_EVO_CONVERGENCE/evidence/protocol-supply-chain.md
upstream:
  path: benchmark.md
  sha256: "a2952410bc5583e568aee1912aae909ad3dbcec9a55a0968e3c7bf474bde2d5e"
---

# ship

Ship is conditional on local verification, a clean policy gate and external
CI evidence. The final Outcome Brief will list every unresolved state and will
not convert a pending merge or external scanner into a success claim.
