---
sdd: 1
feature: API_FORGE_ECONOMY_FRESHNESS_RESUME
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "b6c5ab272f76c97eaac9a889547f3a8a682ca32956b754b7dac9124dbde44fdf"
problem: 'Stale knowledge was detected one pack at a time, live evidence had no gate, an inconclusive
  test had no declared next step and a resumed run re-resolved its profile without its prior spend.'
success:
- freshness-watch
- live-evidence-gate
- progressive-verification
- phase-budgets
- resume-checkpoint
- freshness-eval
out_of_scope:
- fetching-upstream-sources
- executing-live-adapters
- scheduling-watches
owner: api-forge-economy
risk_class: low
risk_signals:
- path:src/apiforge/runtime/supervisor.py
- path:src/apiforge/evidence/live_gate.py
---
# intent

Pay for refresh, live evidence and escalation only when the cheaper answer is stale or inconclusive, and never let a resume forget what it already spent.
