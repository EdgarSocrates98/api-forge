---
sdd: 1
feature: API_FORGE_STEP11_OTEL_GENAI
phase: discover
profile: critical
status: done
approaches:
  - id: otel-sdk-dependency
    summary: adopt opentelemetry-python SDK for export
    verdict: refused -- adds a runtime dependency for a payload we can emit
      deterministically; the platform stays offline-first and SDK-free in
      src/ (no provider SDK imports is a standing rule)
  - id: replace-span-ledger
    summary: store spans directly in OTLP shape
    verdict: refused -- the append-only AgentSpan ledger is the evidence
      plane with dedupe/conflict semantics; OTLP is a projection of it, not
      the store
  - id: projection-plus-probe
    summary: keep the local ledger, project to OTLP ExportTraceServiceRequest
      JSON on demand, validate structure deterministically, and POST to a
      real pinned collector in CI counting accepted span ids
    verdict: chosen -- additive, offline gate plus a real collector test in
      CI, honest unresolved when no collector is declared
chosen: projection-plus-probe
---

# discover

Phase 7 of `prompt_evo_step11.md` (§50-§52): the local OTel-shaped spans
become an interoperable OTLP export covering all 18 roadmap operations; a
standardized correlation id set with W3C traceparent; and a real collector
acceptance test in CI — not just local JSON assertions.
