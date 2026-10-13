---
sdd: 1
feature: API_FORGE_STEP11_AGENT_GOVERNOR
phase: ship
profile: critical
status: done
deviations:
  - "primitives emit decisions only; the runtime that consumes them arrives
    with the phase-5 decision control plane — wiring is deliberately not in
    this wave"
  - "the recovery policy ships with declared ladders per class; operators
    extend recovery_policy.yaml, unknown classes refuse rather than guess"
evidence:
  - docs/sdd/API_FORGE_STEP11_AGENT_GOVERNOR/evidence/G1.txt
  - docs/sdd/API_FORGE_STEP11_AGENT_GOVERNOR/evidence/G2.txt
  - docs/sdd/API_FORGE_STEP11_AGENT_GOVERNOR/evidence/G3.txt
rollback: revert this commit; the governor surface is additive — older code
  never imports src/apiforge/governance/ primitives or reads the new rules
upstream:
  path: benchmark.md
  sha256: "6020e2b16b88658ce5670b2d4ba19a1ca18f7a1d0a54af9562fae71021484db5"
---

# ship
