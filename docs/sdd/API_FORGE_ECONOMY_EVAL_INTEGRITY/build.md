---
sdd: 1
feature: API_FORGE_ECONOMY_EVAL_INTEGRITY
phase: build
profile: critical
status: draft
upstream:
  path: plan.md
  sha256: "5cff56f4f4dc1bff55946de1ff564f5daedc8e38f06b7157b1dd9ece5e1aa7e1"
tasks:
- id: e1-certification
  status: done
  evidence: sdd/API_FORGE_ECONOMY_EVAL_INTEGRITY/evidence/eval-integrity-tests.txt
- id: e2-oracle-paths
  status: done
  evidence: sdd/API_FORGE_ECONOMY_EVAL_INTEGRITY/evidence/economy-hardening-eval.json
claims:
- quality-floor
- baseline-non-regression
- token-eligibility
- run-scoped-failures
- production-oracle
- explicit-path-confinement
---
# build

Implemented the agentic-quality floor and baseline gates (CLI/MCP), `rules/token_eligibility.yaml` with `is_token_eligible`, run-scoped persist failures, the hardening oracle on `plan_roles`/`build_delta` with a contract-invariant case, and `confine_dir` plus confined `--changed` normalization.
