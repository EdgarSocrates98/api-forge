---
sdd: 1
feature: API_FORGE_EVOLUTION1_GOVERNED_BUDGETS
phase: architecture
profile: critical
status: done
files:
  - src/apiforge/contracts/agentic_governance.py
  - src/apiforge/governance/budget.py
  - src/apiforge/cli_economy.py
  - src/apiforge/mcp/tools.py
decisions:
  - id: exact-hierarchy
    summary: match task, phase, role and tool limits by exact ids
    rollback: remove the new budget surface; preserve existing economy records
  - id: observed-token-only
    summary: refuse enforcement when a declared token limit lacks measured tokens
    rollback: keep non-token dimensions and report token state unresolved
  - id: preappend-admission
    summary: evaluate every spend before writing its receipt
    rollback: retain plan and diagnostic logs without recording rejected spend
upstream:
  path: contract.md
  sha256: "d845150baabf036c910b6aed43f9496d12938c210a0dec6efbb4f0c897086025"
---

# architecture

`governance/budget.py` stores plans and spends as JSONL under
`.apiforge/economy/agentic-budget/`. Matching is deterministic: each limit
applies to its exact scope id, historical spend is summed from the same plan,
and the proposed cost is evaluated before append. CLI and MCP call the same
service. The semantic checkpoint can reference the plan and decision without
coupling transcript state to economy state.
