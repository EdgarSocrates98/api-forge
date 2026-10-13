# GraphPlanIR/v1

One parsed graph explain/profile dump. Produced by `apiforge model graph-explain`
from a file the operator captured or `collect neptune-explain` wrote. Parsing never
contacts a database. A plan is `executed` only when its format records runtime
columns (Gremlin profile, openCypher dynamic/details, Neo4j PROFILE, SPARQL explain
with units).

Model: `apiforge.contracts.graph_access.GraphPlanIR`.

| Field | Type | Required |
|---|---|---|
| `version` | integer (1) | no |
| `id` | string | yes |
| `format` | enum (below) | yes |
| `executed` | boolean | yes |
| `source_sha256` | string | yes |
| `synthetic` | boolean | no — `true` marks fixtures shaped from documentation, never field evidence |
| `operators` | array of PlanOperator | no |
| `warnings` | array of strings | no |
| `predicate_count` | integer \| null | no |

`format`: `neptune-gremlin-explain`, `neptune-gremlin-profile`,
`neptune-opencypher-static`, `neptune-opencypher-dynamic`, `neptune-sparql-explain`,
`neo4j-explain`, `neo4j-profile`.

## PlanOperator

| Field | Type | Notes |
|---|---|---|
| `op_id` | string | positional |
| `name` | string | operator or step name |
| `arguments` | string | continuation rows are joined |
| `units_in`, `units_out` | integer \| null | runtime rows when executed |
| `estimate` | string \| null | `estimatedCardinality` / `Estimated Rows` |
| `native` | boolean | `false` for Neptune steps "not converted into Neptune steps" |

The backing `data.graph.plan` fact carries `non_native_steps`, `unbounded_estimate`,
`predicate_warning`, `all_label_scan`, `full_scan_operator` and, for executed plans,
`max_fanout_ratio` — judged by `AF-GDB-020..025`.
