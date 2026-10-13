# AgenticQualityAssessment/v1

Aggregate quality view for golden evals, holdout coverage and host parity.
It preserves blocked and review cases instead of averaging them away.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `id` | string | yes |
| `subject` | string | no |
| `status` | `ready\|review\|blocked` | yes |
| `total_cases` | integer | yes |
| `passed_cases` | integer | yes |
| `review_cases` | integer | yes |
| `blocked_cases` | integer | yes |
| `holdout_covered` | integer | yes |
| `host_gaps` | array | no |
| `blockers` | array | no |
| `evidence` | array | no |
