---
sdd: 1
feature: API_FORGE_FIELD_VALIDATION
phase: plan
profile: critical
status: draft
upstream:
  path: architecture.md
  sha256: "79d3c42ff899012f90ac17d1c9ec69ce431bd39f4e6f62a43d075b049f9c9f64"
tasks:
- id: f-harness
  covers:
  - pre-registered-corpus
  - evidence-joined-record
  - closed-enum-annotation
  - blind-verification
  - deterministic-gap-report
  - anonymized-export
  test: sdd/API_FORGE_FIELD_VALIDATION/evidence/field-tests.txt
  risk: medium
  rollback: revert the field harness files
- id: s-inference
  covers:
  - isolated-inference
  test: sdd/API_FORGE_FIELD_VALIDATION/evidence/field-tests.txt
  risk: high
  rollback: revert inference, graph and workspace service changes
---
# plan

Harness first, then inference, then MCP parity and docs; full suite once before ship.
