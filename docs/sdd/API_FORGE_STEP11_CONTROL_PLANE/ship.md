---
sdd: 1
feature: API_FORGE_STEP11_CONTROL_PLANE
phase: ship
profile: critical
status: done
deviations:
  - "evaluate_route emits decisions; the per-request wiring that consults
    RouteDecision arrives with the phase-6 router — this phase ships the
    lifecycle, not the dispatcher"
  - "trigger detection is explicit (callers declare triggers or use control
    triggers to map signals); automatic detection from telemetry is left
    unresolved"
evidence:
  - docs/sdd/API_FORGE_STEP11_CONTROL_PLANE/evidence/G1.txt
  - docs/sdd/API_FORGE_STEP11_CONTROL_PLANE/evidence/G2.txt
  - docs/sdd/API_FORGE_STEP11_CONTROL_PLANE/evidence/G3.txt
rollback: "revert this commit; modes/shadow ledgers are additive-only data —
  older code never opens .apiforge/control-plane/"
upstream:
  path: benchmark.md
  sha256: "9d5dc8df015b0d48e12854778e3f52a8bddcf29debe94938ac2f8c3d5d522e4a"
---

# ship
