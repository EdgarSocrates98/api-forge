# Local agent telemetry

`AgentSpan/v1` is API Forge's provider-neutral local evidence record for
`invoke_agent`, `execute_tool`, `handoff`, `decision`, `retrieval` and
`checkpoint` operations. It uses trace/run/task identity and OTel-shaped names
without importing an exporter or making a network call.

Spans are appended to `.apiforge/telemetry/agent-spans.jsonl`. The contract
rejects secret-like attribute keys such as `authorization`, `api_key`,
`password`, `secret` and `access_token` with `AF-OTEL-SENSITIVE-ATTRIBUTE`.
Duplicate span ids are idempotent only when their content hash matches;
conflicting reuse is refused.

```text
apiforge runtime telemetry-span --trace-id trace-1 --task-id task-1 \
  --run-id run-1 --operation execute_tool --tool budget-check \
  --started-at 2026-10-04T12:00:00Z \
  --attributes '{"gen_ai.tool.name":"budget-check"}'
apiforge runtime telemetry-query --trace-id trace-1
```

The MCP projections `agent_span_append` and `agent_span_query` call the same
local service. A ready query proves local persistence only; it does not prove
that a live backend or exporter received the data.
