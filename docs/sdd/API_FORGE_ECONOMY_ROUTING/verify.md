---
sdd: 1
feature: API_FORGE_ECONOMY_ROUTING
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "c463bf1dc14f0b72e9a8cf6b8b42c7173eb711b02aac494168f1284a562a06b2"
results:
  - gate: targeted tests
    outcome: pass
    evidence: sdd/API_FORGE_ECONOMY_ROUTING/evidence/economy-routing-tests.txt
  - gate: economy-routing eval
    outcome: pass
    evidence: sdd/API_FORGE_ECONOMY_ROUTING/evidence/economy-routing-eval.json
  - gate: pytest full suite
    outcome: pass-with-preexisting-gap
    evidence: "1109 passed, 1 skipped; release gate reports only the pre-existing untracked orphan .claude/agents/README.md"
  - gate: Ruff
    outcome: pass
    evidence: ruff check src tests; ruff format --check src tests
  - gate: mypy
    outcome: pass
    evidence: "Success: no issues found in 382 source files"
---
# verify

All 15 acceptance tests map to `tests/runtime/test_economy_plan.py`,
`tests/runtime/test_economy_supervisor.py`, `tests/contracts/test_economy_routing_contracts.py`,
`tests/sdd/test_risk_classify.py` and `tests/evals/test_economy_routing_eval.py`.
The corpus gates (role invariant, effective profile, critical ⇒ deep, economy
cheaper for low risk) pass on 15/15 cases; critical cases are review-blocked
before routing and report no call counts.
