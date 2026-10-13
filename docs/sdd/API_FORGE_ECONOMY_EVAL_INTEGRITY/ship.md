---
sdd: 1
feature: API_FORGE_ECONOMY_EVAL_INTEGRITY
phase: ship
profile: critical
status: draft
upstream:
  path: benchmark.md
  sha256: "c90afd930d0be0663141a6cc4eef8bff03a2d31b07238a4d2340cdcb188845e1"
deviations:
- refused-changed-path-blocks-the-delta
evidence:
- path: sdd/API_FORGE_ECONOMY_EVAL_INTEGRITY/evidence/agentic-quality-eval.json
  sha256: a7f4a18f40dbbf88d1e5bbaae2e4ef64ae57482afd3e96727b271709812f9eda
- path: sdd/API_FORGE_ECONOMY_EVAL_INTEGRITY/evidence/economy-hardening-eval.json
  sha256: 3da296adcc93e8f4a3979feda2ff5ffd3fb18cd56f7330b51d0c9e4a8c1214bb
- path: sdd/API_FORGE_ECONOMY_EVAL_INTEGRITY/evidence/eval-integrity-tests.txt
  sha256: 960376ae972cb2f7a8b16b9d62be13d952196d99f8f9d664ccf8f7780b1a9d12
---
# ship

Ready for review. A refused `--changed` path makes the delta `unresolved`: the impact of a file that cannot be read is unknown.
