---
sdd: 1
feature: API_FORGE_EVALS_GOLDEN_HOLDOUT_C
phase: verify
profile: standard
status: done
upstream:
  path: build.md
  sha256: "a6b3169a9232dc050a098e442e3ae49692099e869362180607914bb9d7a765ba"
results:
  - gate: "pytest tests/evals/test_platform_suite.py"
    outcome: pass
    evidence: "3 passed"
  - gate: "apiforge evals validate"
    outcome: pass
    evidence: "4 cases, no invalid cases"
  - gate: "ruff check src/apiforge tests/evals"
    outcome: pass
    evidence: "All checks passed"
---

# verify

Casos de matriz, recusa por evidência ausente, score PASS e digest de holdout
foram verificados.
