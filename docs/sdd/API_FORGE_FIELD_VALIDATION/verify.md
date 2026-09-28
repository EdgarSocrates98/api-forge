---
sdd: 1
feature: API_FORGE_FIELD_VALIDATION
phase: verify
profile: critical
status: draft
upstream:
  path: build.md
  sha256: "e83600af96e07f8b97f2b1aa9f4a4a8b92fd7122c6c922b2d4b3b11d0cba8c02"
results:
- gate: targeted tests field, workspace, mcp, agentops, contracts
  outcome: pass
  evidence: sdd/API_FORGE_FIELD_VALIDATION/evidence/field-tests.txt
- gate: pytest full suite
  outcome: fail
  evidence: sdd/API_FORGE_FIELD_VALIDATION/evidence/full-suite.txt
- gate: Ruff + mypy
  outcome: pass
  evidence: 'ruff: all checks passed; mypy: no issues in 452 source files'
---
# verify

Full suite: 1284 passed; the one failure is the release gate flagging the pre-existing untracked `.claude/agents/README.md` orphan mirror, not introduced here.

AT-001..AT-016 are mapped to tests under `tests/field/` and `tests/workspace/test_inference.py`. Precision/recall on the OpenTelemetry Demo is a cycle gate, not a build gate.
