# KnowledgeImpactReport-v1

§29 declared relation graph: source -> pack -> rule -> skill -> eval.

| Field | Meaning |
|---|---|
| `nodes`/`edges` | `GraphNode`/`GraphEdge` with closed kind vocabularies |
| `totals` | counts by node kind plus edge count |
| `unresolved` | relations with no declared carrier (agent -> knowledge today) |
| `evidence` | provenance record |

Invariant: every edge derives from declared data (pack.yaml rule_ids,
source_authority.yaml, evals.yaml expectations, skill manifests naming
rule ids); nothing is inferred from prose.
