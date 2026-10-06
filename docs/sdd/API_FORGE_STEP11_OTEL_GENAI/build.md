---
sdd: 1
feature: API_FORGE_STEP11_OTEL_GENAI
phase: build
profile: critical
status: done
tasks:
  - id: B1
    summary: contract extensions + four contracts + registry + exports + docs
    files: [src/apiforge/contracts/agent_telemetry.py, src/apiforge/contracts/otel_export.py, src/apiforge/contracts/registry.py, src/apiforge/contracts/__init__.py, docs/contracts/, docs/catalog-contract.md]
  - id: B2
    summary: OTLP exporter + correlation ids + probe + ledger id plumbing
    files: [src/apiforge/runtime/otel_export.py, src/apiforge/runtime/agent_telemetry.py]
  - id: B3
    summary: four runtime verbs + two MCP read tools + eval + corpus + collector script + CI job
    files: [src/apiforge/cli_agentic_state.py, src/apiforge/mcp/tools.py, src/apiforge/evals/otel_export.py, src/apiforge/cli.py, scripts/otel_collector_check.py, scripts/otelcol/otelcol.yaml, .github/workflows/ci.yml, evals/corpus/telemetry-otlp/, tests/]
claims:
  - "all 18 §50 operations validate as SpanOperation members and export"
  - "telemetry-export produces a valid OTLP ExportTraceServiceRequest with
    gen_ai.operation.name on every span"
  - "telemetry-ids --issue-trace mints a W3C traceparent; absent ids are
    named in unresolved, never invented"
  - "telemetry-collector-check POSTs and counts accepted span ids in the
    collector output file; refused/unresolved are distinct"
  - "the CI job runs a pinned collector image; no fake acceptance"
  - "sensitive attribute keys stay refused at the contract boundary"
upstream:
  path: plan.md
  sha256: "99e2ee9982e7dfdcaa05cbec2dd9ea4f1207eadecfbf2198fab4bab6d0e462d2"
---

# build

Implementation matches the architecture decisions; every claim is
exercised by the focused suite or the eval corpus.
