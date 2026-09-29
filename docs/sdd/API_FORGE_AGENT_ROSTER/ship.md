---
sdd: 1
feature: API_FORGE_AGENT_ROSTER
phase: ship
profile: critical
status: draft
upstream:
  path: benchmark.md
  sha256: "82822735b82042a4c9b267382c0e31e80aaba916bc43bffd15109aaa1baae4f0"
deviations:
- aliases-count-33-not-27
- agentic-quality-baseline-not-re-recorded
- golden-gain-confounded-by-language-and-leakage
- claude-bash-not-narrowed
- release-gate-orphan-readme-preexisting
evidence:
- path: sdd/API_FORGE_AGENT_ROSTER/evidence/agentic-quality.json
  sha256: 2728f2dc07c2404d4d1dad7e6fce6daf71dfcf700bd1fe7a056f43158ed6c2f5
- path: sdd/API_FORGE_AGENT_ROSTER/evidence/audit.json
  sha256: 2e593766b254c70454bf10b2b09748c7d05d874f136a931285734d675bc9484e
- path: sdd/API_FORGE_AGENT_ROSTER/evidence/economy-hardening.json
  sha256: 3da296adcc93e8f4a3979feda2ff5ffd3fb18cd56f7330b51d0c9e4a8c1214bb
- path: sdd/API_FORGE_AGENT_ROSTER/evidence/full-suite.txt
  sha256: f8719dd81925933ae6e838f616f99d8050261ea5abbba69b98910415949c7f65
- path: sdd/API_FORGE_AGENT_ROSTER/evidence/holdout-baseline-52.json
  sha256: 946a6e3ecad84084fa918a3a41d3ab49a92ba25fca33b7cb8e5a53db397f4426
- path: sdd/API_FORGE_AGENT_ROSTER/evidence/holdout-candidate-25.json
  sha256: efbac0b2a6e380c4f21acc408934f24e8375bf9d0ad93715f1206f029fd4980e
- path: sdd/API_FORGE_AGENT_ROSTER/evidence/lint.json
  sha256: 53ab547091adc7436e84bf6372668696356fe384cafef362d883ed58093a0558
- path: sdd/API_FORGE_AGENT_ROSTER/evidence/routing-baseline.json
  sha256: a09235c5cea93b3e9fbd233a95634d70e58085862df4873e96f890d77989c7b7
- path: sdd/API_FORGE_AGENT_ROSTER/evidence/routing-candidate.json
  sha256: 1e8798d035cdc24f88e8cc4bd1fc17aa0820f6f0069921fe3065695597f95a7d
---
# ship

25 contract-complete agents rendered for Claude, Devin and Codex, gated by drift, lint, references and audit; old names resolve with a deprecation warning until roster-v2.
