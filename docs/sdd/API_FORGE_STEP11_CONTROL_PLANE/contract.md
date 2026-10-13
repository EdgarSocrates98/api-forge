---
sdd: 1
feature: API_FORGE_STEP11_CONTROL_PLANE
phase: contract
profile: critical
status: done
covers:
  - control-plane-contracts
  - route-lifecycle
  - shadow-records
  - promotion-gates
  - fallback-routing
  - cli-mcp-surface
  - eval-corpus
contracts:
  - ControlPlaneRoute/v1
  - ShadowRecord/v1
  - PromotionEvidence/v1
  - PromotionDecision/v1
  - FallbackDecision/v1
  - RouteDecision/v1
upstream:
  path: intent.md
  sha256: "6b13630b4dc5e35fe8c019e4c769b323145bf7d4dbb1d09c9013622b08b5303d"
---

# contract
