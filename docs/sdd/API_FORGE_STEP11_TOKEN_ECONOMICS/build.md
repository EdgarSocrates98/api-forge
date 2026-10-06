---
sdd: 1
feature: API_FORGE_STEP11_TOKEN_ECONOMICS
phase: build
profile: critical
status: done
tasks:
  - id: B1
    summary: contracts + registry + exports + contract docs
    files: [src/apiforge/contracts/token_economics.py, src/apiforge/contracts/registry.py, src/apiforge/contracts/__init__.py, docs/contracts/]
  - id: B2
    summary: token ledger, pricing catalog, reconciliation engine
    files: [src/apiforge/economy/token_ledger.py, src/apiforge/economy/pricing.py, src/apiforge/economy/reconciliation.py, src/apiforge/rules/provider_pricing.yaml]
  - id: B3
    summary: CLI verbs, MCP read tools, eval corpus, catalog codes, tests
    files: [src/apiforge/cli_economy.py, src/apiforge/cli.py, src/apiforge/mcp/tools.py, src/apiforge/evals/token_economics.py, evals/corpus/token-economics/, tests/]
claims:
  - observed/estimated/unresolved bases never mix inside a ledger sum;
    unresolved rows are counted, not added
  - no price is hardcoded in source; the catalog is declared yaml data
    resolved by effective_at
  - calibration error exists only where both sides carry a value; gaps stay
    named in unresolved
  - AF-ECONOMY-PRICING-MISSING refuses inferred prices with field+unlock
upstream:
  path: plan.md
  sha256: "bb43cf7034568af14b8043c0af7eb6b91b30ff263bc795bd5506a6b451bca86a"
---

# build
