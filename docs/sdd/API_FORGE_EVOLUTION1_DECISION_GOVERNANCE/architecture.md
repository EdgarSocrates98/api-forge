---
sdd: 1
feature: API_FORGE_EVOLUTION1_DECISION_GOVERNANCE
phase: architecture
profile: critical
status: done
upstream:
  path: contract.md
  sha256: "2adcb8385381949cbe8b1d6212d117b3f6c61db50266c8f99bd12d1c6b56e181"
files: [src/apiforge/contracts/agentic_governance.py, src/apiforge/governance/decision.py, src/apiforge/cli_agentic_state.py, src/apiforge/mcp/tools.py]
decisions:
  - id: default-deny-mutation
    summary: default policy disallows external mutation
    rollback: remove projection while retaining request/result contracts
  - id: approval-is-artifact
    summary: only ApprovalGate status can satisfy a human gate
    rollback: all risky requests remain review/block
---

# architecture

The pure evaluator is shared by local CLI and MCP. It only records the result;
it never invokes the proposed action.
