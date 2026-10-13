---
sdd: 1
feature: API_FORGE_STEP11_AGENTOPS
phase: contract
profile: critical
status: done
covers:
  - run-inspection
  - inspection-sections
  - evidence-labeled-metrics
  - waste-findings
  - run-comparison
  - cli-mcp-surface
  - eval-corpus
contracts:
  - RunInspection/v1
  - InspectionSection/v1
  - InspectionMetric/v1
  - WasteFinding/v1
  - WasteReport/v1
  - RunComparison/v1
  - ComparisonAxis/v1
refusals:
  - "AF-AGENTOPS-WASTE-POLICY: waste policy file unreadable or detectors mapping missing"
upstream:
  path: intent.md
  sha256: "6a208744b32169a0ed679e616ffec784d4dd74547b50e1ff5d39101ddd7f96c6"
---

# contract

`InspectionMetric` enforces the §57 invariant structurally: `unresolved`
metrics carry `value: null` and a non-empty `detail` naming the missing
basis; `observed`/`estimated` require a value.
