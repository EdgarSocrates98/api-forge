---
sdd: 1
feature: API_FORGE_STEP11_OTEL_GENAI
phase: contract
profile: critical
status: done
covers:
  - operation-vocabulary
  - correlation-ids
  - otlp-export
  - structural-acceptance
  - collector-probe
  - cli-mcp-surface
  - eval-corpus
contracts:
  - CorrelationIds/v1
  - OtlpExport/v1
  - OtlpValidation/v1
  - CollectorProbe/v1
upstream:
  path: intent.md
  sha256: "b7120ce4c61b695ddb6d883046f2d0a73d3be7cf915e24342a7627be82833068"
---

# contract

Four new contracts plus additive extensions to `AgentSpan`/`SpanOperation`:

- `SpanOperation` grows from 6 to all 18 §50 members — old values unchanged;
- `AgentSpan` gains six optional correlation id fields — old payloads keep
  validating;
- `CorrelationIds` records the §51 id set with `traceparent` projection;
- `OtlpExport` wraps the ExportTraceServiceRequest payload with source hash;
- `OtlpValidation` is the deterministic acceptance verdict;
- `CollectorProbe` records sent/accepted counts and the honest status —
  `accepted`, `refused`, `unresolved`.
