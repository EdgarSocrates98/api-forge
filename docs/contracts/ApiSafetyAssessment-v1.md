# ApiSafetyAssessment/v1

Deterministic gate for the API controls required before production planning.
It covers authentication, authorization, input validation, idempotency,
timeouts, retries, circuit breaker, rate limiting and structured observability.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `id` | string | yes |
| `subject` | string | no |
| `status` | `ready\|review\|blocked` | yes |
| `required_controls` | array | no |
| `passed_controls` | array | no |
| `missing_controls` | array | no |
| `failed_controls` | array | no |
| `evidence` | array | no |

Missing declarations produce `review`; an explicitly failed control produces
`blocked`.
