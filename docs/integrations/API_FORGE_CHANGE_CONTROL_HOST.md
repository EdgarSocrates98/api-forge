# Change-control IDE/UI host

The local host turns a completed `change-control run` into a read-only browser
and IDE bridge without introducing a second result contract.

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
| `/reports/change-control.junit.xml` | CI-compatible JUnit projection. |
| `/reports/change-control.md` | Human-reviewable Markdown projection. |

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
independent verification.
