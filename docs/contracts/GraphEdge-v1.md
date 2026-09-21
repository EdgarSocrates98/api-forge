# GraphEdge/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `from_id` | string | yes |
| `to_id` | string | yes |
| `kind` | EdgeKind | yes |
| `props` | object | no |

A directed provenance edge between two node ids.
