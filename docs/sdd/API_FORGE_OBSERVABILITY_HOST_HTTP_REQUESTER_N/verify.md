---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HOST_HTTP_REQUESTER_N
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "fe8644d80b0214ce609f5d7496b31b6bdb681b4cb659321122afb65102b71e5d"
results:
  - gate: pytest tests/observability
    outcome: pass
    evidence: 33 passed
  - gate: ruff and mypy
    outcome: pass
    evidence: all checks passed
---
# verify

Endpoints HTTP, hosts não permitidos e placeholders não resolvidos são rejeitados antes do callback.
