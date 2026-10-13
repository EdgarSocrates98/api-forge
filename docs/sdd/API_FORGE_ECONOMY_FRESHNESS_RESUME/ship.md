---
sdd: 1
feature: API_FORGE_ECONOMY_FRESHNESS_RESUME
phase: ship
profile: standard
status: draft
upstream:
  path: secure.md
  sha256: "da91c1634d70ec02a3818c99e3bc75157041a09630f660d6777c96b1033550dc"
deviations:
- window-measured-from-pack-verified-date
- keyword-declared-question-classes
evidence:
- path: sdd/API_FORGE_ECONOMY_FRESHNESS_RESUME/evidence/economy-freshness-eval.json
  sha256: f5a162ffd6ae63e48c6548879239551400001611dfe6803bb2310d9d756eedcf
- path: sdd/API_FORGE_ECONOMY_FRESHNESS_RESUME/evidence/economy-freshness-tests.txt
  sha256: 96c3a93a3e1d689ba3bf4329abc14e0d12a2052073ca546f5e4946446b412cd6
---
# ship

Ready for review. The freshness window is measured from the pack's `verified` date, not from the manifest observation. Question classes come from declared terms; an ambiguous question stays local first and is flagged `escalate_if_unanswered`.
