---
sdd: 1
feature: API_FORGE_ECONOMY_POLICY_INTEGRITY
phase: intent
profile: critical
status: draft
upstream:
  path: discover.md
  sha256: "bdee326a6b502bf7f588c7dccb45449a8d9aa08b7e4d31e90f2bdac4cfa45ed4"
problem: 'Configuration could still mislead certification: foreign or partial baselines, an emptied
  eligibility policy, and a GitHub ruleset that targets no branch with no required checks and a missing
  CODEOWNERS.'
success:
- benchmark-identity
- strict-baseline
- fail-closed-token-policy
- codeowners
- ruleset-plan
out_of_scope:
- applying-the-ruleset
- new-economy-features
owner: api-forge-economy
risk_class: high
risk_signals:
- path:.github/CODEOWNERS
- path:scripts/github_ruleset_plan.py
---
# intent

Make certification impossible to fake by configuration and make declared governance appliable.
