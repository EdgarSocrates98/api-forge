# DataAccessReadiness/v1

Governance preflight for static data-access facts in Redis/Valkey, MongoDB,
DynamoDB and Neptune. It is local-only and does not open connections.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `id` | string | yes |
| `database` | `redis\|mongo\|dynamo\|neptune` | yes |
| `status` | `ready\|review\|blocked` | yes |
| `observed_patterns` | array | no |
| `mutation_patterns` | array | no |
| `blockers` | array | no |
| `evidence` | array | no |

Mutating patterns are blocked unless an explicit approval policy allows them.
