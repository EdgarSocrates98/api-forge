# TaskSpec/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `id` | string | yes |
| `outcome` | string | yes |
| `size` | TaskSize | no |
| `writable_paths` | array | no |
| `inputs` | array | no |
| `dependencies` | array | no |
| `preconditions` | array | no |
| `tests` | array | no |
| `expected_proofs` | array | no |
| `budgets` | Budgets | no |
| `risk` | TaskRisk | no |
| `strategy` | Recipe | no |
| `rollback` | string | no |
| `acceptance_criteria` | array | no |
| `capability_covered` | string|null | no |
| `state` | TaskState | no |
| `revision` | integer | no |

A declared unit of agentic work — scope is closed, never widened at run.
