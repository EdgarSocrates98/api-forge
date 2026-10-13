---
sdd: 1
feature: API_FORGE_FIELD_INTEGRITY_HARDENING
phase: verify
profile: critical
status: draft
upstream:
  path: build.md
  sha256: "345dfe48a6c983bdc4d5a3f36a24353fe752cd5f3497608b03709fa58f831059"
results:
- gate: targeted tests field, workspace inference, mcp tools
  outcome: pass
  evidence: sdd/API_FORGE_FIELD_INTEGRITY_HARDENING/evidence/field-tests.txt
- gate: Ruff + mypy on changed modules
  outcome: pass
  evidence: 'ruff: all checks passed; mypy: no issues in 15 source files'
---
# verify

AT-001..AT-017 map to `tests/field/test_integrity.py`, `tests/field/test_export_parity.py` and `tests/workspace/test_inference.py`. Full suite runs once before ship.
