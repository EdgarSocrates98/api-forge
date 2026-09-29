---
sdd: 1
feature: API_FORGE_FIELD_INTEGRITY_HARDENING
phase: build
profile: critical
status: draft
upstream:
  path: plan.md
  sha256: "7f9191c95f3f1690116fafcf8af23cb7d14e805e4a3524a554e49c2217745eba"
tasks:
- id: i-integrity
  status: done
  evidence: sdd/API_FORGE_FIELD_INTEGRITY_HARDENING/evidence/field-tests.txt
- id: p-provenance
  status: done
  evidence: sdd/API_FORGE_FIELD_INTEGRITY_HARDENING/evidence/field-tests.txt
claims:
- sealed-cycle-identity
- stale-verification-receipt
- independent-verifier
- readiness-gated-decision
- enforced-timebox
- http-callee-provenance
---
# build

New `field/identity.py`, `field/actors.py`, `field/readiness.py`; `--executor` on `field record`, `--verifier` on `field verify` (CLI and MCP); `gate.max_runs` 40. Build report: `.claude/sdd/reports/BUILD_REPORT_FIELD_INTEGRITY_HARDENING.md`.
