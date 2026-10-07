---
sdd: 1
feature: API_FORGE_STEP11_TOKEN_ECONOMICS
phase: architecture
profile: critical
status: done
files:
  - src/apiforge/contracts/token_economics.py
  - src/apiforge/economy/token_ledger.py
  - src/apiforge/economy/pricing.py
  - src/apiforge/economy/reconciliation.py
  - src/apiforge/rules/provider_pricing.yaml
  - src/apiforge/evals/token_economics.py
  - src/apiforge/cli_economy.py
  - src/apiforge/mcp/tools.py
  - src/apiforge/contracts/registry.py
  - src/apiforge/contracts/__init__.py
  - evals/corpus/token-economics/
  - tests/contracts/test_token_economics.py
  - tests/economy/test_token_ledger.py
  - tests/economy/test_pricing.py
  - tests/economy/test_reconciliation.py
decisions:
  - usage rows live in a separate append-only token_usage ledger; the v1
    attribution ledger (economy.jsonl) is never rewritten
  - pricing resolves by effective_at horizon; future-dated rows never leak
    into the past and at=None picks the latest declared row
  - reconciliation compares axes only when both sides carry a value; a zero
    estimate against a positive observation stays unresolved
  - MCP exposes read tools only (ledger/pricing/reconcile); record-usage
    stays a CLI write verb
upstream:
  path: contract.md
  sha256: "cb1c79a77dbec8f87e687c2d9dd86adb6a650c7fdf2fb933f764199920e6cda1"
---

# architecture
