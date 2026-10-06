---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HOST_EXPORT_AUTH_T
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "4e04304e1467a24076117bccc564a528981d61491c4bf0a4ee761e73e8cb39be"
results:
  - gate: pytest tests/observability
    outcome: pass
    evidence: 45 passed
  - gate: ruff and mypy
    outcome: pass
    evidence: all checks passed
---
# verify

Sem aprovação, credencial, sender ou host confiável o export é bloqueado sem chamada de rede.
