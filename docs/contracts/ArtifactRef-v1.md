# ArtifactRef/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `path` | string | yes |
| `sha256` | string | yes |
| `kind` | string | no |

Pointer to a content-addressed artifact — path + sha256, never inline.
