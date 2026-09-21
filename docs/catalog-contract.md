# Catalog, routing and adapter contract

## Rule catalog

`src/apiforge/rules/catalog/*.yaml` — one file per area, merged in sorted
order by `load_catalog()`. File schema: `catalog_version`, `schema_version`,
`area` (required), `retrieved`, `rules[]`. Rule keys are closed:
`id`, `title`, `severity`, `rationale`, `remediation`, `reference`,
`runtime_scope`. `expected_gain` is refused by schema — asserting a saving
requires the cost of the run that never happened.

| Code | Meaning |
|---|---|
| `AF-CATALOG-SCHEMA` | rule/file violates the closed schema (unknown key, `expected_gain`, missing field) |
| `AF-CATALOG-INVALID` | catalog file fails strict YAML parsing |
| `AF-CATALOG-AREA-MISSING` | catalog file lacks the required `area` header |
| `AF-CATALOG-DUPLICATE-RULE` | the same rule id appears in two files |

## Routing

`catalog/routing.yaml` maps `(phase, dominant_area)` → `recommended_agent`;
phases are the canonical SDD vocabulary, areas come from the catalog itself.
`next-step` composes over findings — ties between areas break by highest
severity then area name; unmapped rule_ids are counted, never routed.

| Code | Meaning |
|---|---|
| `AF-ROUTING-SCHEMA` | `routing.yaml` malformed |
| `AF-ROUTING-CATALOG` | the rule catalog failed to load while routing |
| `AF-ROUTING-NO-FINDINGS` | `next-step` invoked with an empty finding list |
| `AF-ROUTING-NO-ROUTE` | no route covers the (phase, dominant_area) pair — refusal, never a guess |

## Spring adapter

`extract_spring` parses `*.java` with tree-sitter — no JDK, no build tool, no
code execution. Non-literal annotation arguments and unresolvable route
shapes are named diagnostics, never inferred.

| Code | Meaning |
|---|---|
| `AF-SPRING-UNRESOLVED-ROUTE` | annotation argument is not a string literal (constant, SpEL, composed meta-annotation) |
| `AF-SPRING-PARSE` | tree-sitter reported a parse error; the file is hashed and extraction is partial |

## Go adapter

`extract_go` parses `*.go` with tree-sitter — no `go` toolchain, no module
resolution, no code execution. Recognized shapes: chi/net-http/gin/echo
verb calls, `mux.Handle`/`HandleFunc` (Go 1.22 `"METHOD /path"` patterns;
bare paths record method `any`), `Route`/`Group` scope joins. `Mount`,
middleware (`Use`, `With`, `Method`) and non-literal paths are named
diagnostics, never inferred.

| Code | Meaning |
|---|---|
| `AF-GO-UNRESOLVED-ROUTE` | route shape could not be resolved statically (non-literal path, `Mount`, middleware) |
| `AF-GO-PARSE` | tree-sitter reported a parse error; the file is hashed and extraction is partial |

## Detail level

`--detail-level` projects CLI payloads: `summary` drops verbose text keys
while refusal codes and `fact_id`s survive; `normal`/`full` are identical
today.

| Code | Meaning |
|---|---|
| `AF-DETAIL-LEVEL` | unknown detail level requested |

## AWS collectors

`collect *` is the only verb family that touches AWS; boto3 imports are
confined to `apiforge.collectors` and enforced by the release gate. Dumps
are canonical JSON + a `manifest.json` receipt; `--now` is the only clock.

| Code | Meaning |
|---|---|
| `AF-COLLECT-AWS` | the AWS call failed; the named operation is in the detail |
| `AF-COLLECT-PATH` | artifact name refused (not a plain `*.json` basename) |
| `AF-COLLECT-ARG` | a collector argument fails its closed set (e.g. WAF scope) |

Beyond `api-gateway`/`lambda`, collectors exist for `sqs` (queue
attributes), `sns` (topic + subscriptions), `eventbridge` (bus + rules +
targets), `iam-role` (role + attached + inline policy documents),
`cognito` (user pool + app clients) and `waf` (one WebACL). Each writes a
dump that `model <same-name>` reads offline into `aws.<svc>.*` facts.

| Code | Meaning |
|---|---|
| `AF-SQS-DUMP` | `queue.json` missing or invalid |
| `AF-SNS-DUMP` | `topic.json`/`subscriptions.json` missing or invalid |
| `AF-EVB-DUMP` | `event-bus.json`/`rules.json`/`targets.json` missing or invalid |
| `AF-IAM-DUMP` | `role.json`/`attached-policies.json`/`inline-policies.json` missing or invalid |
| `AF-COG-DUMP` | `user-pool.json`/`clients.json` missing or invalid |
| `AF-WAF-DUMP` | `web-acl.json` missing or invalid |

## API Gateway dump adapter

`model api-gateway --path` reads a collect dump offline. Missing files and
malformed JSON are named diagnostics, never guesses.

| Code | Meaning |
|---|---|
| `AF-GW-DUMP-MISSING` | an expected dump file is absent |
| `AF-GW-DUMP-INVALID` | a dump file is not valid JSON |

## Builder

`build endpoint` synthesizes Spring skeletons as new-file unified diffs,
evaluates them in the copy sandbox, and promotes into a git worktree only
when the `sensitive`-class gates (`evidence`, `approval`) are satisfied.
It never edits existing files and never writes to the main tree.

| Code | Meaning |
|---|---|
| `AF-BUILD-OP-MISSING` | the requested operationId (or method) is absent from the contract |
| `AF-BUILD-SCHEMA-MISSING` | a schema node has no bounded Java mapping — refused, never guessed |
| `AF-BUILD-TARGET-EXISTS` | a generated path already exists — builds never clobber |

## Agentic layer

`apiforge playbook <coordinator>` renders the executor decomposition declared
in `playbooks.yaml` — the floor on platforms that cannot dispatch subagents.
Coordinator names equal `agents/*.md` profiles; every `recommended_agent` in
`routing.yaml` must have both a profile and a playbook (release-gated).

The economy ledger appends `{verb, detail_level, payload_bytes}` per emitted
payload to `.apiforge/economy.jsonl`; `economy report` aggregates and shows
`detail_level_effect`. Tokens are `tokens_unresolved` without a provider
transcript — measured bytes only, never invented numbers.

| Code | Meaning |
|---|---|
| `AF-PLAYBOOK-NOT-FOUND` | no playbook for the named coordinator; known names are in the detail |

## MCP server and context funnel

`apiforge-mcp` serves the read/compose verbs over MCP (extra `[mcp]`); each
tool takes `detail_level` and records `payload_bytes` to the economy ledger
as `mcp:<verb>` — same payloads as the CLI, same accounting. Mutating verbs
stay CLI-only until policy-gating through MCP is designed.

`context funnel --case <dir>` measures the funnel in bytes per persisted
stage (api-ir → facts → findings → summary projection). Reductions are
ratios of measured bytes; a missing artifact is a named diagnostic, never
a zero silently reported.

| Code | Meaning |
|---|---|
| `AF-MCP-UNAVAILABLE` | `mcp` package absent; unlock: `pip install apiforge[mcp]` |
| `AF-FUNNEL-ARTIFACT-MISSING` | a stage file is absent from the case directory |

## AWS slice 2 — Lambda / Terraform / SAM

`collect lambda` writes `function.json` (Configuration only — the pre-signed
`Code.Location` is never persisted) plus `policy.json` when a resource
policy exists; its absence is data, not failure. `model lambda` reads the
dump offline: env var **names** are extracted, values never read.

`model terraform --path` parses `*.tf` with python-hcl2 — no terraform
binary, no provider calls. Interpolated values (`${...}`) become
`AF-TF-UNRESOLVED`, never resolved by inference.

`model sam --path` parses the template with a `SafeLoader` subclass that
maps intrinsic tags (`!Ref`, `!Sub`, `!GetAtt`) to plain data — never
objects — and every tagged property becomes `AF-SAM-UNRESOLVED`.

| Code | Meaning |
|---|---|
| `AF-LAM-DUMP-MISSING` | `function.json` absent from the dump directory |
| `AF-LAM-DUMP-INVALID` | a dump file is not valid JSON |
| `AF-TF-PARSE` | hcl2 could not parse the `.tf` file |
| `AF-TF-UNRESOLVED` | an attribute is interpolated — named, never inferred |
| `AF-SAM-INVALID` | the template is malformed or has no `Resources` mapping |
| `AF-SAM-UNRESOLVED` | a property is an intrinsic tag — named, never resolved |

## Test and security report readers

`model pact|schemathesis|k6|coverage` and `model zap|semgrep|trivy|gitleaks`
read the tools' standard report files offline — the tools are never run.
These facts are evidence for `rules lookup` and the coordinators; they do
not feed `judge_api_model` (the contract↔code path).

| Code | Meaning |
|---|---|
| `AF-TEST-REPORT-MISSING` | a pact/schemathesis/k6/coverage report file is absent |
| `AF-TEST-REPORT-INVALID` | the report file is not valid JSON |
| `AF-SEC-REPORT-MISSING` | a zap/semgrep/trivy/gitleaks report file is absent |
| `AF-SEC-REPORT-INVALID` | the report file is not valid JSON |

## Release evidence bundle

`report build --case <dir>` composes `report.json`: case manifest, receipt
(optional), catalog/policy digests, finding counts — canonical JSON.
`report sign` appends a signature block pinning `body_sha256`,
`evidence_sha256` and `catalog_sha256` at sign time; `report verify`
recomputes and names each diverged part (`signature_version`, `body`,
`evidence`, `catalog`), exiting 4. Correspondence, never authorship.

| Code | Meaning |
|---|---|
| `AF-REPORT-NO-CASE` | no `case.json` under the given directory |
| `AF-REPORT-NO-RECEIPT` | the `--receipt` path is absent |
| `AF-REPORT-UNSIGNED` | `report verify` on a report without a signature block |

## Executable checks over facts

Rules may carry a closed `check` block (`kind`, dotted `path` into
`measures`/`attrs`, `op` in `gt|ge|lt|le|eq|ne|present`, `value`) — the
threshold stays catalog data, citable like every other field.
`judge --facts <f.json>` applies every check rule to facts emitted by
`model *`; each match is a `confirmed` finding citing the `fact_id`.

| Code | Meaning |
|---|---|
| `AF-JUDGE-INPUT-AMBIGUOUS` | `--facts` combined with `--contract`/`--project` |
| `AF-JUDGE-INPUT-MISSING` | neither `--contract`/`--project` nor `--facts` given |
| `AF-JUDGE-FACTS-INVALID` | the facts payload is not a fact list |

## AsyncAPI

`model asyncapi --path doc.yaml` reads AsyncAPI 2.x/3.x offline.
2.x `publish`/`subscribe` map to operation `action` `send`/`receive`
(provider's perspective); 3.x `operations` carry their own action. Every
`$ref` is a named pointer diagnostic — never dereferenced.

| Code | Meaning |
|---|---|
| `AF-ASYNC-INVALID` | malformed YAML or missing `asyncapi` version key |
| `AF-ASYNC-VERSION` | version is neither 2.x nor 3.x |
| `AF-ASYNC-UNRESOLVED` | a `$ref` was recorded as a pointer, not followed |

## GraphQL and protobuf

`model graphql --path schema.graphql` parses SDL with graphql-core
(confined to `adapters/graphql_` by the release gate) — types become
`graphql.type` facts, root Query/Mutation/Subscription fields become
`graphql.field` facts carrying args, return type and deprecation.
`model proto --path dir/` reads `*.proto` with a deterministic
mini-parser — no protoc; services/rpcs/messages become `proto.*` facts,
streaming flags are data.

| Code | Meaning |
|---|---|
| `AF-GQL-INVALID` | graphql-core could not parse the SDL |
| `AF-PROTO-PARSE` | unbalanced braces or undecodable .proto file |
| `AF-PROTO-EMPTY` | no `*.proto` under the given directory |

## Profiler exports

`model jfr|pprof|pyroscope` read profiler exports offline — `jfr print
--json`, `go tool pprof -top` text, and Pyroscope flamebearer JSON. Entries
are capped at the top 20; a `truncated` attr names when more existed.

| Code | Meaning |
|---|---|
| `AF-PERF-REPORT-INVALID` | the profile export is unreadable or lacks the expected shape |

## Strangler cut plan

`plan strangler --baseline facts_a.json --candidate facts_b.json` compares
`code.route` facts from two inventories. Baseline routes are `migrated`
(candidate serves method+path — `cut_requires` names the parity evidence
still owed: contract diff + consumer confirmation), `missing` (cut blocker),
or `stale` (unreachable in baseline); candidate-only routes are `added`.

| Code | Meaning |
|---|---|
| `AF-PLAN-NO-ROUTES` | neither payload carries `code.route` facts |

## Debate protocol

`debate open --case <dir> --question "..." --sides a,b --now ISO` creates
`debates/<id>.json` in the case. `debate submit` appends a position — every
position must cite `fact_id` evidence (an opinion without evidence is
refused). `debate close --referee <name>` resolves with `--decision` or
records `unresolved` when omitted; closing requires submissions on >= 2
distinct sides. A closed debate refuses further mutation.

| Code | Meaning |
|---|---|
| `AF-DEBATE-NOT-FOUND` | no debate with that id in the case |
| `AF-DEBATE-SIDES` | fewer than two distinct sides at open |
| `AF-DEBATE-SIDE` | submission on a side not declared at open |
| `AF-DEBATE-NO-EVIDENCE` | position without `fact:`-prefixed citations |
| `AF-DEBATE-NO-QUORUM` | close attempted with < 2 sides having submitted |
| `AF-DEBATE-CLOSED` | mutation attempted on a resolved/unresolved debate |

## Dispatch and agent mirrors

`dispatch run --coordinator <name> --case <dir>` executes each playbook step
whose verb is dispatchable and whose inputs are in the context; ran steps
record `output_sha256`, pending steps name their missing inputs, and
`collect *` is refused inside dispatch (it touches AWS). The run record
persists under `case/dispatch/`.

`agents sync` regenerates `.agents/agents/` and `.claude/agents/` as
byte-identical mirrors of `agents/*.md`; `agents check` and the release
gate fail on drift.

| Code | Meaning |
|---|---|
| `AF-DISPATCH-NO-PLAYBOOK` | no playbook for the named coordinator |

## Key-bound signing (Ed25519)

`report keygen --name <n>` writes `<n>.pem`/`<n>.pub.pem` under
`--keys-dir`. `report sign --key <priv.pem>` adds `algorithm: ed25519`,
`public_key_sha256` (fingerprint of the derived public key) and
`signature_b64` over the canonical hash-binding block. `report verify
--pubkey <pub.pem>` verifies cryptographically: `crypto` is
`valid|invalid|unverified|absent`; divergence names `signature_key`
(fingerprint mismatch) or `signature_crypto` (bad signature). A valid
signature proves possession of the private key — never identity.
`cryptography` is confined to `apiforge/report/` by the release gate.

| Code | Meaning |
|---|---|
| `AF-KEY-EXISTS` | key name already present in the keys dir |
| `AF-KEY-NOT-ED25519` | PEM is not an Ed25519 key |

## Executing scanner binaries (`run tool`)

`run tool <semgrep|trivy|gitleaks|k6> --target <path> --out <report>`
executes the binary from a fixed argv template — resolved by
`shutil.which`, no shell, bounded by `--timeout` — then reads the produced
report through the same reader `model <tool>` uses. `--dry-run` prints the
argv without executing. The analyzed code is still never executed: the
scanner runs, the target stays data. `zap` is deliberately absent
(baseline needs a daemon/docker, not a bare binary).

| Code | Meaning |
|---|---|
| `AF-RUN-TOOL-UNKNOWN` | tool not in the allowlist |
| `AF-RUN-TOOL-MISSING` | binary absent from PATH; names the install path |
| `AF-RUN-CONFIG-MISSING` | semgrep without a local `--config` (`auto` hits the network) |
| `AF-RUN-TIMEOUT` | the run exceeded `--timeout` |
| `AF-RUN-NO-REPORT` | the tool exited without writing the report file |

## Provider tokens (`economy report`)

Bytes are always counted; tokens are counted only with
`--transcript <jsonl>` (host transcript — `message.usage` summed per
`message.model`; unparseable lines are counted in `unparsed_lines`).
`--estimate` adds `token_estimate` — a labeled `payload_bytes/4` heuristic,
never presented as counted (`counted: false`). Dollar cost requires
`--transcript` **and** `--cost-basis <yaml>` (model→`input_per_mtok`/
`output_per_mtok`); a model outside the basis lands in
`cost_basis_missing`, never priced by inference.

| Code | Meaning |
|---|---|
| `AF-ECONOMY-TRANSCRIPT-MISSING` | no transcript file, or `--cost-basis` without `--transcript` |
| `AF-ECONOMY-COST-BASIS-MISSING` | basis file absent or not a model→rates mapping |

## Canonical contracts (`contract`)

`contract list` enumerates the registered `<Name>/v1` contracts;
`contract show <name>` emits the JSON schema. Every contract is frozen and
closed (`extra: forbid`); `version` is a `Literal[1]` — a v2 lands as a
sibling class, never an in-place change. Docs live in
`docs/contracts/<Name>-v1.md`, kept in parity with the registry by the
release gate.

| Code | Meaning |
|---|---|
| `AF-CONTRACTS-UNKNOWN` | contract name not in the registry |

### Tasks (`task`, `brief`)

A task is a sealed, budgeted unit of work under
`<root>/.apiforge/tasks/<id>/` — `task.yaml`, append-only `revisions/`,
`history.jsonl`, `runs/`. Lifecycle:
`draft -> reviewed -> sealed -> ready -> running -> awaiting_supervision ->
accepted`, with `rejected`, `parked`, `blocked`, `expired` as refusal or
terminal states. `task review` on a sealed task writes a new unsealed
revision — amendment always invalidates the prior seal. `task seal` binds an
Ed25519 signature to the exact revision (key lives outside the task; the
executor never holds it). `task run` executes the recipe from
`rules/recipes.yaml` through the same `dispatch_step` unit as playbooks,
inside `budgets` (max rounds, max calls, deadline) with a no-progress
breaker. The run record carries `inputs_missing` — the union of ctx fields
the recipe's verbs need, derived from the dispatch tables, named upfront.
`task accept` requires `accepted_by` distinct from the executor and
at least one `--evidence`. `brief show` renders the OutcomeBrief — `DONE` is
refused while gaps, missing acceptance, or open items remain.

Mutation verbs (`build endpoint`) live in a separate dispatch table and are
refused by ordinary `dispatch_step`; only the task runner may invoke them,
after `policy.decide("build.endpoint")` returns `allow` and the spec's
`writable_paths` covers `.apiforge`. `gate.*` task inputs become policy
decision detail. The generated diff lands in the sandbox — the main tree is
never touched by a task step; promotion stays a separate human action.

| Code | Meaning |
|---|---|
| `AF-TASK-ID` | task id fails `^[a-z0-9][a-z0-9-]{0,63}$` |
| `AF-TASK-EXISTS` | `task create` on an existing id |
| `AF-TASK-NOT-FOUND` | no task under the root |
| `AF-TASK-TRANSITION` | state machine refuses the move |
| `AF-TASK-FIELD` | `task review --set` names an unknown or non-scalar field |
| `AF-TASK-INPUT` | `--input` is not `field=value` or names an unknown field |
| `AF-TASK-UNSEALED` | `task ready|run` while the current revision has no seal |
| `AF-TASK-SEALED` | mutation attempted on a sealed revision |
| `AF-TASK-REVISION-MISSING` | spec.revision points at a revision file that is absent |
| `AF-TASK-RECIPE` | `strategy` names no recipe in `rules/recipes.yaml` |
| `AF-TASK-MUTATION-GATED` | mutation verb outside the task runner, or the task lacks policy `allow` / a `.apiforge` writable scope |
| `AF-RECIPE-INVALID` | `recipes.yaml` is malformed |

### Graph (`graph`)

`graph build` reads a case directory into `nodes.jsonl`/`edges.jsonl` —
canonical lines sorted by id, each node line carrying a `sha256` over its
`{id,kind,props}` payload so a tampered line is detected on load. Queries
are closed-vocabulary (`--kind`, `--edge`, `--prop k=v`); `impact` traverses
in reverse, `trace` returns the shortest directed path or names the pair
unreachable, `coverage` names unverified findings / unimplemented
operations / unreferenced facts. `export` copies canonical bytes plus a
digest manifest; `--format neptune` is a named stub, not a silent no-op.

| Code | Meaning |
|---|---|
| `AF-GRAPH-NOT-FOUND` | no `nodes.jsonl` under the graph directory |
| `AF-GRAPH-NO-CASE` | `graph build` found no `case.json` under `--case` |
| `AF-GRAPH-INVALID` | a node/edge line fails the contract schema |
| `AF-GRAPH-HASH-MISMATCH` | a node line's `sha256` diverges from its payload |
| `AF-GRAPH-KIND` | query names an unknown node or edge kind |
| `AF-GRAPH-NODE` | `impact`/`trace` name a node absent from the graph |
| `AF-GRAPH-INPUT` | a source artifact is unreadable or malformed |
| `AF-GRAPH-FORMAT` | export format named but not implemented (e.g. `neptune`) |

### Index (`index`)

`index build` writes `.apiforge/index/{files,symbols,routes,facts}.jsonl`
plus `index.json` — all derived from extractor output, all canonical JSONL.
`index status` compares the live tree against `files.jsonl` and names
added/removed/changed. The extractor cache lives at
`.apiforge/cache/<sha256(extractor_version|framework|source_digest)>.json`;
a changed file yields a new key (stale entries are unreachable, never
wrong), a corrupt cache file self-heals as a miss, and every hit is
recorded in the economy ledger as `cache:extract:<framework>`.

| Code | Meaning |
|---|---|
| `AF-INDEX-NOT-FOUND` | `--project` is not a directory |
| `AF-INDEX-FRAMEWORK` | no extractor registered for the framework |
| `AF-INDEX-NOT-BUILT` | `index status` without a prior `index build` |

### Data access (`model redis`)

`model redis --path <dir>` scans a project tree offline for Redis/Valkey call
sites. Python files go through `ast`: a receiver is bound when assigned a
`redis.Redis`/`valkey.Valkey`/`from_url` constructor (`binding: constructor`)
or when it uses a conventional name while a redis package is imported
(`binding: name` — emitted honestly as heuristic). Java (`jedis`,
`redisTemplate`, `opsFor*()`) and Go (`rdb`, `redisClient`, `valkey`) files
are pattern-matched only when a client import is present, always with
`binding: name`. Each call emits `data.redis.command`; mutating commands
also emit `data.redis.write` with `ttl_seconds` when a literal expiry is
visible (otherwise absent — AF-DATA-002 fires on absence, never on a guess).
Aggregation lands in `data_access_ir` (the `DataAccessIR` contract):
`entities` = distinct literal keys, `access_patterns` = distinct commands,
`unresolved` = diagnostic codes.

Catalog area `DATA` (8 rules, `check:`-executable): AF-DATA-001 KEYS,
AF-DATA-002 write-without-TTL, AF-DATA-003 FLUSHALL, AF-DATA-004 FLUSHDB,
AF-DATA-005 CONFIG, AF-DATA-006 DEBUG, AF-DATA-007 MONITOR, AF-DATA-008 SAVE.

| Code | Meaning |
|---|---|
| `AF-REDIS-PARSE` | a `.py` file failed `ast.parse` — extraction continues |
| `AF-REDIS-HEURISTIC-BINDING` | receivers matched by name only — binding unproven |

### Telemetry (`model otel`, `perf compare`)

`model otel --path export.json` reads an OTLP/JSON trace export
(`resourceSpans[].scopeSpans[].spans[]`) — offline, never a live collector.
Spans aggregate per operation (`METHOD http.route`, else span name) into
`perf.otel.operation` facts (count, mean_ms, p95_ms nearest-rank, max_ms)
plus one `perf.otel.run` fact; the payload also carries `performance_run`
(the `PerformanceRun` contract). Spans without usable timestamps are counted
and named; a missing `service.name` leaves the run subject unresolved.

`perf compare --baseline A --candidate B --threshold-pct N [--min-samples M]`
runs `compare_runs`/`detect_regression` over two PerformanceRun payloads
(bare contract JSON or a `model otel` payload). Shared operations are
compared on `mean_ms`/`p95_ms`; regressions name operation, metric, both
values and `delta_pct`. Operations on only one side are named
`added`/`removed`; shared operations under `min_samples` are named
`insufficient_data`, never judged. The threshold is an explicit argument.

| Code | Meaning |
|---|---|
| `AF-OTEL-REPORT-INVALID` | export unreadable or missing `resourceSpans` |
| `AF-OTEL-SPAN-INCOMPLETE` | spans lack usable timestamps — counted, named |
| `AF-OTEL-SERVICE-UNKNOWN` | no `service.name` resource attribute |
| `AF-PERF-RUN-INVALID` | compare input is not a PerformanceRun payload |

### Autonomy modes (`autonomy`)

Three ordered modes, persisted in `.apiforge/autonomy/mode.json` (absent
file means `observe` — the safest reading of unknown):

- `observe`: every action is evaluated by the policy engine and recorded;
  nothing executes.
- `supervised`: `allow` executes; `gate` is recorded `pending` with its
  missing requirements named; a runbook halts on the first non-executed
  step.
- `continuous`: same per-action semantics; a runbook records the skip and
  continues past `pending`/`denied` steps.

`autonomy set` is itself a policy action (`autonomy.set`, class
`sensitive`) — under the default policy, escalation requires the gate's
requirements in `--detail` (evidence, approval), while the shipped rule
`autonomy-observe-always-allowed` lets de-escalation to `observe` through.
Every evaluation appends to `ledger.jsonl` (mode, decision, rule, missing
requirements, outcome: `observed`/`executed`/`pending`/`denied`/
`not_dispatchable`/`error`, plus `output_sha256` on `executed`). Only verbs
in the dispatch table can ever execute — mutation stays outside the
boundary by construction. Runbooks are data (`rules/runbooks.yaml`):
ordered `{verb, class}` steps over the same dispatch context.

| Code | Meaning |
|---|---|
| `AF-AUTONOMY-MODE-UNKNOWN` | mode string not in observe/supervised/continuous |
| `AF-AUTONOMY-MODE-CORRUPT` | `mode.json` unreadable or fails schema |
| `AF-AUTONOMY-SET-REFUSED` | policy refused the mode change; missing requirements named |
| `AF-AUTONOMY-RUNBOOK-UNKNOWN` | no runbook with that name |
| `AF-AUTONOMY-RUNBOOK-SCHEMA` | runbooks.yaml malformed |
| `AF-AUTONOMY-DETAIL` | `--detail` pair is not `key=value` |
