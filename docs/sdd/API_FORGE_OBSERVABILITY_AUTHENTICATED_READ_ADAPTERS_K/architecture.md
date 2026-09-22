---
sdd: 1
feature: API_FORGE_OBSERVABILITY_AUTHENTICATED_READ_ADAPTERS_K
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "b47752a0a7cd428455804cde5646dd46e3b3723edae53c23ffda6bb19ef4cb60"
files: [src/apiforge/observability/read_adapter.py, tests/observability/test_read_adapter.py]
decisions:
  - id: transport-boundary
    decision: HTTP e headers pertencem ao host/broker injetado
    rollback: manter fixture-only
---
# architecture

Um adapter provider-neutral cobre Datadog, Dynatrace, CloudWatch e OTel por transporte injetado.
