# VerificationCheck/v1

Frozen, closed check emitted by the independent verifier.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `check_id` | string | yes |
| `axis` | `contract`, `security`, `idempotency`, `pagination` | yes |
| `verdict` | `pass`, `fail`, `inconclusive` | yes |
| `evidence` | array[string] | no |
| `gaps` | array[string] | no |
| `limitation` | string or null | no |

Each check cites its evidence or names the gap/limitation that prevents a
confirmed result.
