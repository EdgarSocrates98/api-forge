---
sdd: 1
feature: API_FORGE_ANALYTICAL_DATA_SPECIALIZATION_5
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "5fa9f3b1e02175a2ed4389f3c7d6f1cc58879f06751d25bf8bc97a79dccafe96"
results:
  - gate: pytest tests/adapters/test_analytical.py -q
    outcome: pass
    evidence: 2 passed
  - gate: ruff, mypy and release gate
    outcome: pass
    evidence: evidence/analytical-tests.txt
---
# verify

Busca, aggregation, paginação e partição são preservadas como sinais.
