---
sdd: 1
feature: API_FORGE_STEP11_OTEL_GENAI
phase: intent
profile: critical
status: done
risk_class: medium
problem: local spans use a closed six-operation vocabulary, carry only four
  correlation ids, and never leave the JSONL ledger — nothing interoperates
  with a real OpenTelemetry pipeline and no collector acceptance is proven
success: AgentSpan covers all 18 §50 operations and the 10 §51 correlation
  ids; telemetry-export emits a valid OTLP ExportTraceServiceRequest;
  telemetry-ids issues W3C traceparent values; telemetry-validate accepts
  the payload deterministically; a pinned collector CI job confirms real
  acceptance or honestly reports refused/unresolved
out_of_scope:
  - OTLP/gRPC transport (HTTP/JSON is the collector's declared receiver)
  - live instrumentation wiring — emitters call telemetry-span explicitly
  - metrics/logs pipelines (traces only this phase)
upstream:
  path: discover.md
  sha256: "5c7900f92c2743ef56278dcba4ff7d68fcb87fbcfccbe987c43aedd98b8b5cb8"
---

# intent

Deliver §50-§52: interoperable OTLP export over the full GenAI operation
vocabulary, the standardized correlation id set, and a real collector
acceptance gate — while keeping the local ledger the source of truth and
the whole path offline-capable.
