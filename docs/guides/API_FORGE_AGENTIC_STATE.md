# Governed agentic state

The first evolution wave adds three local data planes:

- `apiforge memory`: propose, persist, search and invalidate immutable memory;
- `apiforge blackboard`: append/query task-scoped facts, claims, objections and decisions;
- `apiforge runtime semantic-checkpoint`: save a semantic resume snapshot.

All writes are local and append-only. No command calls a model/provider or
mutates cloud, GitHub, databases or production. Use an explicit `--now` for
deterministic timestamps. JSON payloads may be passed inline or by file.

## Safe memory flow

```text
memory propose -> candidate -> memory persist -> memory search -> use
                                             \-> invalidate (append-only)
```

The default policy permits working/case/task/episodic scopes at observed
trust. Institutional/semantic persistence requires evidence refs, and
model-generated or external-untrusted content receives a named refusal. A
search can be `degraded` when records are stale, tainted or from another
environment; those states are intentionally visible.

## Examples

```text
apiforge memory propose --scope case --origin verified_evidence \
  --payload '{"fact":"route"}' --by af-synthesizer \
  --reason "case fact" --now 2026-10-04T10:00:00Z --evidence fact:abc
apiforge memory persist --candidate-id candidate:<id> --now 2026-10-04T10:01:00Z
apiforge memory search --term route --now 2026-10-04T10:02:00Z
apiforge blackboard append --task-id task-1 --scope planner --kind hypothesis \
  --origin model_generated --payload '{"text":"candidate"}' --now 2026-10-04T10:00:00Z \
  --taint model_generated
apiforge blackboard query --task-id task-1 --kind hypothesis
```

The MCP functions `memory_propose`, `memory_persist`, `memory_search`,
`blackboard_append` and `blackboard_query` call the same application services
and return the same versioned payloads. The MCP surface remains optional and
the compact gateway discovers these tools instead of loading every schema.

