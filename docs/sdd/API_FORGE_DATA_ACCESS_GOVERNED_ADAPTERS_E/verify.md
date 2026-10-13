---
sdd: 1
feature: API_FORGE_DATA_ACCESS_GOVERNED_ADAPTERS_E
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "29f75a56c445279dd4dde30eea3ee99999f0dc0448efdceaa7b126c0cfcd03e6"
results:
  - gate: pytest tests/test_data_governance.py -q
    outcome: pass
    evidence: 4 passed
  - gate: ruff, mypy and release gate
    outcome: pass
    evidence: evidence/data-tests.txt
---
# verify

Leituras declaradas podem ficar ready; mutações sem aprovação são bloqueadas.
