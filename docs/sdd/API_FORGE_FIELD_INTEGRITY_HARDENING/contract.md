---
sdd: 1
feature: API_FORGE_FIELD_INTEGRITY_HARDENING
phase: contract
profile: critical
status: draft
upstream:
  path: intent.md
  sha256: "0c8c6343a86e346fd464cc5cb48a3b4a455c6992392595f8d5759a3f82272315"
covers:
- apiforge/field-cycle-identity/v1
- apiforge/field-verification-receipt/v1
- apiforge/field-run/v2
- apiforge/field-report/v2
api_ir:
  input: corpus.yaml, hypothesis.md, cycle.lock.json, field-run records, executor and verifier actors
  output: sealed cycle identity, verification receipts, readiness-gated gap report, HTTP relations with callee refs
---
# contract

`field-run` and `field-report` move to v2 in place: no v1 payload exists (cycle unstarted, `docs/field/runs` empty). `verifier_verdict` is replaced by `verification` (receipt); `executor` is required. New refusals `AF-FIELD-CYCLE-MUTATED`, `AF-FIELD-CYCLE-EXPIRED`, `AF-FIELD-VERIFIER-NOT-INDEPENDENT`, `AF-FIELD-ACTOR-INVALID` are cataloged.
