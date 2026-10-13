---
sdd: 1
feature: API_FORGE_FIELD_INTEGRITY_HARDENING
phase: plan
profile: critical
status: draft
upstream:
  path: architecture.md
  sha256: "26e5e5e29cf6e49ab9cf85a8c45445ff43cad3a4873503ddb135ca16afa09978"
tasks:
- id: i-integrity
  covers:
  - sealed-cycle-identity
  - stale-verification-receipt
  - independent-verifier
  - readiness-gated-decision
  - enforced-timebox
  test: sdd/API_FORGE_FIELD_INTEGRITY_HARDENING/evidence/field-tests.txt
  risk: high
  rollback: revert the field harness files and contracts
- id: p-provenance
  covers:
  - http-callee-provenance
  test: sdd/API_FORGE_FIELD_INTEGRITY_HARDENING/evidence/field-tests.txt
  risk: low
  rollback: revert workspace/inference/match.py
---
# plan

Contracts and errors first, then identity/actors/readiness, then command wiring, CLI/MCP parity, docs and catalog; full suite once before ship.
