---
sdd: 1
feature: API_FORGE_ECONOMY_EVAL_INTEGRITY
phase: architecture
profile: critical
status: draft
upstream:
  path: contract.md
  sha256: "b5d4f82456b2a009942c3eff8649dbaabaf7f12b83f9b862d2a6602de93902c7"
files:
- src/apiforge/evals/agentic_quality.py
- src/apiforge/rules/token_eligibility.yaml
- src/apiforge/economy/run_ledger.py
- src/apiforge/evals/hardening.py
- src/apiforge/security/source_paths.py
- src/apiforge/context/delta.py
- src/apiforge/context/gateway/capsule.py
- src/apiforge/evidence/resolve.py
decisions:
- id: floor-plus-baseline
  decision: every profile must reach min_accuracy and not regress vs deep or a baseline
  rollback: drop the floor gates
- id: declarative-eligibility
  decision: model-facing verb prefixes plus measured rows form the denominator
  rollback: edit rules/token_eligibility.yaml
- id: production-oracle
  decision: hardening eval calls plan_roles and build_delta on an analyzed fixture
  rollback: none needed
- id: confine-explicit-paths
  decision: --changed items and case dirs pass the AllowedRoots resolver
  rollback: revert confine_dir callers
---
# architecture

Two waves: E1 certification semantics, E2 production-path oracle and explicit path confinement.
