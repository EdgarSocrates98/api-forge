---
sdd: 1
feature: API_FORGE_STEP11_AGENTOPS
phase: architecture
profile: critical
status: done
files:
  - src/apiforge/contracts/agentops_report.py
  - src/apiforge/contracts/registry.py
  - src/apiforge/contracts/__init__.py
  - src/apiforge/agentops/inspect.py
  - src/apiforge/agentops/compare.py
  - src/apiforge/agentops/waste.py
  - src/apiforge/rules/agentops_waste.yaml
  - src/apiforge/cli.py
  - src/apiforge/mcp/tools.py
  - src/apiforge/evals/agentops.py
  - evals/corpus/agentops/
  - tests/agentops/test_inspect_waste.py
decisions:
  - "sections never drop: every §54 section renders with unresolved metrics when its source is absent"
  - "memory scope is store-wide; metrics report estimated, not per-run"
  - "compare axes carry deterministic direction; absence never ties"
  - "detector thresholds live in rules/agentops_waste.yaml, not in code"
upstream:
  path: contract.md
  sha256: "dc958a96e8fe3a7d4b05628ccf7fc05dcd0316f9274104b95296d2c8ee3621bf"
---

# architecture

inspect.py joins `run_ledger.entries`, `token_ledger.load_entries`,
`read_spans`, `uses_from_ledger`+`evaluate`, the memory store jsonl files
and the decision-gates jsonl. compare.py composes two inspections. waste.py
reads the same inputs plus the declared detector policy.
