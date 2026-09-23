# Change-control IDE/UI host

The host turns a completed `change-control run` into a read-only browser and
IDE bridge without introducing a second result contract. It can run locally
or as an authenticated TLS service behind a controlled remote host.

```bash
apiforge change-control serve --run-dir .apiforge/change-control
```

The default bind address is `127.0.0.1`. Fixed endpoints are:

| Endpoint | Purpose |
|---|---|
| `/` | Dependency-free visual report. |
| `/api/result` | Canonical `ChangeControlResult`. |
| `/api/ide` | `CapabilityResult/v1` envelope for an IDE host. |
| `/api/ui` | Same canonical result for a visual host. |
| `/healthz` | Liveness probe with no project data. |
| `/readyz` | Readiness probe proving `result.json` is readable. |
| `/reports/change-control.junit.xml` | CI-compatible JUnit projection. |
| `/reports/change-control.md` | Human-reviewable Markdown projection. |
| `/reports/change-control.sarif.json` | Code-scanning-compatible SARIF. |
| `/reports/change-control.html` | Standalone static report for remote hosting. |

The host reads only the selected run directory and exposes no arbitrary file
route. It cannot merge, push, dispatch, deploy, comment, change status or
autofix. The `state`, `status`, `evidence`, `gaps` and `limitations` are copied
from the canonical result; a presentation surface cannot promote `review`,
`blocked` or `unresolved` to success.

For an editor that prefers an artifact instead of HTTP:

```bash
apiforge change-control surface \
  --run-dir .apiforge/change-control \
  --surface ide \
  --out .apiforge/change-control/ide.json
```

The host is a local deployment proof. A shared or production deployment still
needs host-owned authentication, TLS, network policy, retention, identity and
independent verification. Direct remote binding refuses to start without a
Bearer token and TLS; `--trust-proxy` is permitted only when a trusted HTTPS
proxy terminates TLS before the host.

For a containerized remote host:

```bash
set APIFORGE_HOST_TOKEN=use-a-secret-manager-value
docker compose -f docker-compose.change-control.yml up --build
```

Mount a certificate and key under `deploy/tls/`, or terminate HTTPS in a
trusted proxy and use the documented proxy boundary. The container is
read-only, drops Linux capabilities and exposes only the selected run.

The repository also contains `.github/workflows/change-control-pages.yml`.
After Pages is enabled for the repository, it publishes the standalone HTML,
Markdown and SARIF projections from the canonical result on `main`.

## Green PR lifecycle

The CI workflow opens or reuses the pull request only after the complete
validation job succeeds. A repository administrator may opt into the separate
host-owned auto-merge job by setting the repository variable
`APIFORGE_AUTO_MERGE=true`; the job uses the GitHub workflow token, reads the
open PR back, and uploads an `af-github-pr-receipt/1`. The receipt proves the
request and read-back, not authorship, branch protection, merge completion or
deployment health. Enable this variable only together with the repository's
required-review and required-check policy; the API Forge core and agents never
receive merge authority.
