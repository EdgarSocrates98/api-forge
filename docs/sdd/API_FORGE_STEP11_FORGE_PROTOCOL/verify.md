---
sdd: 1
feature: API_FORGE_STEP11_FORGE_PROTOCOL
phase: verify
profile: critical
status: done
results:
  - "focused tests: 26 passed, 1 skipped (tests/forge 21 + MCP registry expectations incl. 5 forge tools)"
  - "wider focused wave: 42 passed, 1 skipped (forge + mcp surface_v2 + tools)"
  - "evals forge-protocol: 4/4 cases (lifecycle, completed-run, refusal gates, unresolved honesty)"
  - "CLI smoke: capabilities -> 20+ descriptors; submit/status/attach/result/evidence/handoff/health E2E; AF-FORGE-ENGINE-UNKNOWN / AF-FORGE-RISK-GATE / AF-FORGE-CAPABILITY-UNKNOWN / AF-FORGE-TASK-EXISTS all observed"
  - "mcp audit post-registration: 0 findings, 1 accepted, 148 tools — the 5 forge tools introduce no hygiene findings"
  - "Ruff over new/changed files: clean; format: clean"
  - "mypy strict over forge/cli_forge/evals/contracts: no issues"
upstream:
  path: build.md
  sha256: "c9a070317950049062c2de5b4fd9c8e10b422b03847f32fab80fdcc0f81ae248"
---

# verify

Evidence files:

- `evidence/G1-focused-tests.txt` — pytest tail
- `evidence/G2-evals.txt` — eval totals
- `evidence/G3-gates.txt` — Ruff + format + mypy output
