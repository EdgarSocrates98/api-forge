---
sdd: 1
feature: API_FORGE_AGENT_ROSTER
phase: verify
profile: critical
status: draft
upstream:
  path: build.md
  sha256: "8d60913590cb7911ee5d007ba166ffb91cab14f355f752008370304104101c47"
results:
- gate: agents lint (25 agents, tools exist, playbooks coherent)
  outcome: pass
  evidence: sdd/API_FORGE_AGENT_ROSTER/evidence/lint.json
- gate: agents audit 25/25 keep
  outcome: pass
  evidence: sdd/API_FORGE_AGENT_ROSTER/evidence/audit.json
- gate: routing eval golden vs baseline
  outcome: pass
  evidence: sdd/API_FORGE_AGENT_ROSTER/evidence/routing-candidate.json
- gate: routing eval independent holdout vs baseline
  outcome: pass
  evidence: sdd/API_FORGE_AGENT_ROSTER/evidence/holdout-candidate-25.json
- gate: agentic-quality against previous baseline
  outcome: pass
  evidence: sdd/API_FORGE_AGENT_ROSTER/evidence/agentic-quality.json
- gate: economy-hardening
  outcome: pass
  evidence: sdd/API_FORGE_AGENT_ROSTER/evidence/economy-hardening.json
- gate: pytest full suite
  outcome: fail
  evidence: sdd/API_FORGE_AGENT_ROSTER/evidence/full-suite.txt
---
# verify

Golden: top-1 0.7333 -> 0.9733, top-3 0.92 -> 1.0, protected misroutes 5 -> 0, but 25% of golden cases share a 4-gram with their agent and the baseline was mostly Portuguese, so the golden gain is confounded. Independent holdout (80 cases by two other models, labels from names only, leakage 0): top-1 0.2875 -> 0.4625, top-3 0.4875 -> 0.65, protected misroutes 13 -> 9. The proxy router is weak in absolute terms; the relative gain holds. The only full-suite failure is the pre-existing untracked `.claude/agents/README.md`.
