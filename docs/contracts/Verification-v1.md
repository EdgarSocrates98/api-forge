# Verification/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `id` | string | yes |
| `subject` | string | yes |
| `method` | string | yes |
| `result` | VerificationResult | no |
| `evidence` | array | no |
| `verified_by` | string | no |

A check over a subject — method, result, evidence. Never implicit.
