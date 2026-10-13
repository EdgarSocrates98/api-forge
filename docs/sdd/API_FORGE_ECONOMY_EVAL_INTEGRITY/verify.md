---
sdd: 1
feature: API_FORGE_ECONOMY_EVAL_INTEGRITY
phase: verify
profile: critical
status: draft
upstream:
  path: build.md
  sha256: "5d7d0ed041b4166f88028959e1743889bf997fe8460fa6c3d978589ecb65f282"
results:
- gate: pytest full suite
  outcome: pass
  evidence: sdd/API_FORGE_ECONOMY_EVAL_INTEGRITY/evidence/eval-integrity-tests.txt
- gate: economy-hardening eval
  outcome: pass
  evidence: sdd/API_FORGE_ECONOMY_EVAL_INTEGRITY/evidence/economy-hardening-eval.json
- gate: agentic-quality eval
  outcome: pass
  evidence: sdd/API_FORGE_ECONOMY_EVAL_INTEGRITY/evidence/agentic-quality-eval.json
- gate: Ruff + mypy + release gate
  outcome: pass
  evidence: 'mypy: no issues in 439 source files; release gate PASS'
---
# verify

An all-wrong corpus now fails; a mutated `plan_roles` fails the hardening eval; `../secret.py` passed as `--changed` is never opened.
