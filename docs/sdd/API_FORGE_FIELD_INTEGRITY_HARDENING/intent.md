---
sdd: 1
feature: API_FORGE_FIELD_INTEGRITY_HARDENING
phase: intent
profile: critical
status: draft
upstream:
  path: discover.md
  sha256: "2817893b9d2efce742a19c7afb101e070c3eabb5f5e83d769f024236c488beb9"
problem: 'The field harness can report a verified, decision-grade result from a mutated pre-registration,
  a re-labelled annotation, a self-verification or an incomplete cycle.'
success:
- sealed-cycle-identity
- stale-verification-receipt
- independent-verifier
- readiness-gated-decision
- enforced-timebox
- http-callee-provenance
out_of_scope:
- new-inference-protocols
- field-event-ledger
- lock-signing
- cycle-reset-command
- running-the-field-cycle
owner: api-forge-field
risk_class: high
risk_signals:
- path:src/apiforge/contracts/field.py
- path:src/apiforge/mcp/tools.py
- path:src/apiforge/workspace/inference/match.py
---
# intent

Make the field evidence chain fail closed before the first real cycle starts, so the next roadmap theme is decided on untampered, independently verified and complete data.
