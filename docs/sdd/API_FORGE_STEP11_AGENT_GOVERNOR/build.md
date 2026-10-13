---
sdd: 1
feature: API_FORGE_STEP11_AGENT_GOVERNOR
phase: build
profile: critical
status: done
tasks:
  - id: B1
    summary: governance contracts + registry + exports + contract docs
    files: [src/apiforge/contracts/agentic_governance.py, src/apiforge/contracts/registry.py, src/apiforge/contracts/__init__.py, docs/contracts/]
  - id: B2
    summary: governor/gain/stop/recovery/loop primitives + policy yaml
    files: [src/apiforge/governance/, src/apiforge/rules/governor_policy.yaml, src/apiforge/rules/recovery_policy.yaml]
  - id: B3
    summary: governor CLI app, MCP tools, eval corpus, AF codes, tests
    files: [src/apiforge/cli_governor.py, src/apiforge/cli.py, src/apiforge/mcp/tools.py, src/apiforge/evals/agent_governor.py, evals/corpus/agent-governor/, tests/, docs/catalog-contract.md]
claims:
  - "the risk floor is monotone: irreversible/high risk can only raise the
    profile, never lower it"
  - every clamp applied is named in GovernorDecision.clamped_by; absent input
    signals land in unresolved
  - gain is a deterministic weighted mean over present signals; unresolved
    signals are dropped, never zeroed
  - "stop fails closed: unmeasurable gain => AF-GOV-GAIN-UNRESOLVED; below
    threshold => AF-GOV-STOP-LOW-GAIN"
  - "recovery classes are a closed vocabulary; unknown classes refuse
    AF-GOV-FAILURE-CLASS-UNKNOWN and exhausted caps fire the terminal step"
upstream:
  path: plan.md
  sha256: "7355e350a5048c8c9e74fa0185712e34efef50835cdb5e0b53e63c76b7f1ddaf"
---

# build
