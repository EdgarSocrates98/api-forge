---
sdd: 1
feature: API_FORGE_ECONOMY_FRESHNESS_RESUME
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "72ef6f21bfd369e99cbce033e28e295d8c7897fc69266645ab1ffe760090b9aa"
files:
- src/apiforge/contracts/economy_resume.py
- src/apiforge/knowledge/watch.py
- src/apiforge/evidence/live_gate.py
- src/apiforge/rules/live_evidence_triggers.yaml
- src/apiforge/verification/progressive.py
- src/apiforge/economy/phase_budget.py
- src/apiforge/rules/phase_budgets.yaml
- src/apiforge/runtime/economy_checkpoint.py
- src/apiforge/runtime/supervisor.py
- src/apiforge/cli_resume.py
- src/apiforge/evals/freshness_resume.py
decisions:
- id: manifest-read-only
  decision: the watch reads a local upstream manifest; it never fetches or rewrites a pack
  rollback: none needed
- id: runtime-terms-gate-live
  decision: live_read_only only when the question names a runtime effect; live_mutation refused
  rollback: none needed
- id: escalation-table-in-code
  decision: six fixed transitions; ladder stops at live_read_only
  rollback: none needed
- id: protected-phases
  decision: contract, verify and secure get a floor and are never cut
  rollback: edit rules/phase_budgets.yaml
- id: resume-pins-profile
  decision: resume keeps at least the checkpoint profile and carries calls used
  rollback: delete economy_checkpoint.json
---
# architecture

Four read-only modules behind verbs; the supervisor writes the checkpoint after a run and reads it on resume.
