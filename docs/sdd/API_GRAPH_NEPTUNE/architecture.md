---
sdd: 1
feature: API_GRAPH_NEPTUNE
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "e6fa2e1eda37409bed87c19ac34cd6dc479161e0f2ee125fde2c15e8eb2c89b6"
files:
  - src/apiforge/adapters/graph_/
  - src/apiforge/contracts/graph_access.py
  - src/apiforge/collectors/graph_explain.py
  - src/apiforge/graph/formats.py
  - src/apiforge/graph/export.py
  - src/apiforge/evals/graph_quality.py
  - src/apiforge/rules/catalog/gdb.yaml
  - agents/api-graph-data-architect.md
  - .agents/skills/api-forge-graph/
  - knowledge/graph-databases/
  - knowledge/neo4j/
decisions:
  - id: exclusive-owner
    decision: api-graph-data-architect owns graph-store tools; data-access cedes model neptune*
    rollback: restore the two tools to api-data-access-architect and drop the agent
  - id: gdb-namespace
    decision: AF-GDB-* for graph-database rules; AF-GRAPH-* stays system graph
    rollback: remove gdb.yaml
  - id: unified-fact-kind
    decision: data.graph.query with vendor measure; AF-DATA-013 rebinds to it
    rollback: rebind AF-DATA-013 to data.neptune.query
  - id: allowlisted-collector
    decision: closed read-only neptunedata allowlist; guards before any client; SPARQL dump-only
    rollback: delete collectors/graph_explain.py and the CLI command
  - id: knowledge-packs
    decision: vendor knowledge in knowledge/ packs, prose in skill references
    rollback: delete the two new packs, restore neptune pack v1
  - id: deterministic-export
    decision: all-String Gremlin CSV and IRI-namespaced N-Triples, grammar-validated
    rollback: restore the named stub refusal
---
# architecture

Camadas: `contracts` <- `adapters/graph_` <- `data_governance`/`rules` <- `cli`/`dispatch`.
O collector depende só dos analisadores puros; o core nunca importa `boto3`.
