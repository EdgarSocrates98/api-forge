# Governed agentic state

The agentic state plane now covers four local, append-only surfaces:

- `apiforge memory`: propose, persist, search, rank, quarantine and invalidate
  immutable memory under the §14 gate pipeline;
- `apiforge blackboard`: append/query task-scoped facts, claims, objections
  and decisions;
- `apiforge runtime semantic-checkpoint`: save a semantic resume snapshot;
- Trust Plane (`apiforge.trust`): unified origin/trust/taint annotation,
  deterministic propagation and allowlist-first tool authorization.

All writes are local and append-only. No command calls a model/provider or
mutates cloud, GitHub, databases or production. Use an explicit `--now` for
deterministic timestamps. JSON payloads may be passed inline or by file.

## Safe memory flow

```text
memory propose -> candidate -> memory persist -> memory search -> use
                              |                 \-> memory rank (scored)
                              \-> quarantine (trust below policy minimum)
                                  -> quarantine-resolve (human: persist|reject)
                                             \-> invalidate (append-only)
```

The default policy permits working/case/task/episodic scopes at observed
trust. Institutional/semantic persistence requires evidence refs, and
model-generated or external-untrusted content receives a named refusal. Trust
below the policy minimum no longer hard-rejects: the candidate parks in
`quarantine.jsonl`, invisible to retrieval, until a human resolves it — a
release to `persist` re-runs the entire gate pipeline. A search can be
`degraded` when records are stale, tainted or from another environment; those
states are intentionally visible. `memory rank` exposes the §15 deterministic
signal decomposition; semantic similarity remains an optional caller-supplied
bonus, never a dependency.

## The four different things people call "compaction"

These mechanisms are deliberately distinct; conflating them corrupts resume
semantics and hides cost:

- **Tool-output compaction** — `apiforge context compact` and the RTK-style
  filters shrink *one tool's output* before it re-enters context. Lossless by
  rule: critical lines stay, the full artifact keeps its path.
- **Context reduction** — `context capsule`/`context quality` select the
  minimum sufficient *evidence refs* for an intent under a byte budget. It
  decides what enters context, not how it is phrased.
- **Conversation compaction** — transcript summarization inside a host/agent
  loop. It rewrites history for the model's window and is *not* trusted state:
  anything lost here must be recoverable from ledgers.
- **Semantic checkpoint** — `SemanticCheckpoint/v1` is governed *resume state*:
  decisions, facts, unresolved items, tool/routing/budget state, next actions.
  It survives transcript compaction entirely and is the source of truth a
  fresh process resumes from (see `tests/runtime/test_checkpoint_parity.py`
  for the continuous-vs-resumed parity proof).

## Examples

```text
apiforge memory propose --scope case --origin verified_evidence \
  --payload '{"fact":"route"}' --by af-synthesizer \
  --reason "case fact" --now 2026-10-04T10:00:00Z --evidence fact:abc
apiforge memory persist --candidate-id candidate:<id> --now 2026-10-04T10:01:00Z
apiforge memory search --term route --now 2026-10-04T10:02:00Z
apiforge memory rank --term route --environment repo:a --now 2026-10-04T10:02:00Z
apiforge memory quarantine-list
apiforge memory quarantine-resolve --candidate-id candidate:<id> \
  --verdict persist --by reviewer --now 2026-10-04T10:03:00Z
apiforge blackboard append --task-id task-1 --scope planner --kind hypothesis \
  --origin model_generated --payload '{"text":"candidate"}' --now 2026-10-04T10:00:00Z \
  --taint model_generated
apiforge blackboard query --task-id task-1 --kind hypothesis
```

The MCP functions `memory_propose`, `memory_persist`, `memory_search`,
`memory_rank`, `memory_quarantine_list`, `memory_quarantine_resolve`,
`blackboard_append` and `blackboard_query` call the same application services
and return the same versioned payloads. The MCP surface remains optional and
the compact gateway discovers these tools instead of loading every schema.

## Governed decisions (phase 4)

The governor surface answers *whether* to act, never *executes*: every verb is
a pure function over declared inputs plus versioned policy yaml, so the same
inputs always produce the same `GovernorDecision`/`StopDecision`/
`RecoveryDecision`/`LoopDetection`.

- `apiforge governor decide --profile … --risk …` — the risk floor only
  raises the profile; `budget` and `security_state` clamps land in
  `clamped_by`, inputs not supplied land in `unresolved`.
- `apiforge governor gain|stop --action <name>` — expected information gain
  for the §24 named actions; a score below threshold stops
  (`AF-GOV-STOP-LOW-GAIN`) and an unmeasurable gain stops closed
  (`AF-GOV-GAIN-UNRESOLVED`) unless a mandatory requirement holds.
- `apiforge governor recover --failure-class C --attempt N` — the closed
  §26 vocabulary (unknown classes refuse `AF-GOV-FAILURE-CLASS-UNKNOWN`);
  exhausted caps fire the terminal escalate/stop.
- `apiforge governor loop-check --fingerprints …` — repeated strategy
  fingerprints inside the window block `AF-GOV-LOOP-DETECTED`.

The same projections are exposed as read-only MCP tools
(`governor_decide`, `governor_stop`, `governor_recover`). Nothing in this
surface spawns agents or spends budget — the phase-5 control plane consumes
the decisions.
