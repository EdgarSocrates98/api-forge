# API Forge Plans 7+8 — Test & Security Report Adapters

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans task-by-task.

**Goal:** Offline readers for the standard report formats of the API test/security toolchain — `model pact|schemathesis|k6|coverage` and `model zap|semgrep|trivy|gitleaks` — each emitting facts + named diagnostics, never running the tool.

**Architecture:** `adapters/testreports.py` and `adapters/secreports.py` share the established dump-reader shape (`_load`/`_diag`/`_fact` → `CodeInventory`). Missing/invalid reports are `AF-TEST-REPORT-*` / `AF-SEC-REPORT-*`. Gitleaks extracts rule/file/line — **never the secret**. These facts are evidence for `rules lookup` and coordinators; they do not feed `judge_api_model` (that path is contract↔code only) — recorded decision.

**Facts (bounded):**
- `test.pact.contract` — consumer, provider, interactions, methods, paths
- `test.schemathesis.run` — totals + check verdict counts
- `test.k6.summary` — vus_max, iterations, p95 latency, fail rate, checks rate
- `test.coverage.py` — percent, statements, missing lines, file count
- `sec.zap.report` — alerts by risk level
- `sec.semgrep.report` — findings by severity + rule ids
- `sec.trivy.report` — vulnerabilities by severity per target
- `sec.gitleaks.report` — leak count by rule/file (no secret material)

## Tasks

- [ ] T1: `testreports.py` + fixtures (pact json, schemathesis report, k6 summary-export, coverage json) + tests
- [ ] T2: `secreports.py` + fixtures (zap, semgrep, trivy, gitleaks json) + tests
- [ ] T3: CLI `model <name>` ×8 + gate parity (`AF-TEST`/`AF-SEC` rows) + docs + threat row + commit

## Acceptance

- Each reader: valid fixture → expected facts; missing file → named diagnostic; malformed → named diagnostic
- No secret values in any gitleaks fact (asserted in tests)
- pytest/ruff/mypy/gate green
