---
sdd: 1
feature: API_FORGE_STEP11_AGENTOPS
phase: build
profile: critical
status: done
tasks:
  - id: B1
    summary: seven contracts + registry + exports + catalog code + contract docs
    files: [src/apiforge/contracts/agentops_report.py, src/apiforge/contracts/registry.py, src/apiforge/contracts/__init__.py, docs/contracts/, docs/catalog-contract.md]
  - id: B2
    summary: inspect + compare + waste modules and the detector policy
    files: [src/apiforge/agentops/inspect.py, src/apiforge/agentops/compare.py, src/apiforge/agentops/waste.py, src/apiforge/rules/agentops_waste.yaml]
  - id: B3
    summary: three CLI verbs + three MCP read tools + eval + corpus + tests
    files: [src/apiforge/cli.py, src/apiforge/mcp/tools.py, src/apiforge/evals/agentops.py, evals/corpus/agentops/, tests/agentops/test_inspect_waste.py, tests/mcp/test_tools.py]
claims:
  - "all 12 §56 WasteKinds implemented with declared thresholds"
  - "every finding labeled observed/estimated/hypothesis per §57"
  - "unresolved metrics never carry values; sections never drop"
upstream:
  path: plan.md
  sha256: "c8743b726f61cd911b69a8ec2e10078f948e4a6cafb7c7ccc7568de264df3632"
---

# build
