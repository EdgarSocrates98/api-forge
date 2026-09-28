---
sdd: 1
feature: API_FORGE_ECONOMY_EVAL_INTEGRITY
phase: contract
profile: critical
status: draft
upstream:
  path: intent.md
  sha256: "455bb67cc6d5fb2b949bbd1d2dbc322dd65b0ec1fa92fecaf0531bd62b8de11c"
covers:
- agentic-quality-eval/v1
- economy-stats
- DeltaSlice/v1
api_ir:
  input: recorded corpus, min accuracy, baseline report, ledger rows, explicit changed paths and case dirs
  output: floor/baseline gates, eligible-only token coverage, run-scoped failures, refused paths
---
# contract

Additive: the agentic-quality report gains `min_accuracy`, `baseline_sha256`, `baseline_accuracy` and per-profile floor/baseline gates; `economy stats` gains `persist_failures_for_run`/`persist_failures_global`.
