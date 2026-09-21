# API Forge Plan 10 — Release Evidence Bundle + `report sign/verify`

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans task-by-task.

**Goal:** The release evidence bundle — one canonical `report.json` composing case manifest + receipt + catalog/policy digests + finding counts — plus `report sign` (signature block pinning body/evidence/catalog hashes) and `report verify` naming **which part diverged**: `signature_version` | `body` | `evidence` | `catalog`. Proves correspondence, never authorship (no keys, per ADR-005).

## Tasks

- [ ] T1: `apiforge/report/` — `bundle.py` (`build_report(case, receipt?, now)`), `sign.py` (`sign_report`, `verify_report`), catalog digest helper; tests round-trip + per-part divergence
- [ ] T2: CLI `report build|sign|verify`; verify exits 4 on divergence, `AF-REPORT-UNSIGNED` when no signature
- [ ] T3: gate parity `AF-REPORT` + docs + threat row; spec row 10 → entregue; commit

## Acceptance

- sign→verify round-trip ok; tampering body/evidence/catalog each named in `diverged`
- unsigned report → `AF-REPORT-UNSIGNED`; pytest/ruff/mypy/gate green
