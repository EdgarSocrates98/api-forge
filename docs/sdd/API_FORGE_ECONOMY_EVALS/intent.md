---
sdd: 1
feature: API_FORGE_ECONOMY_EVALS
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "5005719a8c8b08522fc57c5ce0ac3145a286d88f3097e931450fd8de291751ec"
problem: No multi-axis profile comparison on canonical tasks, no gate against safety regression, no replay
  of stored runs, no ROI of extra agents and no quality floor in routing.
success:
- economy-matrix
- holdout-mutation
- evaluation-gate
- replay
- role-roi
- information-gain
- quality-floor
out_of_scope:
- llm-judged-quality
- monetary-cost-axis
- external-api-corpus
owner: api-forge-economy
risk_class: medium
risk_signals:
- path:src/apiforge/runtime/scorecard_routing.py
- path:src/apiforge/rules/agent_profiles.yaml
- path:src/apiforge/runtime/supervisor.py
---
# intent

Measure every profile on the same canonical API changes with quality as a constraint, and let an economy change ship only when quality and safety do not regress.
