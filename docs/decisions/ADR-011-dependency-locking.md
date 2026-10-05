# ADR-011: dependency locking strategy — declared ranges + vendored assets

## Status

Accepted — 2026-10-06.

## Context

§30 asks to approach Spark Forge robustness on CI and supply chain,
including "locked dependencies". Spark Forge pins every transitive
dependency in a lockfile and installs with `--require-hashes`.

API Forge today declares bounded ranges in `pyproject.toml`
(`>=x,<y`), vendors its critical compression assets under `vendor/` with
a `MANIFEST.sha256` gate, and runs `pip check`, the vendor parity check
and the offline `scripts/supply_chain_audit.py` in CI.

## Decision

Keep declared ranges for library dependencies; do not introduce a
lockfile at this stage.

| option | chosen | because |
|--------|--------|---------|
| pip-tools/uv lockfile for all deps | no | API Forge is installed as a library (`pip install -e .[dev]`); a lockfile governs the app's environment, not the library's resolved graph, and would duplicate the range policy in two places that drift silently |
| bounded ranges + vendored assets | yes | ranges keep the library installable across the declared Python range; `vendor/` pins the assets that actually execute; the manifest gate makes drift a hard failure |
| hash-locked requirements for CI | revisit | `pip download --require-hashes` only helps the CI image, not consumers; if CI supply-chain risk grows, the wheel-smoke job can adopt `--require-hashes` against a generated requirements file without changing the library contract |

## Consequences

- `scripts/supply_chain_audit.py` enforces the declared-range
  invariant (every dependency must carry a bound), runs `pip check`,
  verifies vendor parity, checks eval corpus consistency and reports
  the MCP surface count.
- CVE/advisory scanning remains a declared external boundary — the
  audit reports it `unresolved` rather than pretending an offline CVE
  feed exists.
- Revisit trigger: a second consumer needs byte-identical CI installs,
  or an upstream yank incident hits the project.
