# Finding/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `finding_id` | string | yes |
| `rule_id` | string | yes |
| `status` | FindingStatus | yes |
| `severity` | Severity | yes |
| `title` | string | yes |
| `detail` | string | no |
| `evidence` | array | no |
| `remediation` | string|null | no |


