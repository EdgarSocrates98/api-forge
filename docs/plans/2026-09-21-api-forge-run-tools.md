# Plan 19 — `run <tool>`: execute the scanners, then read their reports

**Goal:** the report readers stay pure, but `apiforge run <tool>` closes the
loop — a closed allowlist (`semgrep`, `trivy`, `gitleaks`, `k6`) executed via
fixed argv templates (no shell, `--timeout`, binary resolved by
`shutil.which`). The produced report feeds the existing reader in the same
call. Missing binary → `AF-RUN-TOOL-MISSING` naming the install path;
`--dry-run` prints argv without executing. `zap` is deliberately absent —
baseline needs a daemon/docker, not a bare binary.

- [ ] T1: `run_tools.py` — TOOLS table (argv template, report path flag, reader import), subprocess no-shell + timeout
- [ ] T2: `run` CLI group + `--dry-run` + tests (monkeypatched which/run) + threat-model row + docs/gate parity
