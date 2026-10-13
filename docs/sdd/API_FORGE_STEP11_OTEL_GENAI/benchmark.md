---
sdd: 1
feature: API_FORGE_STEP11_OTEL_GENAI
phase: benchmark
profile: critical
status: done
baseline:
  name: full-suite
  command: pytest -q --basetemp=<host-temp>
  result: 1611 passed, 2 skipped (phase-6 wave baseline)
  recorded_at: "2026-10-06"
results:
  - "focused suite: 18 passed, 1 skipped in ~9s"
  - "evals telemetry-otlp: 3/3 deterministic, no provider calls"
  - "export is O(spans); validation is O(spans x attributes); probe polls
    the output file on a 250ms cadence until deadline"
upstream:
  path: secure.md
  sha256: "de8c8af379478bbbcfc8f1575fe301d59372876885285e87b68278f4468b3881"
---

# benchmark

Export and validation run on demand from CLI/MCP — nothing sits on a hot
path. The ledger grows append-only as before; the OTLP projection adds no
storage.
