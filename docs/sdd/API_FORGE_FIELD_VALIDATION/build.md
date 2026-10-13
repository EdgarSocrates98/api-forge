---
sdd: 1
feature: API_FORGE_FIELD_VALIDATION
phase: build
profile: critical
status: draft
upstream:
  path: plan.md
  sha256: "4d0d082009a01cc0d0e8e956b612724dea4790f78bc99fa8e43379ac0a9ef0fb"
tasks:
- id: f-harness
  status: done
  evidence: sdd/API_FORGE_FIELD_VALIDATION/evidence/field-tests.txt
- id: s-inference
  status: done
  evidence: sdd/API_FORGE_FIELD_VALIDATION/evidence/field-tests.txt
claims:
- pre-registered-corpus
- evidence-joined-record
- closed-enum-annotation
- blind-verification
- deterministic-gap-report
- isolated-inference
- anonymized-export
---
# build

`apiforge field record|annotate|verify|report|export`, MCP twins, `workspace graph [--infer --run-id]`, the `http.outbound` extractor and the pure matcher. Build report: `.claude/sdd/reports/BUILD_REPORT_API_FORGE_FIELD_VALIDATION.md`.
