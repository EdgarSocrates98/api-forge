# OutcomeBrief/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `status` | BriefStatus | yes |
| `outcome` | string | yes |
| `human_action` | string|null | no |
| `proof` | array | no |
| `gaps` | array | no |
| `next` | string|null | no |
| `open` | array | no |
| `subject` | string|null | no |
| `graph_impact` | `GraphImpactAssessment/v1`|null | no |

The closing brief — DONE is refused while mandatory gaps exist.

When present, `graph_impact` is the exact assessment persisted with the runtime
run. The brief renderer reads that artifact and does not recalculate graph
impact, so impacted nodes, edge evidence, policy effects and unresolved gaps
remain identical across routing, plan and brief projections.
