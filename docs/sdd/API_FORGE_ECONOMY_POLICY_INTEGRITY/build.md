---
sdd: 1
feature: API_FORGE_ECONOMY_POLICY_INTEGRITY
phase: build
profile: critical
status: draft
upstream:
  path: plan.md
  sha256: "63a370e728d3fb99c3d95d7741128a255d46268ea72f55df6473504fc2b75322"
tasks:
- id: p1-benchmark-policy
  status: done
  evidence: sdd/API_FORGE_ECONOMY_POLICY_INTEGRITY/evidence/policy-integrity-tests.txt
- id: p2-governance
  status: done
  evidence: sdd/API_FORGE_ECONOMY_POLICY_INTEGRITY/evidence/ruleset-plan.json
claims:
- benchmark-identity
- strict-baseline
- fail-closed-token-policy
- codeowners
- ruleset-plan
---
# build

Implemented `BenchmarkIdentity/v1` with strict baselines and `--allow-cross-corpus-baseline`, the fail-closed eligibility parser, `.github/CODEOWNERS` and the read-only `scripts/github_ruleset_plan.py` with the governance guide.
