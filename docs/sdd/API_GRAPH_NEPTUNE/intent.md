---
sdd: 1
feature: API_GRAPH_NEPTUNE
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "851eea68e864baf55a205975e85f4df5e89998eb2e975b38b2a78f9302850f29"
problem: >
  Graph-store access (Neptune, Neo4j) had no dedicated owner, no typed evidence beyond a
  same-line unbounded flag, no plan reading and a stub export.
success: [graph-owner, graph-access-ir, graph-rules, graph-plans, explain-collector, graph-export, graph-quality-eval]
out_of_scope: [numeric-cost-calculator, neo4j-live-collector, graph-mutation, index-creation, neptune-agent]
owner: api-forge-graph
---
# intent

Especialização vendor-neutral de bancos de grafo com Neptune (Database e Analytics) e Neo4j
como packs, sem redundância com os donos transversais existentes.
