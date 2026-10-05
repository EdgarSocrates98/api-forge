---
sdd: 1
feature: API_FORGE_EVO_CONVERGENCE
phase: verify
profile: critical
status: done
results:
  - id: focused-tests
    command: uv run pytest -q --basetemp E:/pytest-apiforge-evo-convergence tests/agentops tests/runtime tests/knowledge tests/memory
    observed: false
  - id: static-quality
    command: uv run ruff check src tests; uv run ruff format --check src tests; uv run mypy
    observed: false
  - id: governance-gates
    command: uv run apiforge capabilities verify --detail-level full; uv run apiforge agents check --root .; uv run apiforge sdd check --root docs/sdd
    observed: false
  - id: independent-runtime
    command: uv run apiforge platform verify-runtime --now 2026-10-05T12:00:00-03:00
    observed: false
upstream:
  path: build.md
  sha256: "e159e620fb02f20ab4032d754b177c2c115401b81fad6d79ac37aedf044a207d"
---

# verify

Verification records exact commands and preserves environmental failures as
unresolved. The controlled pytest base directory is outside the repository to
avoid the host temporary-directory ACL failure observed in the baseline.
