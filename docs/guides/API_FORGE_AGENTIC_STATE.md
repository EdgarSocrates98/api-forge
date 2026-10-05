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
  fingerprints inside the window block `AF-GOV-LOOP-DETECTED`. Runtime records
  every selected strategy in `events.jsonl` before invoking capabilities; the
  current governor policy uses `action=stop`, returning `BLOCKED` without
  spending another call.

The same projections are exposed as read-only MCP tools
(`governor_decide`, `governor_stop`, `governor_recover`). Nothing in this
surface spawns agents or spends budget — the phase-5 control plane consumes
the decisions.

Runtime tool authorization uses the declared capability role (`specialist`,
`reviewer`, `critic`, `referee` or `runner`) for named tool requests. The
adapter crossing remains one `agent-invocation` boundary grant; it does not
grant the requesting role every tool. Delegation requires an explicit parent
edge and requested-tool scope. `apiforge_call` authorizes the gateway and then
the resolved target against the MCP registry before preserving inner domain
gates.

## Decision Control Plane lifecycle (phase 5)

Every decision route declared in `rules/control_plane.yaml` lives under a
`shadow → assisted → active` lifecycle; the fail-closed `governance
decision-check` gate stays the admission boundary underneath.

- **shadow** — `control eval` runs the candidate in parallel, records a
  `ShadowRecord` (candidate vs legacy decision + sorted `difference`) in
  `control-plane/shadow.jsonl`, and **legacy governs**.
- **assisted** — the candidate's answer is a `recommendation`; legacy/human
  remains authoritative.
- **active** — the candidate governs, but only after `control promote`
  verifies the five §31 requirements (eval thresholds, security gates,
  complete evidence, declared rollback, approved `ApprovalGate`); each
  promotion is one step, appended to `control-plane/modes.jsonl`.
- **fallback** — any of the five §32 triggers (`control eval --trigger …`
  or `control triggers` to map signals) routes to the declared
  `fallback_route`; a degraded terminal route refuses
  `AF-GOV-FALLBACK-MISSING` instead of continuing.

`control demote` steps a route back — the safe direction never needs a gate.

## Model routing, scorecards and adaptive retrieval (phase 6)

The `model_routing` route declared in `rules/control_plane.yaml` is served by
`route model`: deterministic ranking over declared `ModelCandidate` rows —
hard constraints first (tool support, structured output, context window,
reasoning tier, declared cost/latency ceilings, availability), then a weighted
score over quality history, latency, cost and availability. Candidates fail
loud (`ranked[].reasons`); nothing eligible answers
`AF-ROUTE-NO-ELIGIBLE-MODEL`.

`ModelScorecard` (§34) is folded from `ModelEvaluation` rows per
provider/model **and task class**: quality, tool selection, evidence
correctness, structured reliability, latency p50, cost mean, failure rate and
freshness. Below `quality_floor` with `min_evaluations` the candidate cannot
compete on cost; missing scorecards lower the score, never block.
`route promote` converts scorecard evidence into a phase-5 promotion attempt —
a small synthetic benchmark refuses `AF-ROUTE-PROMOTION-EVIDENCE`.
`route model --shadow-root <root>` records task-class-aware candidate routing
in the existing `model_routing` Decision Plane route; candidate output remains
non-authoritative while the route is `shadow`.

`knowledge adaptive` climbs the §36 ladder only as far as needed: `L0` exact →
`L1` lexical (`knowledge/retrieval.py`) → `L2` structural graph refs → `L3`
hybrid semantic → `L4` reranker over merged candidates. L3 runs only when a
`SemanticAdapter` is declared (`HashFeatureSimilarityAdapter` is deterministic
local option — no vector DB, no network); otherwise the step is skipped with
`unresolved: ["semantic"]`. `knowledge rewrite` is §39-gated: rewriting runs
only when deterministic retrieval failed, budget remains and the profile
permits it — `economy` blocks. `evals retrieval` compares
lexical/graph/semantic/hybrid on recall, precision, latency, tokens and cost
over a declared gold corpus; `evals model-routing` covers constraint refusal,
quality floors and insufficient evaluations.

Each level writes `signals.effective_score`; ranking and sufficiency consume
that same value. `RetrievalStep.top_score` reports effective score and
`raw_top_score` keeps source-scale diagnostics. L2/L4 graph contribution comes
from bounded traversal depth, never `selected_pack`.

## Telemetry export and correlation (phase 7)

Local `AgentSpan` rows now cover all 18 §50 operations (`task`, `routing`,
`context_build`, `context_expansion`, `retrieval`, `memory_read`,
`memory_write`, `invoke_agent`, `invoke_model`, `execute_tool`, `handoff`,
`review`, `debate`, `security_decision`, `decision`, `checkpoint`,
`resume`, `promotion`) and carry the full §51 correlation set
(`agent_id`, `model_call_id`, `tool_call_id`, `decision_id`, `memory_id`,
`context_id`) beside `task_id`/`run_id`/`trace_id`/`span_id`.

- `runtime telemetry-ids` emits a `CorrelationIds` record with a W3C
  `traceparent`; `--issue-trace` mints a fresh pair. Ids never issued land
  in `unresolved`.
- `runtime telemetry-export` converts the append-only span ledger into one
  OTLP `ExportTraceServiceRequest` JSON — `gen_ai.operation.name`/
  `gen_ai.agent.name`/`gen_ai.tool.name` plus `apiforge.*` attributes, no
  OTel SDK needed.
- `runtime telemetry-validate --otlp F` is the deterministic structural
  acceptance (hex ids, unix-nano timestamps, declared operation, valid
  status code).
- `runtime telemetry-collector-check --endpoint U --output-file F` POSTs to
  a real collector and counts span ids accepted in its output file —
  `accepted`, `refused` or `unresolved`, never assumed.
- `scripts/otel_collector_check.py` drives the §52 CI job against a pinned
  `otel/opentelemetry-collector-contrib:0.114.0`; `evals telemetry-otlp`
  covers operation coverage, id propagation and malformed-input honesty.


## AgentOps inspect, compare and waste (phase 8)

`agentops inspect <run>` joins the run ledger, token ledger, span store,
context-quality derivation, memory store and decision-gate ledger into one
`RunInspection` — the §54 sections (`run`, `agents`, `context`, `memory`,
`tools`, `models`, `evidence`, `security`) plus waste findings and the
decision path. Every metric carries `observed`/`partial`/`estimated`/`unresolved`;
absent sources are named in `unresolved`, never zero-filled. Memory rows are
store-wide (no `run_id`), so memory metrics report `estimated` scope, and
provider cost stays `unresolved` without declared pricing.

Context token accounting is intentionally strict: no observed token row yields
an unresolved total, and mixed measured/unmeasured rows yield a partial total
plus `token_observation_coverage`. A missing measurement is never converted to
an observed zero.

`agentops compare RUN_A RUN_B` emits `RunComparison` over the §55 axis set —
quality, tokens, cost, latency, context, evidence, tools, agents — with a
deterministic direction per axis (lower-is-better for spend, higher for
quality/evidence). An axis missing a numeric side is `unresolved`, never a
tie by absence.

`agentops waste <run>` runs the §56 detector set declared in
`rules/agentops_waste.yaml`: all 12 `WasteKind`s (duplicate context,
duplicate retrieval, repeated tool call, repeated rule lookup, redundant
agent/review/debate, oversized tool output, full-file read, premium model
misuse, repeated summary, unused context expansion). Findings are labeled
`observed`/`estimated`/`hypothesis` per §57; detectors lacking a
prerequisite (undeclared risk, empty ledgers) land in `unresolved`. MCP
exposes the three read projections (`agentops_inspect`, `agentops_compare`,
`agentops_waste`); `evals agentops` covers sections, detection, verdicts and
missing-run honesty.

## Tool surface engineering and MCP compliance (phase 9)

`mcp audit` measures the declared surface — `oversized_schema` and
`poor_description` findings are observed against
`rules/tool_surface.yaml` thresholds; `unbounded_list` and `overlapping`
stay hypothesis-level because signatures cannot prove output size;
`oversized_output` only reports when benchmark bytes are supplied. Phase 9
engineering cut findings from 20 to 0: docstrings were added to nine
tools, `limit` parameters to the ten list-shaped tools (CLI and MCP carry
the same bound via `bound_collections`), and the one remaining overlap
hypothesis became a declared `accepted:` exception in
`rules/tool_surface.yaml` — recorded in the audit with its reason, never
silently dropped.

`mcp disclose --task "..."` is the §41 advisory router — task text is
classified over declared keywords in `rules/tool_disclosure.yaml` into a
task class whose declared tool set becomes `active_tools` (everything else
`dropped_tools`). Unclassified tasks fall back to the full surface and say
so; disclosure never silently narrows. The host still decides what it
loads.

`mcp benchmark` runs the declared `rules/tool_benchmark.yaml` samples on an
isolated root and ranks tools by measured median/p95 response bytes plus a
chars/4 token estimate — always `estimated`, never counted. `usefulness`
compares medians against a declared `max_bytes` when one is set.

`ToolPage`/`paged()` in `output/page.py` is the §42 standard shape —
`summary`/`items`/`refs`/`evidence`/`unresolved`/`pagination` with honest
`total` and `next_offset`.

`docs/mcp-compliance.md` holds the §44 matrix over the twelve required
axes against spec revision 2025-11-25 plus the §45 version-compatibility
notes: the SDK negotiates `2024-11-05`→`2025-11-25`, tool names are the
stable public contract, and breaking changes refuse with
`AF-MCP-TOOL-UNKNOWN` + unlock.

## Forge Protocol (phase 10)

`forge` is the versioned public boundary (`forge-protocol/v1`) over the
governed runtime — a facade, not a second runtime. `forge submit`
validates the `ForgeTaskRequest` against the declared capability matrix
(`AF-FORGE-CAPABILITY-UNKNOWN`), applies the risk gate from
`rules/forge_protocol.yaml` (`sensitive`/`external_mutation`/`destructive`/
`irreversible` need `--acknowledge-risk`, else `AF-FORGE-RISK-GATE`), and
persists the task under `.apiforge/forge/` — nothing executes and nothing
is silently claimed.

`forge attach` links a Forge task to a governed `TaskSpec`; after that
`inspect`/`status` project the governed state (`draft`→`in_progress`,
`accepted`→`completed`, refused states pass through). `result` returns a
`ForgeTaskResult` whose `status` is `ok`, `review` or `unresolved` — a
task without an attached governed spec reports `unresolved` with the gap
named, never a fabricated outcome. `evidence` emits a
`ForgeEvidenceBundle` of observed artifacts (request, status, ledger,
governed spec/events) plus an explicit `unresolved` list.

`forge handoff --to <engine>` prepares a `ForgeHandoff` record for an
engine declared in `rules/forge_protocol.yaml` (`spark-forge`,
`the-forger`); undeclared targets refuse `AF-FORGE-ENGINE-UNKNOWN` and
re-runs refuse `AF-FORGE-HANDOFF-EXISTS`. Delivery stays out-of-band — a
human boundary, not a network call. `health` reports the wire identity,
protocol version, engine and task counts by state.

Five read-only MCP tools (`forge_capabilities`, `forge_health`,
`forge_inspect`, `forge_result`, `forge_evidence`) project the same
payloads; mutation verbs stay CLI-only. `docs/architecture/
forge-kernel-boundary.md` records the §49 kernel-boundary analysis —
what would be extracted for a standalone kernel, and why extraction is
deferred.

## Eval plane (phase 11)

§23 layers evals into a periodic surface: `evals live` runs the
deterministic tier declared in `rules/live_evals.yaml`
(agentic-quality + security-adversarial + memory-evals +
trace-grading) and reports the provider tier as `deferred_external` —
live model calls stay a human-gated external boundary, never CI. The
`LiveEvalReport` contract refuses provider results unless the tier is
`observed`.

`evals trace-grading` grades recorded `AgentSpan` sets against
`rules/trace_rubric.yaml` — five declared dimensions (evidence
coverage, status honesty, unresolved reporting, operation coverage,
retry justification) scored deterministically; empty or mixed-id
traces are `unresolved`, never zero-scored.

`evals security-adversarial` drives nine synthesized §25 attacks
against the platform's own defenses — `evaluate_gates` (memory
poisoning, scope violation, evidence-free persist), allowlist-first
`authorize` (privilege escalation, unknown tool), `propagate`
(cross-agent injection, trust laundering, authority forgery) and
`trust_unit` (tool-output injection). Every defense verdict is
`refused` or `contained`; `escaped` fails loudly.

`evals memory-evals` covers the eight §24 axes — usefulness,
poisoning, stale, wrong-environment, conflicting, cross-task leakage,
retrieval, invalidation — against the real governed store on isolated
roots; setup ingress is `persist_candidate` only.

`evals frontier --report <agentic-quality.json>` computes the
quality×cost×latency Pareto over declared profiles; latency and cost
come from optional sidecars — absent data stays `unresolved`, never
inferred. `docs/security/agentic-threat-model.md` maps every §10–§11
attack class to its defense module and eval evidence.

## Knowledge engine + lab + agentic health (phase 12)

§29 extends the knowledge plane: `FreshnessState` gains `verified`
(hash+version+window all confirmed), `conflicted` (receipts disagree)
and `deprecated` (`expires_at` passed); `PackFreshness` accepts
`last_validated` and an `applies_to` block (`PackApplicability`).
`knowledge drift <domain> --receipt … --now …` rolls one or more
read-only `SourceObservation` receipts into a `KnowledgeDrift` verdict —
zero receipts stay `unresolved`, disagreeing receipts become
`conflicted` with the pairs named, never averaged. `knowledge impact`
emits the declared source→pack→rule→skill→eval relation graph over the
40 bundled packs; the agent→knowledge edge is named `unresolved`
because no declared carrier exists.

§28 ships the opt-in lab catalog (`labs/scenarios.yaml` +
`lab scenarios`): all 13 scenario kinds are declared, 8 carry real
fixture/eval/proof pointers (timeout, retry storm, circuit breaker,
breaking change, schema evolution, backward compatibility,
idempotency, version migration) and 5 are honest declared gaps
(latency regression, auth migration, rate limit, event contract,
pagination) — a cell with neither refuses `AF-LAB-CELL-UNDECLARED`.

`doctor --agentic` emits `AgenticDoctorReport` — cross-plane health
over case, memory (quarantine backlog), trust (policy presence+parse),
telemetry (span store), evals (corpus consistency), sdd (chain
completeness), mcp (registry size) and economy (the §55 checks);
unobservable planes report `unresolved`, never an implied pass.

§30 hardened CI/supply chain: `windows-parity` job (declared py3.12
range, external basetemp, full suite), `wheel-smoke` job (build wheel,
clean-venv install, `apiforge --version` + `capabilities verify`), and
`scripts/supply_chain_audit.py` wired into validate — dependency
inventory + `pip check` + vendor parity + corpus consistency + MCP
surface count; CVE scanning is a named external boundary, not faked.
`docs/decisions/ADR-011-dependency-locking.md` records the declared-
ranges-over-lockfile decision. `evals knowledge-drift` adds the
5-case deterministic corpus (verified/stale/conflicted/deprecated/
unresolved).
