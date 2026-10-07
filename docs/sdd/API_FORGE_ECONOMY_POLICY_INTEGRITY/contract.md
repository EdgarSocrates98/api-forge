---
sdd: 1
feature: API_FORGE_ECONOMY_POLICY_INTEGRITY
phase: contract
profile: critical
status: draft
upstream:
  path: intent.md
  sha256: "7c00043081a535cdbdfc5d80e36d147fc502db4dc50828cebf551e6fe25066ef"
covers:
- BenchmarkIdentity/v1
- agentic-quality-eval/v1
- github-ruleset-plan/v1
api_ir:
  input: corpus, baseline report, token eligibility rule, ruleset JSON
  output: identity-checked gates, fail-closed coverage, CODEOWNERS, ruleset payload and warnings
---
# contract

Adds `BenchmarkIdentity/v1`; agentic-quality reports gain `benchmark_identity` and `baseline_scope`.
