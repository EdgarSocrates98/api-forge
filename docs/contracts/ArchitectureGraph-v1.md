# ArchitectureGraph-v1

The first-wave workspace graph is a deterministic local projection over
workspace, repository, service, contract, dependency and runtime claims.

Every relation carries `source`, `from_id`, `to_id`, an `EvidenceRecord` and
limitations. Evidence levels remain distinct:

`observed` · `declared` · `inferred` · `heuristic` · `verified` · `unknown`

The graph is bounded to declared repositories and local read-only signals. A
missing repository, unsupported relation or stale input stays in `unresolved`.
The graph is not proof of deployment, runtime traffic, production dependency
or host capability.
