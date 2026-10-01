---
sdd: 1
feature: API_FORGE_ECONOMY_ARCH_HARDENING
phase: architecture
profile: critical
status: draft
upstream:
  path: contract.md
  sha256: "8cad2751f396aae67e0ea77d6d76a160ae076824c0b24c044957dcde870d7f24"
files:
- src/apiforge/security/source_paths.py
- src/apiforge/case/service.py
- src/apiforge/context/gateway/levels.py
- src/apiforge/evidence/resolve.py
- src/apiforge/runtime/role_context.py
- src/apiforge/runtime/control.py
- src/apiforge/runtime/supervisor.py
- src/apiforge/economy/run_ledger.py
- src/apiforge/runtime/economy.py
- src/apiforge/cache/store.py
- src/apiforge/knowledge/selector.py
- src/apiforge/knowledge/retrieval.py
- src/apiforge/evals/hardening.py
- src/apiforge/evals/agentic_quality.py
- .github/workflows/ci.yml
decisions:
- id: one-resolver-refuse-per-ref
  decision: paths confined to project and declared workspace roots after symlinks; refused refs are unresolved
  rollback: revert source_paths.py callers
- id: one-case-reader
  decision: gateway, evidence and delta read cases through load_verified_case only
  rollback: none needed
- id: class-pools
  decision: share x context_bytes is a class total split across instances
  rollback: revert role_context pools
- id: control-plane-single-counter
  decision: shadow calls through ControlPlane.record_call
  rollback: revert supervisor shadow accounting
- id: structured-l0
  decision: L0 needs re-hashed ProofReceipts
  rollback: revert deterministic_proof
---
# architecture

Trust boundary first (H1), then budget/accounting invariants (H2), proof and cache semantics (H3), reporting, evals and CI (H4).
