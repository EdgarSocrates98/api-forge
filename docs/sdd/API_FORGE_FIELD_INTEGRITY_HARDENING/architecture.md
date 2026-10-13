---
sdd: 1
feature: API_FORGE_FIELD_INTEGRITY_HARDENING
phase: architecture
profile: critical
status: draft
upstream:
  path: contract.md
  sha256: "722fcba18c74b60289f21b1cc17cb3244c39230b2e1f8ce64db3b9cd8dbd60e3"
files:
- src/apiforge/contracts/field.py
- src/apiforge/field/
- src/apiforge/cli_field.py
- src/apiforge/mcp/tools.py
- src/apiforge/workspace/inference/match.py
decisions:
- id: sealed-lock
  decision: first field record writes cycle.lock.json; every field command recomputes the identity and refuses on mismatch or missing lock
  rollback: delete src/apiforge/field/identity.py and its calls
- id: derived-staleness
  decision: receipts store an annotation digest; staleness is derived at read time, annotate never touches the receipt
  rollback: revert field/readiness.py and annotate.py
- id: readiness-gate
  decision: h1_verdict and SDD recommendations only when cycle_status is ready; record refused after expiry
  rollback: revert report.py and record.py
---
# architecture

Identity, actors and readiness are new leaf modules; record, annotate, report and export only call them. Inference stays independent of the field harness.
