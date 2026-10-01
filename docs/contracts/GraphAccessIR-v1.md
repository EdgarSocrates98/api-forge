# GraphAccessIR/v1

Graph-database call sites observed in source code (Amazon Neptune, Neo4j) and the
draft domain schema they name. Produced by `apiforge model graph-access`
(`neptune-access`, `neo4j-access` filter by vendor) from `data.graph.query` facts.
Nothing executes; a dynamic query keeps its bound `unresolved`.

Model: `apiforge.contracts.graph_access.GraphAccessIR`.

| Field | Type | Required |
|---|---|---|
| `version` | integer (1) | no |
| `id` | string | yes |
| `root` | string | yes |
| `vendors` | array of `neptune`/`neo4j` | no |
| `call_sites` | array of GraphCallSite | no |
| `sketch` | DomainGraphSketch | no |
| `unresolved` | array of diagnostic codes | no |

## GraphCallSite

| Field | Type | Notes |
|---|---|---|
| `fact_id` | string | links to the `data.graph.query` fact |
| `vendor` | `neptune` \| `neo4j` | Bolt drivers are Neptune only when the file names Neptune |
| `language` | `gremlin` \| `opencypher` \| `sparql` | |
| `operation` | string | method or `traverse_<root>` |
| `path`, `line`, `sha256` | provenance | |
| `query_text` | string \| null | first 500 characters of a literal query |
| `query_dynamic` | boolean | text was not a literal |
| `bounded` | boolean | a bound step/clause is written |
| `mutation` | boolean | `addV/addE/drop/property/merge*`, Cypher `CREATE/MERGE/SET/DELETE/REMOVE`, SPARQL update forms |
| `labels_used`, `edge_labels_used` | arrays | written in the query, never inferred |
| `shape_risks` | array | `repeat-without-stop`, `fanout-without-edge-label`, `unfiltered-start`, `open-variable-length-path`, `unlabeled-node-pattern`, `cartesian-pattern`, `unbounded-property-path`, `dynamic-query-text`, `analytics-unscoped-algorithm`, `vector-search-without-topk` |

## DomainGraphSketch

| Field | Type | Notes |
|---|---|---|
| `vertex_labels`, `edge_labels` | arrays | union over call sites |
| `edges` | array of `[from_label?, edge_label, to_label?]` | Cypher patterns give both ends; Gremlin gives the start label only when exactly one is written |
| `evidence` | array of `path:line` | |

Rules over the backing facts: `AF-DATA-013`, `AF-GDB-001..010` (`docs/catalog-contract.md`).
