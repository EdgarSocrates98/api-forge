---
sdd: 1
feature: API_GRAPH_NEPTUNE
phase: benchmark
profile: standard
status: draft
upstream:
  path: secure.md
  sha256: "6337e7dd7d2ac37c62576a77488c3826dac67affe1b6cee98b9445fbbe5cbc14"
baseline: HEAD 4ebd286 (agent-routing 75 cases top1 0.9733; agentic-quality accuracy 1.0)
results:
  - artifact: sdd/API_GRAPH_NEPTUNE/evidence/build-gates.txt
    outcome: measured-by-eval
    note: graph-quality 85 cases (79 golden + 6 holdout) precision 1.0 per language, recall 1.0
  - artifact: sdd/API_GRAPH_NEPTUNE/evidence/build-gates.txt
    outcome: measured-by-eval
    note: agent-routing 81 cases top1 0.9753 (6/6 graph cases), no regression on the 75 baseline cases
  - artifact: sdd/API_GRAPH_NEPTUNE/evidence/build-gates.txt
    outcome: unresolved
    note: traversal latency, plan quality on real clusters and field accuracy need a graph-backed target repository
---
# benchmark

O corpus golden foi escrito junto com o código (in-distribution); os 6 casos holdout acharam um
bug real (cadeia em comentário Java) antes de passarem. Precisão 1.0 não prova generalização —
o field cycle continua `unresolved`.
