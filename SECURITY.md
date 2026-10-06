# Security Policy

Language: [English](SECURITY.md) · [Português (Brasil)](SECURITY.pt-BR.md)

## Scope

API Forge is an offline-first engineering platform. Its deterministic core
analyzes source, contracts and persisted evidence; it does not execute target
applications, call model SDKs, or mutate cloud, database, broker or Git
provider state.

This policy covers:

- the Python package and CLI under `src/apiforge/`;
- the MCP surface and the repository's agents and skills;
- read-only external adapters and their receipt handling;
- the dedicated CI host boundary in `scripts/` and `.github/workflows/`;
- the containerized change-control host.

The policy does not turn a static analysis result, fixture, local runtime probe
or receipt into proof of production security. Production deployment, provider
permissions, runtime health and operational hardening remain deployment-owner
responsibilities and require independent evidence.

## Supported versions

| Version | Support status |
| --- | --- |
| `0.1.x` | Security fixes accepted |
| Older versions | Upgrade before reporting a vulnerability when possible |

The supported runtime is the Python version declared in `pyproject.toml`.

## Reporting a vulnerability

Please do not disclose suspected vulnerabilities in a public issue or pull
request. Prefer a private GitHub Security Advisory for this repository:

<https://github.com/EdgarSocrates98/api-forge/security/advisories/new>

If private advisories are unavailable, send a report to
`edgarsocrates98@gmail.com` with the subject `API Forge security report`.

Include, when safe to share:

- a concise description and impact;
- affected commit, release or component;
- reproduction steps or a minimal non-destructive proof of concept;
- required permissions, configuration and environment;
- logs or receipts with secrets, tokens and personal data removed;
- a suggested mitigation, if known.

Please allow the maintainers to investigate privately before public
disclosure. Do not send credentials, private keys, access tokens or production
data in the report.

## Handling process

Reports are triaged privately, reproduced in an isolated branch or sandbox,
and recorded with the relevant evidence and unresolved limitations. A fix
must include a regression test or an explicit reason why a test cannot safely
be added. External mutations are never used as part of reproduction without an
explicit policy gate and approval.

The resolution may include a patched commit, mitigation guidance, release
note and coordinated disclosure. A receipt proves correspondence between the
reported artifacts and the verification run; it does not prove authorship or
that an affected production deployment has been fixed.

## Security boundaries and expectations

- Treat bundles, contracts, provider payloads and generated artifacts as
  untrusted input.
- Keep secrets outside cases, bundles, receipts, fixtures, logs and PR bodies.
- Use the GET-only adapters for external observations. They do not authorize
  merge, push, deploy, workflow dispatch or other mutation.
- GitHub PR creation and optional auto-merge are restricted to the dedicated
  CI host, require explicit policy configuration and emit a
  `af-github-pr-receipt/1` receipt. The core and agents do not receive that
  authority.
- Configure bearer authentication and TLS, or a trusted TLS-terminating
  proxy, before exposing the change-control host beyond loopback.
- Keep anonymized examples anonymized; do not commit provider payloads that
  contain identities, URLs with signed parameters or credentials.
- Do not interpret `supported` local analysis as a production security claim.
  Provider freshness, deployment safety, runtime health and SLOs require
  independent external evidence.

## Out-of-scope reports

The following are not, by themselves, vulnerabilities in the core:

- a capability being intentionally `heuristic`, `unresolved` or
  `unsupported` when the limitation is documented;
- a refusal that exposes its documented `AF-*` code, rejected field and safe
  unlock;
- missing production evidence when no production target or provider access
  was configured;
- insecure configuration introduced by a downstream deployment owner, unless
  the repository's documented defaults claim to prevent it.

Reports that contain secrets or personal data should be withdrawn and rotated
immediately through the affected provider.
