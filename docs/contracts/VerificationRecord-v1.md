# VerificationRecord/v1

Frozen, closed (`extra: forbid`). Independent proof result for a sealed task;
the record is not an acceptance decision and does not prove authorship.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `task_id` | string | yes |
| `revision` | integer | yes |
| `run_id` | string | yes |
| `verdict` | `pass`, `fail`, `inconclusive` | yes |
| `checks` | array of VerificationCheck | no |
| `evidence` | array[string] | no |
| `gaps` | array[string] | no |
| `holdout` | array of HoldoutRecord | no |
| `verified_by` | string | yes |

`pass` requires at least one holdout record and every declared holdout to be
detected. Missing proof remains `inconclusive`.
