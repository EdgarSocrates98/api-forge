---
sdd: 1
feature: API_FORGE_STEP11_OTEL_GENAI
phase: ship
profile: critical
status: done
deviations:
  - "OTLP/HTTP+JSON is the declared transport; OTLP/gRPC is not emitted yet"
  - "emitters call telemetry-span explicitly; auto-instrumentation of the
    runtime loop is left for a later phase"
  - "the real-collector acceptance runs in CI (pinned image); a host
    without Docker reports unresolved via --otlp-only mode"
evidence:
  - docs/sdd/API_FORGE_STEP11_OTEL_GENAI/evidence/G1-focused-tests.txt
  - docs/sdd/API_FORGE_STEP11_OTEL_GENAI/evidence/G2-evals.txt
  - docs/sdd/API_FORGE_STEP11_OTEL_GENAI/evidence/G3-gates.txt
rollback: "revert this commit; SpanOperation additions and optional id
  fields are additive — older payloads keep validating and older code
  never reads otel_export"
upstream:
  path: benchmark.md
  sha256: "328aa80073fd602cd42c9709f6098517b3c67d2dc64e5b3f53d5a3e92f47d886"
---

# ship

Phase 7 delivered: interoperable OTLP export over the full §50 vocabulary,
the §51 correlation id set with W3C traceparent, deterministic structural
acceptance, and a real pinned-collector CI job with honest
accepted/refused/unresolved statuses.
