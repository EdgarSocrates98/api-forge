---
sdd: 1
feature: API_FORGE_STEP11_OTEL_GENAI
phase: architecture
profile: critical
status: done
files:
  - src/apiforge/contracts/agent_telemetry.py
  - src/apiforge/contracts/otel_export.py
  - src/apiforge/contracts/registry.py
  - src/apiforge/contracts/__init__.py
  - src/apiforge/runtime/agent_telemetry.py
  - src/apiforge/runtime/otel_export.py
  - src/apiforge/cli_agentic_state.py
  - src/apiforge/mcp/tools.py
  - src/apiforge/evals/otel_export.py
  - src/apiforge/cli.py
  - scripts/otel_collector_check.py
  - scripts/otelcol/otelcol.yaml
  - .github/workflows/ci.yml
  - evals/corpus/telemetry-otlp/
  - tests/runtime/test_otel_export.py
  - tests/mcp/test_tools.py
  - docs/contracts/
decisions:
  - "OTLP is a projection: to_otlp_payload converts ledger rows on demand;
    the append-only AgentSpan ledger stays the evidence store"
  - "trace ids: 32-hex pass-through else sha256-derived; span ids: the
    span: prefix strips to the 16-hex id — deterministic, reversible"
  - "kind mapping: invoke_model/execute_tool/retrieval export as CLIENT(3);
    every other operation as INTERNAL(1)"
  - "gen_ai.operation.name carries the operation verbatim (the semconv
    vocabulary is open); apiforge.* attributes carry the §51 id set and
    unresolved/evidence refs"
  - "unparseable timestamps do not drop the span — startTimeUnixNano falls
    to 0 and the defect is named in export.unresolved"
  - "collector acceptance is a probe: POST then count sent span ids inside
    the declared output file; refused and unresolved are distinct statuses"
  - "CI runs a pinned otel/opentelemetry-collector-contrib:0.114.0 with a
    file exporter; local runs without a collector stay unresolved"
upstream:
  path: contract.md
  sha256: "6cdd7602a48102360b58c135d1f6d9cba367a98e33398389d50c40be3c31dfe8"
---

# architecture

Additive: a contracts extension, one exporter module, four runtime CLI
verbs, two read-only MCP projections, the CI job and the eval corpus.
Nothing mutates span storage, the decision gate or economy surfaces.
