# TaskRevision/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `task_id` | string | yes |
| `revision` | integer | yes |
| `content_sha256` | string | yes |
| `changed_fields` | array | no |
| `sealed_by` | string|null | no |
| `seal_signature_b64` | string|null | no |
| `public_key_sha256` | string|null | no |

An immutable snapshot of a task's reviewed content + optional seal.
