# API + Git + CI/CD Control Plane Security

Language: [English](api-git-cicd-control-plane.md) · [Português (Brasil)](api-git-cicd-control-plane.pt-BR.md)

The change-control feature is an evidence boundary, not a deployment engine.
Its default path is local replay from `af-change-bundle/1`; the bundle is
untrusted input and is validated before it reaches the deterministic core.

## Read-only boundary

`GitHubReadOnlyAdapter` receives an injected `ReadOnlyTransport`. The bundled
HTTP transport can issue only `GET` requests, and the adapter reads compare,
pull-request and check-run observations. It never merges, pushes, dispatches a
workflow, changes a branch, publishes a status, executes a deployment or
applies an autofix. Credentials are held by the transport and are not part of
the persisted contract; provider payload fields matching token, authorization,
secret or password are redacted before hashing.

## Trust and evidence

Provider payloads are observations, not proof of runtime health, deployment
success, permission, cost or rollback capability. `af-external-read-receipt/1`
adds a bounded response hash and freshness window; it still does not prove
authorship, permission to mutate or production SLOs. `heuristic`,
`unresolved` and `blocked` remain valid terminal states.

The local verifier checks that the result references existing artifacts. Live
collection now emits a `ChangeCollectionReceipt` beside the sanitized bundle;
the receipt binds the bundle hash and provider source hashes, but remains an
observation rather than authorship, identity, permission, freshness or
deployment proof. A provider-specific gate still needs an approved freshness
policy, identity/permission proof, rollback plan and independent verification
before promoting a production capability state.

## Input classes covered

The implementation treats provider JSON and repository-supplied bundle paths as
untrusted. Paths are validated by the analysis/case storage boundary; JSON is
closed by Pydantic contracts; missing, malformed or transport-failed input is
returned with an `AF-*` code, rejected `field` and safe `unlock`. No error path
should expose a traceback through the public CLI.

## Local IDE/UI host

The built-in host is loopback-only by default and serves fixed routes only. A
remote binding requires a Bearer token and TLS, unless an operator explicitly
places it behind a trusted HTTPS proxy. It does not expose arbitrary
filesystem paths, credentials or mutation endpoints. Its HTML document and
IDE JSON projection are both derived from the same `ChangeControlResult`; a
surface cannot turn `review`, `blocked` or `unresolved` into success.

## Mutation boundary

`scripts/github_pr_host.py` is the only repository mutation host. It is not
imported by `src/apiforge`, requires `APIFORGE_HOST_APPROVED=true`, performs an
idempotent lookup before creating a PR and emits `af-github-pr-receipt/1`. The
optional auto-merge request is controlled by `APIFORGE_AUTO_MERGE=true` and
remains subject to branch protection. The core and agents never obtain this
authority.
