---
sdd: 1
feature: API_FORGE_ECONOMY_SELECTIVE_AGENTICS
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "c42d1a62639f0f5ece3ad68d6b943a454928ab8d037e9bb169ed4ec2932d2bd1"
problem: Subagents inherit the full task context, expertise is not selected, debates replicate essays
  to the referee, challengers are never measured and nothing flags agents without unique capability.
success:
- lazy-expertise
- role-context
- position-deltas
- referee-packet
- bounded-shadow
- agent-audit
- selective-eval
out_of_scope:
- reviewer-roi-learning
- prompt-compiler
- automatic-agent-removal
owner: api-forge-economy
risk_class: medium
risk_signals:
- path:src/apiforge/runtime/supervisor.py
- path:src/apiforge/runtime/role_context.py
- path:src/apiforge/debate/service.py
---
# intent

Give every agent the minimum evidence for its role, load expertise only on trigger, exchange debate deltas over one capsule and learn from challengers without paying for them on every run.
