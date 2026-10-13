---
sdd: 1
feature: API_FORGE_OBSERVABILITY_PROVIDER_QUERY_BUILDERS_M
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "25c8e7c4b407ec810affc0777fc7262f74627d70b5b506e6ccbf63c574fedb75"
results:
  - gate: pytest tests/observability
    outcome: pass
    evidence: 29 passed
  - gate: ruff and mypy
    outcome: pass
    evidence: all checks passed
---
# verify

Os builders geram parâmetros específicos sem incluir credenciais ou executar chamadas externas.
