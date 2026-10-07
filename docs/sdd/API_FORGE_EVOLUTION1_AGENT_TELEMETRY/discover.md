---
sdd: 1
feature: API_FORGE_EVOLUTION1_AGENT_TELEMETRY
phase: discover
profile: critical
status: done
approaches:
  - id: provider-export
    summary: send agent spans directly to a telemetry backend
    verdict: refused -- violates offline-first and host-owned network boundaries
  - id: untyped-log
    summary: append arbitrary debug dictionaries
    verdict: refused -- loses semantic conventions and closed validation
  - id: local-otel-span
    summary: store OTel-shaped agent/tool spans as evidence-bound local records
    verdict: chosen -- standardized, provider-neutral and replayable
chosen: local-otel-span
---

# discover

Existing observability normalizes provider-neutral `TelemetryRecord/v1`, but
agent invocation and tool execution spans are not first-class. The wave adds
the missing local span boundary without claiming a live exporter.
