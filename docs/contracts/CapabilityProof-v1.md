# CapabilityProof/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `capability` | string | yes |
| `proven_by` | string | yes |
| `scope` | string | no |
| `evidence` | array | no |
| `limitations` | array | no |

Which capability a test/bench actually proves, and to what extent.
