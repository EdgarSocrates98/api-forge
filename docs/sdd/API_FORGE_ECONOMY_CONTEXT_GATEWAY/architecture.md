---
sdd: 1
feature: API_FORGE_ECONOMY_CONTEXT_GATEWAY
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "37b225cc57c36bb52ae7576449cc75ad6a966555cb50e297432f1d5e7cd95316"
files:
  - src/apiforge/contracts/context.py
  - src/apiforge/contracts/economy.py
  - src/apiforge/context/gateway/canonical.py
  - src/apiforge/context/gateway/refs.py
  - src/apiforge/context/gateway/dedup.py
  - src/apiforge/context/gateway/levels.py
  - src/apiforge/context/gateway/capsule.py
  - src/apiforge/economy/run_ledger.py
  - src/apiforge/evals/economy.py
  - src/apiforge/cli_context.py
  - src/apiforge/cli_economy.py
  - src/apiforge/mcp/tools.py
decisions:
  - id: hash-identity
    decision: ctx refs are sha256 of LF-normalized content in repo-local .apiforge/ctx
    rollback: remove context/gateway and the ctx store directory
  - id: single-ledger
    decision: attribution rows share economy.jsonl with payload_bytes 0 so economy report is unchanged
    rollback: remove run_ledger.py; legacy rows are untouched
  - id: partial-not-crash
    decision: budget exhaustion and missing case return explicit partial capsules; integrity errors refuse
    rollback: map partial statuses to refusals
  - id: conservative-baseline
    decision: baseline is context resolve plus whole evidence files; capsule is charged full expansion
    rollback: re-record baseline.json
---
# architecture

Layering: contracts → economy → context/gateway → evals/economy → CLI/MCP.
Selection walks the persisted case graph (operation → implemented_by route
fact, described_by contract, backed_by findings via `assess_graph_impact`),
never executing consumer code or calling a provider.
