# GraphImpactNode/v1

`GraphImpactNode/v1` records one explicit node reached by bounded reverse graph
traversal.

| Field | Meaning |
|---|---|
| `node_id` | Explicit graph node identifier |
| `kind` | Closed `NodeKind` value |
| `depth` | First deterministic reverse-traversal depth |
| `edge_refs` | Explicit `from->kind->to` references used to reach the node |
| `evidence` | Source/evidence references carried by the node or edges |

Nodes are ordered by depth and ID and are never inferred from names or model
output.
