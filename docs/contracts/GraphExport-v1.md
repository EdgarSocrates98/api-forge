# GraphExport/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `nodes_sha256` | string | yes |
| `edges_sha256` | string | yes |
| `node_count` | integer | yes |
| `edge_count` | integer | yes |
| `built_from` | array | no |
| `format` | string | no |

A canonical graph snapshot — deterministic bytes for a given build.
