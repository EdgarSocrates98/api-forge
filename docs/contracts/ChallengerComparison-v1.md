# ChallengerComparison/v1

`ChallengerComparison/v1` is the §53–58 receipt that records a shadow
challenger next to its champion — over **observable fields only**. It is
persisted as `challenger-comparison-<capability>.json` in the run directory
and linked from `ShadowDecision.comparison_ref`.

Semantics:

- the challenger ran in `shadow` — it never governs (`governs` is always
  `false`), never enters the run's artifacts, gaps or status;
- a challenger is **not** a fallback: fallbacks execute on failure to produce
  the authoritative result; challengers run beside a healthy champion to be
  observed;
- promotion is a separate control-plane decision over accumulated evidence —
  a single comparison never promotes.

| Field | Meaning |
|---|---|
| `run_id`, `task_id`, `mode` | Run identity and shadow mode (`paired_ab` / `capability_eval`) |
| `champion`, `challenger` | `ChallengerSide/v1` per side: capability, artifact_id, recommendation, confidence, facts, evidence, `input_tokens`, `output_tokens`, `duration_ms`, `tool_calls` — `null` where the source did not report it |
| `agreement` | Challenger recommendation equals the champion's (null without a champion artifact) |
| `quality_delta` | `challenger.confidence − champion.confidence` when both are observed |
| `latency_delta_ms` | `challenger.duration_ms − champion.duration_ms` when both are observed |
| `token_delta` | `challenger.input_tokens − champion.input_tokens` when both are observed |
| `cost_delta_usd` | Always `null` locally — no cost observer exists in the runtime |
| `structured_correctness` | Challenger payload passes the artifact guardrail (`validate_agent_payload`) |
| `tool_correctness` | Challenger `tool_calls` equal the champion's — `null` when neither side reported tool calls |
| `governs` | Always `false` — contract-level proof the comparison cannot authorize |
| `basis` | Names of the metrics actually observed (`agreement`, `quality`, `latency`, `tokens`, `structured_correctness`, `tool_correctness`) |

Missing metrics stay `null` and stay out of `basis` — the receipt never
invents quality, latency, token or cost evidence.
