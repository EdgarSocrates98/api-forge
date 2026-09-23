# API Forge API + Git + CI/CD Control Plane

## Boundary

The feature normalizes a pull request, branch or replay artifact into
`ChangeBundle/v1`. The core consumes that bundle without importing a GitHub
SDK or calling a provider. External collection is isolated behind
`ReadOnlyTransport` and `GitHubReadOnlyAdapter`; local reproduction uses
`ReplayAdapter`.

```text
provider/replay
      |
      v
ChangeBundle/v1
      |
      v
analyze -> next-step -> graph -> evidence -> brief
      |                         |
      +--> recommendation eval  +--> result + metrics
```

The pipeline emits a canonical `ChangeControlResult` and does not let CLI,
MCP, IDE or UI reinterpret support state, status, evidence, limitations or
gaps. Surfaces are projections over the same matrix.

## Determinism

Contract and project inputs are hashed by the existing case service. Graph and
receipt artifacts are canonical. Run identity is derived from repository,
base SHA and head SHA. Stage durations are operational observations stored in
`metrics.json` and are not used as deterministic decision inputs.

## Recommendation governance

`Recommendation/v1` requires a recommendation, facts, assumptions,
alternatives, risks, unresolved items, evidence references, verifier and
confidence. The local evaluator checks the shape and declared evidence. It
does not claim that a recommendation is correct in production; an independent
verifier and human approval remain necessary for a release decision.

## Evolution path

The next safe extension is a real read-only provider receipt and a proven IDE
or UI host integration. Mutation requires a separate adapter, policy approval,
identity, rollback, receipt and independent verification. The core remains
small until those proofs exist.
