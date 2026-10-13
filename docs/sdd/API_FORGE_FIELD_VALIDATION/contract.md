---
sdd: 1
feature: API_FORGE_FIELD_VALIDATION
phase: contract
profile: critical
status: draft
upstream:
  path: intent.md
  sha256: "92b594a2fce9e475d732a7603de500259ffcbe23af4d7b2a86d47114d27d2130"
covers:
- apiforge/field-corpus/v1
- apiforge/field-run/v1
- apiforge/field-report/v1
- apiforge/field-eval-case/v1
- apiforge/workspace-graph/v1
api_ir:
  input: corpus.yaml, hypothesis.md, economy ledger, summary.json, economy_checkpoint.json, workspace manifest and repository sources
  output: field-run records, gap report with Wilson CI and H1 verdict, anonymized eval cases, inferred workspace relations
---
# contract

New field contracts. `RelationKind` gains `publishes_to_consumer` (additive); inferred edges use `EvidenceRecord.level = inferred` with confidence and file:line refs. New refusal family `AF-FIELD-*` and unresolved codes `AF-WORKSPACE-INFER-*` are cataloged.
