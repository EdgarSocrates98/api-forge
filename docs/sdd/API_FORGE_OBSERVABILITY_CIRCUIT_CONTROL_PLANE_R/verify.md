---
sdd: 1
feature: API_FORGE_OBSERVABILITY_CIRCUIT_CONTROL_PLANE_R
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "b26558d624d309fb02e7c598beda9e3501ad5ab784189dbd02594285e53c4ab2"
results:
  - gate: pytest tests/observability
    outcome: pass
    evidence: 38 passed
  - gate: ruff and mypy
    outcome: pass
    evidence: all checks passed
---
# verify

Falhas, abertura e bloqueios geram contadores e alertas específicos do provider.
