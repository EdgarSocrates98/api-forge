# CorrelationIds/v1

§51 the standardized correlation identifier set for agentic traces.

| Field | Meaning |
|---|---|
| `task_id` / `run_id` / `trace_id` / `span_id` | Execution identity |
| `agent_id` / `model_call_id` / `tool_call_id` | Who acted and which calls |
| `decision_id` / `memory_id` / `context_id` | Governance, memory and context lineage |
| `traceparent` | W3C `00-<32hex>-<16hex>-<flags>` projection when both ids exist |
| `unresolved` | Ids never issued — named, never synthesized |

`runtime telemetry-ids --issue-trace` issues a fresh W3C pair; every absent
id lands in `unresolved`.
