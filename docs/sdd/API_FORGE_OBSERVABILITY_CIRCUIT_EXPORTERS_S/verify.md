---
sdd: 1
feature: API_FORGE_OBSERVABILITY_CIRCUIT_EXPORTERS_S
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "b0e215e696178e1858c2e52020065d171fc58ba72fb2c92304d33fefa3d26b34"
results:
  - gate: pytest tests/observability
    outcome: pass
    evidence: 42 passed
  - gate: ruff and mypy
    outcome: pass
    evidence: all checks passed
---
# verify

Payloads possuem formatos distintos por backend; sem callback o export é disabled e não chama rede.
