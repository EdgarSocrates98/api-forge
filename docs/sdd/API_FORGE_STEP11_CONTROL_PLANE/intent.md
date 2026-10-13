---
sdd: 1
feature: API_FORGE_STEP11_CONTROL_PLANE
phase: intent
profile: critical
status: done
risk_class: high
problem: a new decision system has no governed way to take over a route — no
  parallel-run record, no promotion criteria, no fallback when the active
  system degrades
success: routes declared in yaml move shadow→assisted→active one step at a
  time; shadow evals record candidate-vs-legacy differences while legacy
  governs; active promotion requires the five §31 requirements plus an
  approved ApprovalGate; degraded active routes route to their declared
  fallback or refuse AF-GOV-FALLBACK-MISSING; demotion is always allowed
out_of_scope:
  - runtime dispatch consulting evaluate_route per request (phase-6 wiring
    consumes RouteDecision)
  - automatic trigger detection from telemetry (callers declare triggers)
  - mutating the existing fail-closed decision gate
upstream:
  path: discover.md
  sha256: "697b9c85c885f626fc1626e11b10f996e2ed374f96395fb66c74d32a6285590c"
---

# intent
