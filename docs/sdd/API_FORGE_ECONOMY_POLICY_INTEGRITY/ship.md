---
sdd: 1
feature: API_FORGE_ECONOMY_POLICY_INTEGRITY
phase: ship
profile: critical
status: draft
upstream:
  path: benchmark.md
  sha256: "c6630740e2dad0a12fff293ead91143bd031fca9603c5b725779ba08ecfb1bfb"
deviations:
- ruleset-applied-by-owner
evidence:
- path: sdd/API_FORGE_ECONOMY_POLICY_INTEGRITY/evidence/agentic-quality-baseline.json
  sha256: ec489295943ac7ee1f8c17b240d945a0c5aef6724672274aaa64b9bb63a857c1
- path: sdd/API_FORGE_ECONOMY_POLICY_INTEGRITY/evidence/policy-integrity-tests.txt
  sha256: 938dbb028c4ccc117a67ee442f104146488dc7585b7a401f222d7e32875ae977
- path: sdd/API_FORGE_ECONOMY_POLICY_INTEGRITY/evidence/ruleset-plan.json
  sha256: a4c5c60db3c695ca034e52fd2b95891a1aae3fd070816e54bfdc290e5a24ca84
---
# ship

Ready for review. The `protect` ruleset changes only when the owner applies the plan (`docs/guides/API_FORGE_GITHUB_GOVERNANCE.en.md`); until then it targets no branch.
