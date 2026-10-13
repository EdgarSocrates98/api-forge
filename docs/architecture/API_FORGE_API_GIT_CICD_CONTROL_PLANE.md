# API Forge API + Git + CI/CD Control Plane

Language: [English](API_FORGE_API_GIT_CICD_CONTROL_PLANE.md) · [Português (Brasil)](API_FORGE_API_GIT_CICD_CONTROL_PLANE.pt-BR.md)

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
                                  +--> verify -> JUnit/Markdown
                                  +--> IDE/UI local host projections
```

The pipeline emits a canonical `ChangeControlResult` and does not let CLI,
MCP, IDE or UI reinterpret support state, status, evidence, limitations or
gaps. Surfaces are projections over the same matrix.

## Determinism

Contract and project inputs are hashed by the existing case service. Graph and
receipt artifacts are canonical. Run identity is derived from repository,
base SHA and head SHA. Stage durations are operational observations stored in
`metrics.json` and are not used as deterministic decision inputs.

The live ingress writes a `ChangeCollectionReceipt` beside the sanitized
bundle. It binds provider, refs, source hashes, check summaries and the bundle
SHA-256 without persisting credentials. The receipt proves what bytes were
collected at a stated time; it does not prove authorship, deployment health,
provider freshness or permission beyond the declared observation.

## Recommendation governance

`Recommendation/v1` requires a recommendation, facts, assumptions,
alternatives, risks, unresolved items, evidence references, verifier and
confidence. The local evaluator checks the shape and declared evidence. It
does not claim that a recommendation is correct in production; an independent
verifier and human approval remain necessary for a release decision.

## Published reports and host surfaces

`apiforge change-control publish` produces deterministic JUnit XML, Markdown,
SARIF and standalone HTML from `result.json`; CI uploads them as artifacts.
The same canonical result is available through `change-control surface
--surface ide|ui` and the `change-control serve` host at `/api/ide`, `/api/ui`,
`/api/result`, `/healthz`, `/readyz` and all four report endpoints.

The host binds to loopback by default, serves no project files and performs no
external mutation. A remote or production IDE/UI deployment still requires a
host-owned authentication, network and retention policy.

## Evolution path

Provider freshness is represented by `af-external-read-receipt/1` and can be
verified with `apiforge integration verify-receipt`. Remote UI/IDE serving is
supported through the authenticated TLS host, the container recipe and the
GitHub Pages workflow. Mutation remains a separate host adapter: the CI-only
`scripts/github_pr_host.py` boundary can create/reuse a PR and optionally
request auto-merge, emitting `af-github-pr-receipt/1`; the core still cannot
perform those operations. Deployment health remains a separate GET receipt,
not an inference from a green build.
