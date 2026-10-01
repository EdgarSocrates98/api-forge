---
sdd: 1
feature: API_FORGE_ECONOMY_TOOL_HOST
phase: ship
profile: standard
status: draft
upstream:
  path: secure.md
  sha256: "aa1a357b4198f04509ff3eab27d0b5a9bdebfe94e9b80d8d2669824cab9acbe6"
deviations:
- compact-output-target-65-percent
- deferred-tool-hosts-bound-surface-savings
evidence:
- path: sdd/API_FORGE_ECONOMY_TOOL_HOST/evidence/tool-economy-eval.json
  sha256: ae9ba51a2bce0e7228ee6c20b7da8f87a62d03c53615f227ff60dc75f6a612e2
- path: sdd/API_FORGE_ECONOMY_TOOL_HOST/evidence/tool-host-tests.txt
  sha256: 89c98f3097878e8fe120c954b574f8faa37738a0155fbdad68a1df25e1576b6b
---
# ship

Ready for review. The compact-output target was revised from 60% to 65% after measurement: lossless pruning and minification save about 37%, and capsules are content-dominated. On hosts with deferred tool loading (declared for Claude) the compact surface saves less than its 94% byte reduction suggests — the projection records that.
