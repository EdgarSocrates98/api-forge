# DataAccessIR/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `id` | string | yes |
| `produced_by` | string | no |
| `unresolved` | array | no |
| `attributes` | object | no |
| `database` | string | no |
| `provider` | string | no |
| `entities` | array | no |
| `access_patterns` | array | no |

Data-access intermediate representation; per-database fields land
with the database adapters.

**Redis/Valkey producer** (`apiforge model redis --path <dir>`):
`database="redis"`, `provider="redis|valkey"`, `entities` = distinct
literal keys plus static key patterns (`f"order:{id}"` -> `order:*`),
`access_patterns` = distinct normalized commands, `unresolved` =
diagnostic codes (`AF-REDIS-*`), `attributes` = fact counts and the
files whose receiver binding was name-heuristic only.
