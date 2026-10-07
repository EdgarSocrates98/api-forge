# GraphImpactEffect/v1

`GraphImpactEffect/v1` is the closed policy value applied to one graph impact
band. It is not an authorization grant; it is merged monotonically with the
existing routing assessment.

| Field | Meaning |
|---|---|
| `gate_state` | `open`, `review` or `blocked` |
| `verification_depth` | `standard`, `elevated` or `strict` |
| `required_roles` | Unique review roles required by policy |
| `selection` | `prefer`, `neutral`, `demote`, `exclude` or `unresolved` |

The effect is serialized as part of `GraphImpactPolicy/v1` and the resulting
`GraphImpactAssessment/v1`.
