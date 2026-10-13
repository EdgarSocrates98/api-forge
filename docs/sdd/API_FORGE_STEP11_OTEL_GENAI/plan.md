---
sdd: 1
feature: API_FORGE_STEP11_OTEL_GENAI
phase: plan
profile: critical
status: done
tasks:
  - id: G1
    covers: [operation-vocabulary, correlation-ids, otlp-export, cli-mcp-surface]
    test: sdd/API_FORGE_STEP11_OTEL_GENAI/evidence/G1-focused-tests.txt
  - id: G2
    covers: [eval-corpus, collector-probe]
    test: sdd/API_FORGE_STEP11_OTEL_GENAI/evidence/G2-evals.txt
  - id: G3
    covers: [structural-acceptance]
    test: sdd/API_FORGE_STEP11_OTEL_GENAI/evidence/G3-gates.txt
upstream:
  path: architecture.md
  sha256: "7776027eb024872f9bbbe483c539e0e1391767aa39ec90de68f7413a7521cd7a"
---

# plan

G1 — contracts, exporter, CLI verbs, MCP projections: focused pytest over
`test_otel_export.py`, `test_agent_telemetry.py` and the MCP surface test.

G2 — eval corpus + the collector-check script in `--otlp-only` mode.

G3 — Ruff + mypy strict over every new/changed module.
