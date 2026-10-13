# Fact/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `fact_id` | string | yes |
| `kind` | string | yes |
| `source` | SourceRef | yes |
| `measures` | object | no |
| `attrs` | object | no |


