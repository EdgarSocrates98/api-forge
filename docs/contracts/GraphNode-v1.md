# GraphNode/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `id` | string | yes |
| `kind` | NodeKind | yes |
| `props` | object | no |
| `sha256` | string|null | no |

A provenance node — deterministic id, closed kind, hashed props.
