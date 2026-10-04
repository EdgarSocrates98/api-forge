---
sdd: 1
feature: API_FORGE_STEP11_AGENTOPS
phase: verify
profile: critical
status: done
results:
  - "focused tests: 18 passed, 1 skipped (inspect/compare/waste + MCP surface)"
  - "evals agentops: 4/4 cases (sections, detection, verdicts, missing-run honesty)"
  - "CLI smoke: inspect ghost -> unresolved sections; waste ghost -> empty findings with named basis; compare -> unresolved axes"
  - "Ruff over new/changed files: clean; format: clean"
  - "mypy strict over agentops modules: no issues"
upstream:
  path: build.md
  sha256: "b9022dd8c09598b7a92dab4fc7b571ac28c27d0f630095f7551ba183727d3cb0"
---

# verify

Evidence files:

- `evidence/G1-focused-tests.txt` — pytest tail
- `evidence/G2-evals.txt` — eval totals
- `evidence/G3-gates.txt` — Ruff + format + mypy output
