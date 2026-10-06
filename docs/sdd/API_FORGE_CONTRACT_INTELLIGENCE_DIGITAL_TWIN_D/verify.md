---
sdd: 1
feature: API_FORGE_CONTRACT_INTELLIGENCE_DIGITAL_TWIN_D
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "c79c80167f64237c4095056aa314161a7032bea15ec6a4ca8475eb6e93975185"
results:
  - gate: "pytest tests/contract_intel/test_contract_intel.py"
    outcome: pass
    evidence: "4 passed"
  - gate: "ruff check src tests"
    outcome: pass
    evidence: "All checks passed"
  - gate: "mypy src/apiforge"
    outcome: pass
    evidence: "no issues found"
---

# verify

Acceptance: OpenAPI and gRPC produce a unified verdict; breaking changes are counted; all eight scenarios are declared; timeout simulation is deterministic; `network_called` is false; unknown scenarios fail closed.
