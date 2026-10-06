---
sdd: 1
feature: API_FORGE_STEP11_CONTROL_PLANE
phase: plan
profile: critical
status: done
tasks:
  - id: G1
    covers: [control-plane-contracts, route-lifecycle, shadow-records]
    test: sdd/API_FORGE_STEP11_CONTROL_PLANE/evidence/G1.txt
  - id: G2
    covers: [promotion-gates, fallback-routing, cli-mcp-surface]
    test: sdd/API_FORGE_STEP11_CONTROL_PLANE/evidence/G2.txt
  - id: G3
    covers: [eval-corpus, cli-smoke]
    test: sdd/API_FORGE_STEP11_CONTROL_PLANE/evidence/G3.txt
upstream:
  path: architecture.md
  sha256: "b8a10e67e9bf40f98900fbc1409e8832ad81d2240846cc79b54b040337f4b889"
---

# plan
