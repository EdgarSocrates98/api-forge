---
sdd: 1
feature: API_FORGE_EVO_CONVERGENCE
phase: verify
profile: critical
status: done
results:
  - id: focused-tests
    command: uv run pytest --basetemp E:/pytest-apiforge-evo-convergence-final -q --tb=short --junitxml=E:/pytest-apiforge-evo-convergence-final-results.xml
    observed: true
    result: 1723 passed, 2 skipped
  - id: static-quality
    command: uv run ruff check src tests; uv run ruff format --check src tests; uv run mypy
    observed: true
    result: all passed; mypy checked 557 source files
  - id: governance-gates
    command: uv run apiforge capabilities verify --detail-level full; uv run apiforge agents check --root .; uv run apiforge sdd check --root docs/sdd
    observed: true
    result: capabilities 21 verified, agents drift-free, SDD check ok
  - id: independent-runtime
    command: uv run apiforge platform verify-runtime --now 2026-10-05T12:00:00-03:00
    observed: true
    result: six local fixture verticals passed
upstream:
  path: build.md
  sha256: "e159e620fb02f20ab4032d754b177c2c115401b81fad6d79ac37aedf044a207d"
---

# verify

Verification records exact commands and preserves environmental failures as
unresolved. The controlled pytest base directory is outside the repository to
avoid the host temporary-directory ACL failure observed in the baseline.
