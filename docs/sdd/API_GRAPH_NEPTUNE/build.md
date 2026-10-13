---
sdd: 1
feature: API_GRAPH_NEPTUNE
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "d2a0cde84898497d0bfc3696fffa290155078f8bc45b5749632018e71e498454"
tasks:
  - id: w1-owner-and-knowledge
    status: done
    evidence: sdd/API_GRAPH_NEPTUNE/evidence/build-gates.txt
  - id: w2-access-ir-and-rules
    status: done
    evidence: sdd/API_GRAPH_NEPTUNE/evidence/build-gates.txt
  - id: w3-plans
    status: done
    evidence: sdd/API_GRAPH_NEPTUNE/evidence/build-gates.txt
  - id: w4-collector
    status: done
    evidence: sdd/API_GRAPH_NEPTUNE/evidence/build-gates.txt
  - id: w5-export
    status: done
    evidence: sdd/API_GRAPH_NEPTUNE/evidence/build-gates.txt
claims: [graph-owner, graph-access-ir, graph-rules, graph-plans, explain-collector, graph-export, graph-quality-eval]
---
# build

W1-W5 entregues. Field cycle (W6) segue `unresolved` até haver repositório alvo.
