# ModelCandidate/v1

One provider/model descriptor the router may rank — declared data in
`rules/model_router.yaml`, never invented at call time.

| Field | Meaning |
|---|---|
| `provider` / `model` | Identity — routing reasons over capabilities, not names |
| `tool_support` / `structured_output` | Declared capabilities (hard constraints) |
| `context_window` / `reasoning_tier` | Capacity limits; `reasoning_tier` is `none`/`light`/`deep` |
| `availability` | `available`/`degraded`/`unavailable`/`unknown` |
| `cost_per_1k` / `latency_p50_ms` | Declared economics used when no scorecard exists |
| `role` | `champion` (default selection), `fallback`, or opt-in `challenger` |
