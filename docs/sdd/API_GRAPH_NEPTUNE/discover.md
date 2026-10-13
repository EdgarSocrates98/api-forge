---
sdd: 1
feature: API_GRAPH_NEPTUNE
phase: discover
profile: standard
status: draft
approaches:
  - id: single-graph-specialist
    summary: um agente vendor-neutral api-graph-data-architect + skill api-forge-graph + packs knowledge/graph-databases|neptune|neo4j
    verdict: chosen -- ownership exclusivo, roster 25->26, vendors viram packs
  - id: graph-plus-neptune-agents
    summary: api-graph-data-architect + api-neptune-engineer
    verdict: refused -- sobrepõe infra-reviewer, architecture-reviewer, observability e operations
  - id: extend-data-access
    summary: absorver grafo no api-data-access-architect
    verdict: refused -- nove stores já; roteamento de modelagem/planos/RDF fica diluído
chosen: single-graph-specialist
---
# discover

O Forge reconhecia chamadas Neptune, mas planos e cardinalidade eram blind spots, a única
regra era um `unbounded` de mesma linha (`AF-DATA-013`), o export `--format neptune` era stub
e não havia dono para perguntas de graph store. Brainstorm, DEFINE e DESIGN:
`.claude/sdd/features/{BRAINSTORM,DEFINE,DESIGN}_API_GRAPH_NEPTUNE.md`.
