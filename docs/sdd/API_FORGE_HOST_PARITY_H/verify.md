---
sdd: 1
feature: API_FORGE_HOST_PARITY_H
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "b1492c5fc5037c2a59733c6ba25e582f27d4657a06f4c6bd71732d01ae82b9bf"
results:
  - gate: pytest tests/agentops
    outcome: pass
    evidence: 13 passed
  - gate: release gate
    outcome: pass
    evidence: API Forge release gate PASS
---
# verify

Todos os quatro layouts estão prontos para o core e suas limitações são explicitadas.
