---
sdd: 1
feature: API_FORGE_AGENTIC_PLATFORM
phase: verify
profile: critical
status: draft
upstream:
  path: build.md
  sha256: "85bf9f7b8063774b1ef0db2b5118956dbb115c09e14195296200e01107e93093"
results:
  - gate: "pytest tests/contracts tests/taskspec"
    outcome: pass
    evidence: "36 passed"
  - gate: "pytest -q"
    outcome: pass
    evidence: "390 passed, 1 skipped (optional mcp extra)"
  - gate: "ruff check ."
    outcome: pass
    evidence: "All checks passed"
  - gate: "mypy src"
    outcome: pass
    evidence: "no issues found in 117 source files"
  - gate: "python scripts/check_release.py"
    outcome: pass
    evidence: "API Forge release gate: PASS"
---

# verify

Spec A+B verified: 390 tests pass, 1 skip is the optional `mcp` extra.
Evidence captures under `evidence/` record the pytest output per task.
