# GraphCandidateImpact/v1

`GraphCandidateImpact/v1` explains how explicit graph references affect one
routing candidate.

| Field | Meaning |
|---|---|
| `candidate` | Existing capability name |
| `refs` | Caller-supplied graph node IDs |
| `matched` | `explicit`, `none` or `unresolved` |
| `selection` | Policy effect used by graph-aware ordering |
| `evidence` | Explicit match, missing-node or unmapped-reference diagnostics |

An explicit match can prefer or constrain an already eligible candidate. It
cannot bypass profile, risk, prerequisite, evidence or expertise checks.
