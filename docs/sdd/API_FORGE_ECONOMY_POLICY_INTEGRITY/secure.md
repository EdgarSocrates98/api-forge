---
sdd: 1
feature: API_FORGE_ECONOMY_POLICY_INTEGRITY
phase: secure
profile: critical
status: draft
upstream:
  path: verify.md
  sha256: "e2d0060fee35ba9463b533f3fe1bcd5c94350b6cad563c1dce30365dfad21a86"
threat_model: docs/security/threat-model-mvp.md
---
# secure

No remote mutation: the ruleset plan is a pure transform of a JSON the owner fetched; `scripts/github_pr_host.py` stays the only mutation boundary. The bypass trade-off is explicit in the plan warnings and the governance guide.
