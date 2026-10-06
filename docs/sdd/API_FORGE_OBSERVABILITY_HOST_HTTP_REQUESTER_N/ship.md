---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HOST_HTTP_REQUESTER_N
phase: ship
profile: standard
status: draft
upstream:
  path: benchmark.md
  sha256: "9c892fa1595ae32734cc01bae5e0a8459287b83e442ededfe725a6be04e93fd5"
deviations: []
evidence:
  - path: sdd/API_FORGE_OBSERVABILITY_HOST_HTTP_REQUESTER_N/evidence/requester-tests.txt
    sha256: "292fb4a323efd07a2cb248225b4245b66e6bb2d3e19570acb830e69d37a1e522"
---
# ship

Fronteira HTTP publicada; o próximo incremento será um adapter host específico para cada provider com timeout e retry governados.
