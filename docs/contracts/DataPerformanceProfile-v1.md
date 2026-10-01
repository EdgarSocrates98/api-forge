# DataPerformanceProfile/v1

Observed performance and access-risk profile for Redis/Valkey, DynamoDB,
MongoDB/DocumentDB and Neptune. It never invents hot-key, index or capacity
claims without source facts.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `id` | string | yes |
| `database` | enum | yes |
| `latency_class` | enum | yes |
| `observed_signals` | array | no |
| `risk_findings` | array | no |
| `unresolved` | array | no |
