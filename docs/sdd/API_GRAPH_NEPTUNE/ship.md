---
sdd: 1
feature: API_GRAPH_NEPTUNE
phase: ship
profile: standard
status: draft
upstream:
  path: benchmark.md
  sha256: "1cf3a5cad0319b5b3ed0e1dc3ee919528e1d62107e3c1944f674cfa9cfba580a"
deviations: [no-field-cycle, synthetic-plan-fixtures, no-graph-review-runtime-capability]
evidence:
  - path: sdd/API_GRAPH_NEPTUNE/evidence/build-gates.txt
    sha256: ""
---
# ship

Especialização de bancos de grafo entregue no commit `698b46b` (`feature/graph_evo`).
Pendências do owner: field cycle num repositório Neptune/Neo4j real e dumps reais redigidos
para substituir as fixtures sintéticas de plano.
