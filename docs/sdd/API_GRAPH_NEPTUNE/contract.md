---
sdd: 1
feature: API_GRAPH_NEPTUNE
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "05489b1edb29e4b9756479afd2536e359486a50dcae2bb3dfd6ed42bc8a91795"
covers: [GraphAccessIR/v1, GraphPlanIR/v1, GraphExport/v1, graph-access-ir, graph-plans, graph-export]
api_ir:
  input: source tree (py/java/go/ts), explain/profile dumps, system graph nodes/edges
  output: data.graph.query and data.graph.plan facts, GraphAccessIR, GraphPlanIR, Gremlin CSV, N-Triples
---
# contract

`docs/contracts/GraphAccessIR-v1.md` e `docs/contracts/GraphPlanIR-v1.md`; `GraphExport` ganha
`format: rdf` e `files` (digests). Regras `AF-GDB-*` (área `GDB`) e `AF-DATA-013` sobre o tipo
unificado `data.graph.query`. `AF-GRAPH-*` continua do system graph.
