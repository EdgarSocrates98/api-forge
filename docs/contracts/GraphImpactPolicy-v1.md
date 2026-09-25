# GraphImpactPolicy/v1

`GraphImpactPolicy/v1` is the local, versioned policy used by the bounded graph
impact assessor. It is data, not a model or provider integration.

| Field | Meaning |
|---|---|
| `policy_version` | Version included in the assessment identity |
| `default_mode` | `direct`, `transitive` or `all`; default is `transitive` |
| `max_depth` | Reverse traversal depth bound; default is `4` |
| `max_nodes` | Unique impacted-node bound; default is `256` |
| `max_edges` | Explicit traversed-edge bound; default is `1024` |
| `incomplete_effect` | `elevated` or `blocked` minimum effect for incomplete evidence |
| `unknown_candidate_effect` | `static` or `unresolved` treatment for unmapped candidates |
| `effects` | Complete map for `none`, `explicit`, `bounded` and `unresolved` bands |

Each effect declares `gate_state`, `verification_depth`, `required_roles` and a
selection effect. The closed gate vocabulary is `open`, `review`, `blocked`; the
verification vocabulary is `standard`, `elevated`, `strict`; and candidate
selection is `prefer`, `neutral`, `demote`, `exclude` or `unresolved`.

Malformed policy data is refused with `AF-RUNTIME-POLICY`, including the
rejected field and a safe unlock. Missing or partial graph evidence cannot lower
the existing A risk/complexity or B scorecard outcome.
