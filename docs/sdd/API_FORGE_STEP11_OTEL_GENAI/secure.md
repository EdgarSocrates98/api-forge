---
sdd: 1
feature: API_FORGE_STEP11_OTEL_GENAI
phase: secure
profile: critical
status: done
threat_model:
  - secret exfiltration via span attributes — the existing
    AF-OTEL-SENSITIVE-ATTRIBUTE contract boundary refuses secret-like keys
    before export ever runs
  - fabricated acceptance — CollectorProbe requires span ids physically
    present in the collector's declared output file; unreachable endpoints
    and missing outputs stay unresolved, HTTP errors are refused
  - id spoofing — traceparent refuses non-W3C values with
    AF-OTEL-TRACEPARENT-INVALID; ids are issued by secrets.token_hex, not
    user-supplied randomness
  - supply chain — the CI collector image is pinned to
    otel/opentelemetry-collector-contrib:0.114.0; no floating latest tag
  - mutation surface — MCP exposes only read projections (export, validate);
    span append keeps its existing sanitized boundary
upstream:
  path: verify.md
  sha256: "6d1919998742c3bb8c91213b1af4214fe640b3d921c880fdc51e86f06bcacd8f"
---

# secure

The export path reads the ledger and produces JSON — no mutation. The only
network call is the explicit `telemetry-collector-check` POST to a
caller-declared endpoint; everything else is offline.
