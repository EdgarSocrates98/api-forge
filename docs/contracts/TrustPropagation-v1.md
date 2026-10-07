# TrustPropagation/v1

Record of deriving one `TrustUnit` from source units under an explicit
transform (step11 §10).

| Field | Meaning |
|---|---|
| `transform` | `verbatim`, `parse_extract`, `summarize`, `governed_verification`, `system_synthesis` |
| `derived` | The resulting `TrustUnit` |
| `derived_from` | `subject` of each source unit |
| `taint_reduced` | True only when `governed_verification` + `evidence_refs` cleared removable taints |
| `reason` | Free-text justification for the transform |

Rules: taint is the union of sources; trust is the weakest source's exact
level, lifted at most one tier by evidence-backed `governed_verification`;
`instruction_authority` never widens — any `none` source forces `none`, and
only `system_synthesis` over fully authoritative inputs may keep authority.
