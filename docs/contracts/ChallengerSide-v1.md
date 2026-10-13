# ChallengerSide/v1

One side of a [`ChallengerComparison/v1`](ChallengerComparison-v1.md)
receipt — the champion or the challenger, over **observable fields only**.
Every metric that the run could not observe stays `null`; absence is never
reported as zero.

| Field | Meaning |
|---|---|
| `capability` | The routed capability that produced this side |
| `artifact_id` | The produced `AgentArtifact` id (challenger runs are observational: no artifact persisted → `null`) |
| `recommendation` / `confidence` | Parsed from the side's payload when present |
| `facts` / `evidence` | Declared facts and evidence refs |
| `input_tokens` / `output_tokens` / `duration_ms` | Adapter-observed usage; `null` when the adapter does not report |
| `tool_calls` | Tools the side invoked, when observable |

Canonical schema: `apiforge contract show ChallengerSide/v1`.
