---
sdd: 1
feature: API_GRAPH_NEPTUNE
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "339dcb3d1cebf073fb2b2b370516a98086c4872c6f5e4cf33778fe560a10efbc"
tasks:
  - id: w1-owner-and-knowledge
    covers: [graph-owner]
    test: sdd/API_GRAPH_NEPTUNE/evidence/build-gates.txt
    risk: medium
    rollback: revert agents/, skills and packs
  - id: w2-access-ir-and-rules
    covers: [graph-access-ir, graph-rules, graph-quality-eval]
    test: sdd/API_GRAPH_NEPTUNE/evidence/build-gates.txt
    risk: medium
    rollback: restore dbaccess Neptune scanner
  - id: w3-plans
    covers: [graph-plans]
    test: sdd/API_GRAPH_NEPTUNE/evidence/build-gates.txt
    risk: low
    rollback: remove model graph-explain
  - id: w4-collector
    covers: [explain-collector]
    test: sdd/API_GRAPH_NEPTUNE/evidence/build-gates.txt
    risk: high
    rollback: remove collect neptune-explain
  - id: w5-export
    covers: [graph-export]
    test: sdd/API_GRAPH_NEPTUNE/evidence/build-gates.txt
    risk: low
    rollback: restore named stub
---
# plan

Ondas W1-W5 do DESIGN; W6 (field cycle) fica unresolved até haver repositório alvo.
