# AnalyticalAccessIR/v1

Intermediate representation for OpenSearch/Elasticsearch and Redshift access.
It captures observed search, aggregation, pagination, partition and write
signals without asserting cluster health or query performance.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `id` | string | yes |
| `engine` | `opensearch\|redshift` | yes |
| `provider` | string | no |
| `indexes_or_tables` | array | no |
| `operations` | array | no |
| `query_signals` | array | no |
| `risk_findings` | array | no |
| `unresolved` | array | no |
