---
sdd: 1
feature: API_FORGE_OBSERVABILITY_READ_SAFETY_POLICY_L
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "d22e5329fb7b83e96bfc90dd9a510944cbf74a9b64e3c95261648d31e7e2101c"
results:
  - gate: pytest tests/observability
    outcome: pass
    evidence: 26 passed
  - gate: ruff and mypy
    outcome: pass
    evidence: all checks passed
---
# verify

Resposta acima de `max_records` resulta em `blocked`, `network_called=true` e `mutation_performed=false`.
