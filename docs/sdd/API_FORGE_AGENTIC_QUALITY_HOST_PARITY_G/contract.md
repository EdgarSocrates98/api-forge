---
sdd: 1
feature: API_FORGE_AGENTIC_QUALITY_HOST_PARITY_G
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "554fddd0e5b2a2e381fd4ce83ee0edd8999e78b42208a683dec5978b7e8bde20"
covers: [AgenticQualityAssessment/v1]
api_ir:
  input: EvalResult sequence and host parity report
  output: ready, review or blocked quality assessment
---
# contract

Holdout ausente e gap de host são blockers explícitos; casos REVIEW permanecem visíveis.
