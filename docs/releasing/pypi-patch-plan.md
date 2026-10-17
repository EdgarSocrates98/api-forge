# PyPI patch plan — apiforge-af

Cycle 11.2 (P1-004 + P1-006). Prepared for maintainer approval; nothing here
publishes, tags or uploads anything. Per repo governance, PRs are still opened
through the normal review flow — this document is a plan, not a release.

## Current state (audited in cycle 11.2)

| Signal | Value |
|---|---|
| PyPI published | `apiforge-af 0.1.0` (only release) |
| `pyproject.toml` | `0.1.0` — aligned |
| Git tag / GitHub release | `v0.1.0` — aligned |
| `requires-python` | `>=3.12` |
| CI before this PR | single `3.12` pin in every job (`validate`, `windows-parity`, `wheel-smoke`, `otel-collector`) |
| Classifiers before this PR | `Python :: 3.12` only |

**No version drift**: PyPI = pyproject = tag = GitHub release.

## What changes in this PR

1. **CI matrix** (`ci.yml`):
   - `validate` now runs on `["3.12","3.13","3.14"]` (ubuntu).
   - `windows-parity` — whose name already claimed "declared python range"
     while pinning one version — runs the same three versions on Windows.
   - `wheel-smoke` and `otel-collector` stay on 3.12 (artifact/collector
     contracts are version-agnostic; keeping them pinned preserves cost).
2. **Classifiers**: added `Python :: 3.13`, `Python :: 3.14` (deps resolve:
   pydantic, typer, cryptography>=50,<51, tree-sitter all install clean on
   3.13/3.14 — verified locally).
3. `project.urls` already complete (Homepage/Repository/Documentation/
   Changelog/Issues — all targets exist).

`uv.lock` is unchanged: `requires-python` and dependencies did not move, and
`scripts/lock_audit.py` audits the committed lock against pyproject — it still
passes.

## Proposed next release: `0.1.1` (patch)

Rationale: classifier corrections + CI coverage; no runtime/API/dependency
change.

### Provenance checklist for the maintainer

- [ ] `validate` green on all three legs; `windows-parity` green on all three.
- [ ] `python scripts/lock_audit.py` and `python scripts/check_release.py`.
- [ ] Bump `version = "0.1.1"` in `pyproject.toml` at release time.
- [ ] Tag `v0.1.1` after merge; publish via `publish-pypi.yml`.
- [ ] Verify PyPI classifiers show 3.12/3.13/3.14.

## Local smoke evidence (this PR)

- Interpreters: system `python3.12` (3.12.3); uv-managed 3.13.15, 3.14.7
  (plus 3.10/3.11 for sibling repos; below floor here).
- `uv pip install -e ".[dev,mcp]"` clean on **3.13** and **3.14**
  (cryptography, tree-sitter, pydantic resolve).
- `apiforge --version` → `apiforge 0.1.0` on both; `apiforge capabilities
  verify` runs (returns `verified: 0` outside a case context, as expected).
- `python -m build` wheel smoke on a uv-managed interpreter.

## Blockers

None observed locally: install + CLI smoke clean on 3.13 and 3.14. If a
3.14 leg fails in CI, drop only that leg and record the failure here —
do not silently narrow `requires-python`.
