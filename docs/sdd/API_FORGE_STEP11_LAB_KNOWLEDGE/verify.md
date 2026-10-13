---
sdd: 1
feature: API_FORGE_STEP11_LAB_KNOWLEDGE
phase: verify
profile: critical
status: done
results:
  - "focused tests: 26 passed, 1 skipped (tests/knowledge/test_evolution.py, tests/labs/test_scenarios.py, tests/runtime/test_agentic_doctor.py, tests/knowledge/test_freshness.py, tests/mcp/test_tools.py)"
  - "evals knowledge-drift: 5/5 — verified, stale, conflicted (1 pair named), deprecated, unresolved"
  - "lab scenarios: 13 kinds — 8 covered, 5 declared-gap, 0 unresolved"
  - "doctor --agentic: status attention — sdd chain gap (this feature pre-ship) + economy info findings; memory + telemetry planes unresolved without stores"
  - "knowledge impact: 40 packs, 342 nodes, 454 edges; agent->knowledge unresolved named"
  - "mcp audit: 0 findings, 1 accepted exception, 151 tools"
  - "supply_chain_audit: ok — vendor parity confirmed, 29 corpora/195 cases, surface_lock 151; CVE + pip-in-uv-venv unresolved"
  - "routing/scorecard regression after FreshnessState widening: 40 passed"
  - "Ruff over changed surface: clean; 986 files formatted"
  - "mypy src/apiforge: no issues in 557 source files"
upstream:
  path: build.md
  sha256: "b9dd256ba166a8619350fa4191418dd9f583757d9e62769538bef3dcb01d0911"
---

# verify

Evidence files:

- `evidence/G1-focused-tests.txt` — pytest tail
- `evidence/G2-evals.txt` — eval, lab, doctor, impact, audit outputs
- `evidence/G3-gates.txt` — Ruff + format + mypy

The full-suite run and remaining platform gates (release gate,
capabilities verify, agents drift, vendor check, sdd check) are
executed in the final wave and recorded in the case journal.
