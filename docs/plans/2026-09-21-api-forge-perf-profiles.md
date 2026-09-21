# Plan 14 — Performance profile readers

**Goal:** `model jfr|pprof|pyroscope` read profiler exports offline — the
profilers are never run. JFR = `jfr print --json` events; pprof = `-top`
text rows; Pyroscope = flamebearer JSON. Each emits `perf.*` facts capped at
the top 20 entries (`truncated` attr says when more existed); malformed input
→ `AF-PERF-*` diagnostics.

- [ ] T1: `adapters/perfprofiles.py` — three readers, shared inventory shape
- [ ] T2: CLI table entries + tests + docs/gate parity
