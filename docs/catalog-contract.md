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
| `AF-INPUT-NOT-FOUND` | a declared `--path`/`--project`/`--findings` argument does not exist |
| `AF-INPUT-FRAMEWORK-UNKNOWN` | `--framework` names an adapter that is not registered |
| `AF-INPUT-INVALID` | an input argument fails shape validation (e.g. dump dir layout) |
| `AF-PERF-PLAN-INVALID` | declarative performance plan fails endpoint, threshold or generator validation |
| `AF-OBS-READ-PLAN-INVALID` | vendor read plan fails provider, window or signal validation |
| `AF-OBS-READ-PROVIDER` | requested observability provider has no registered read adapter |
| `AF-OBS-READ-COUNT` | fixture receipt received a negative record count |
| `AF-OBS-CREDENTIAL-INVALID` | credential metadata reference is invalid |
| `AF-OBS-CREDENTIAL-PROVIDER` | credential provider is unsupported |
| `AF-OBS-CREDENTIAL-REFERENCE` | credential reference is empty or invalid |
| `AF-OBS-CREDENTIAL-SOURCE` | credential source is outside the closed broker vocabulary |
| `AF-OBS-ADAPTER-PROVIDER` | read adapter, plan and credential provider do not match |
| `AF-HOST-ACTIVATION-INVALID` | host activation plan input is invalid |
| `AF-HOST-ACTIVATION-HOST` | requested host has no activation plan |
| `AF-DIST-PATH-INVALID` | selected installation, state, config or cache path is empty, invalid or not usable |
| `AF-DIST-ASSET-MISSING` | packaged API Forge asset or host asset manifest is missing or unreadable |
| `AF-DIST-ASSET-DIVERGED` | packaged asset hash does not match the declared source hash |
| `AF-MANIFEST-INVALID` | project or workspace manifest is missing, malformed or violates its versioned schema |
| `AF-MANIFEST-SECRET` | project, workspace or user config contains secret-like material refused by the local contract |
| `AF-MANIFEST-WRITE` | minimal manifest could not be written to the requested user-owned location |
| `AF-ROOT-NOT-FOUND` | bounded discovery could not find a project, repository or workspace root |
| `AF-WORKSPACE-REPO-MISSING` | workspace repository entry points to a missing local root |
| `AF-CONTEXT-SCOPE-INVALID` | context scope, impact mode or required target is outside the closed vocabulary |
| `AF-CONTEXT-TARGET-NOT-FOUND` | requested context target was not observed in the selected scope |
| `AF-HOST-CONFLICT` | generated host output conflicts with a user-owned file; no overwrite is performed |
| `AF-HOST-TEMPLATE` | packaged host template could not be rendered from the supplied safe values |
| `AF-MCP-OPTIONAL-UNAVAILABLE` | optional MCP capability is not installed; local CLI remains available |
| `AF-KNOW-PACKAGED-MISSING` | installed package has no bundled knowledge assets for the requested operation |

## Governed agentic state

Memory and blackboard are local append-only data planes. Their refusals carry
the rejected field and a safe unlock; none is an instruction channel or an
authorization to mutate an external system.

| Code | Meaning |
|---|---|
| `AF-MEMORY-SCOPE-DENIED` | candidate scope is not allowed by the active MemoryPolicy |
| `AF-MEMORY-UNTRUSTED` | external-untrusted data cannot be persisted under the policy |
| `AF-MEMORY-EVIDENCE-REQUIRED` | institutional/semantic memory has no verified evidence refs |
| `AF-MEMORY-MODEL-UNVERIFIED` | model-generated data cannot be promoted automatically |
| `AF-MEMORY-TRUST-INSUFFICIENT` | candidate trust is below the policy minimum (legacy code; superseded by `AF-MEMORY-TRUST-QUARANTINED` in the §14 pipeline) |
| `AF-MEMORY-TRUST-QUARANTINED` | candidate trust is below the policy minimum; parked in the append-only quarantine log for human review |
| `AF-MEMORY-EXPIRED` | candidate expiry is already past at persist time |
| `AF-MEMORY-GATE-DENIED` | a §14 gate failed without a more specific code |
| `AF-MEMORY-QUARANTINE-NOT-FOUND` | review named a candidate with no pending quarantine row |
| `AF-MEMORY-QUARANTINE-REJECTED` | human review rejected a quarantined candidate; nothing reaches the record log |
| `AF-MEMORY-NOT-FOUND` | invalidation named a memory absent from the append-only store |
| `AF-MEMORY-CANDIDATE-NOT-FOUND` | persistence named a candidate absent from the store |
| `AF-MEMORY-FRESHNESS-UNRESOLVED` | an expiry exists but retrieval received no explicit clock |
| `AF-MEMORY-STORE-CORRUPT` | a persisted memory row failed its closed contract |
| `AF-BLACKBOARD-STORE-CORRUPT` | a persisted blackboard row failed its closed contract |
| `AF-CHECKPOINT-NOT-FOUND` | the requested semantic checkpoint is absent |

## Trust Plane and tool authorization

The Trust Plane annotates every context-bearing surface with origin, trust
level, taint and instruction authority; tool authorization is allowlist-first
and defaults to deny. Every refusal carries the denied field and a safe unlock.

| Code | Meaning |
|---|---|
| `AF-TRUST-PROPAGATION-EMPTY` | taint propagation requires at least one source unit |
| `AF-TOOL-PROFILE-MISSING` | the tool has no declared risk profile in `rules/tool_risk.yaml` |
| `AF-TOOL-AUTHZ-DENIED` | the role has no permission set, or the tool is not in its allowlist |
| `AF-TOOL-DENIED` | the tool is explicitly denied for the role |
| `AF-TOOL-RISK-DENIED` | the tool's declared risk classes exceed the role's grant |

## Decision governance

| Code | Meaning |
|---|---|
| `AF-GOV-APPROVAL-REQUIRED` | risky proposal has no human ApprovalGate |
| `AF-GOV-APPROVAL-PENDING` | the human approval gate has not been decided |
| `AF-GOV-APPROVAL-REJECTED` | the human approval gate rejected the proposal |
| `AF-GOV-POLICY-DENIED` | selected policy disallows the proposed mutation risk |
| `AF-GOV-EVIDENCE-REQUIRED` | non-read-only proposal lacks evidence references |
| `AF-GOV-STORE-CORRUPT` | persisted decision result failed its closed contract |
| `AF-GOV-DECISION-CONFLICT` | request id was reused with a different gate result |

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

Evolution policy is local and evidence-gated. A mode or promotion state is not
an execution authorization by itself; the runtime persists the gate and uses
the static route as the only Wave 0 fallback.

| Code | Meaning |
|---|---|
| `AF-EVOLUTION-POLICY` | `runtime.routing_evolution` is missing, malformed or violates the bounded policy |
| `AF-EVOLUTION-PROMOTION` | route promotion is not active because mode, coverage or rollback evidence is unresolved |
| `AF-RUNTIME-EVOLUTION` | persisted `evolution.json` is missing its typed `PromotionGate` shape |
| `AF-RUNTIME-ROUTING-PLAN` | persisted `routing-plan.json` is missing or fails the typed `RoutingPlan/v1` shape |
| `AF-RUNTIME-SCORECARD-FRESHNESS` | scorecard promotion is blocked because an observation is stale or unresolved |
| `AF-RUNTIME-SCORECARD-OBSERVATION` | an observed scorecard signal has no receipt/evidence reference |

## API/Git/CI change control

The change-control adapters are read-only and produce replayable bundles. These
codes describe malformed inputs or bounded transport failures; none authorizes
provider mutation.

| Code | Meaning |
|---|---|
| `AF-CHANGE-REPLAY-MISSING` | replay bundle path does not exist |
| `AF-CHANGE-REPLAY-SHAPE` | replay bundle is not a JSON object |
| `AF-CHANGE-REPLAY-CONTRACT` | replay bundle fails `af-change-bundle/1` validation |
| `AF-CHANGE-INPUT-MISSING` | required contract or project field is absent |
| `AF-CHANGE-INPUT-NOT-FOUND` | declared contract or project path does not exist |
| `AF-CHANGE-ANALYZE` | analysis failed before a named analysis code was available |
| `AF-CHANGE-NEXT-STEP` | routing stage could not produce a governed next step |
| `AF-CHANGE-GRAPH` | provenance graph stage failed |
| `AF-CHANGE-EVIDENCE` | evidence receipt stage failed |
| `AF-CHANGE-BRIEF` | outcome brief could not be materialized |
| `AF-CHANGE-RESULT-SHAPE` | canonical result payload is not a JSON object |
| `AF-CHANGE-RESULT-MISSING` | governed result is absent when verification or publishing starts |
| `AF-CHANGE-RECEIPT` | live collection receipt could not bind to the sanitized bundle |
| `AF-CHANGE-PUBLISH-RESULT` | canonical result is absent or malformed for publishing |
| `AF-CHANGE-PUBLISH-JUNIT` | JUnit projection could not be written |
| `AF-CHANGE-PUBLISH-MARKDOWN` | Markdown projection could not be written |
| `AF-CHANGE-PUBLISH-SARIF` | SARIF projection could not be written |
| `AF-CHANGE-PUBLISH-HTML` | standalone HTML projection could not be written |
| `AF-GITHUB-HTTP` | GitHub read request returned an HTTP failure |
| `AF-GITHUB-NETWORK` | GitHub read transport could not reach the provider |
| `AF-GITHUB-JSON` | provider response was not valid JSON |
| `AF-GITHUB-PAYLOAD` | provider response has an unexpected JSON shape |
| `AF-GITHUB-AUTH` | required read-only token is absent; use replay or supply the host credential |
| `AF-GITHUB-HOST-APPROVAL` | dedicated host mutation lacks explicit CI policy approval |
| `AF-GITHUB-PR-RECEIPT` | GitHub PR mutation could not be read back into a receipt |
| `AF-GITHUB-PR-NOT-FOUND` | requested auto-merge has no matching open pull request |
| `AF-GITHUB-HOST-PR` | dedicated GitHub host command failed or lacks its configured policy |
| `AF-EXTERNAL-URL` | external read URL is not an absolute HTTP(S) reference |
| `AF-EXTERNAL-RECEIPT` | external receipt timestamps are invalid or cannot prove freshness |
| `AF-PLATFORM-VERTICAL` | requested runtime vertical is not in the allowlisted platform set |
| `AF-MCP-CHANGE-CONTROL` | MCP change-control input failed before a typed code was available |
| `AF-MCP-GITHUB-COLLECT` | MCP GitHub collection failed before a typed transport code was available |

Public change-control refusals serialize `code`, `detail`, `field` and
`unlock`. The unlock is remediation guidance only; it never authorizes a
provider mutation or bypasses policy.

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

Batch 2 adds `dynamodb` (table + continuous-backup/PITR status), `docdb`
and `neptune` (`rds:DescribeDBClusters` dumps — the `engine` field in the
dump disambiguates), `stepfunctions` (state-machine description),
`cloudwatch` (metric alarms by prefix), `xray` (sampling rules +
encryption config), `kms` (key metadata + rotation status), `secrets`
(secret *metadata* — `GetSecretValue` is never called), `vpc-endpoints`
(endpoints of a VPC — `private_dns_enabled` is measured only on
`Interface` endpoints, where the field exists) and `s3` (bucket posture:
encryption, public-access block, versioning — objects are never listed).
A missing S3 configuration is recorded as `{"absent": <aws-error-code>}`
in the artifact, so the reader sees measured absence, not an inferred
default.

| Code | Meaning |
|---|---|
| `AF-SQS-DUMP` | `queue.json` missing or invalid |
| `AF-SNS-DUMP` | `topic.json`/`subscriptions.json` missing or invalid |
| `AF-EVB-DUMP` | `event-bus.json`/`rules.json`/`targets.json` missing or invalid |
| `AF-IAM-DUMP` | `role.json`/`attached-policies.json`/`inline-policies.json` missing or invalid |
| `AF-COG-DUMP` | `user-pool.json`/`clients.json` missing or invalid |
| `AF-WAF-DUMP` | `web-acl.json` missing or invalid |
| `AF-DDB-DUMP` | `table.json`/`backups.json` missing or invalid |
| `AF-DOCDB-DUMP` | `cluster.json` missing or invalid |
| `AF-NEPTUNE-DUMP` | `cluster.json` missing or invalid |
| `AF-SFN-DUMP` | `state-machine.json` missing or invalid |
| `AF-CW-DUMP` | `alarms.json` missing or invalid |
| `AF-XRAY-DUMP` | `sampling-rules.json`/`encryption-config.json` missing or invalid |
| `AF-KMS-DUMP` | `key.json`/`rotation.json` missing or invalid |
| `AF-SECRETS-DUMP` | `secret.json` missing or invalid |
| `AF-VPC-DUMP` | `endpoints.json` missing or invalid |
| `AF-S3-DUMP` | `encryption.json`/`public-access.json`/`versioning.json` missing or invalid |
| `AF-ALB-DUMP` | `load-balancer.json`/`listeners.json`/`target-groups.json`/`attributes.json` missing or invalid |
| `AF-ECS-DUMP` | `services.json`/`task-definitions.json` missing, invalid, or a `describe_services` failure was recorded |
| `AF-EKS-DUMP` | `cluster.json` missing or invalid |
| `AF-EC2-DUMP` | `instances.json` missing or invalid |
| `AF-MSK-DUMP` | `cluster.json` missing or invalid |
| `AF-ECACHE-DUMP` | `replication-group.json` missing or invalid |

## Data-access adapters (`model mongo`/`dynamodb-access`/`neptune-access`)

Static call-site extraction over the project tree — Python via `ast`
(receiver bound by constructor or by name, always declared), Java/Go by
pattern when the driver package is imported. Composite postures are
computed from *declared* arguments only: `full_scan` (DynamoDB `scan`
without Limit/FilterExpression/IndexName), `unfiltered_write`
(MongoDB `delete_many`/`update_many`/`replace_one` with a visibly empty
filter), `unbounded`/`unbounded_find` (no `limit=`/`.limit(`/`.range(`/
`LIMIT` visible). Aggregated into `data_access_ir` per database.

| Code | Meaning |
|---|---|
| `AF-MONGO-PARSE` | a `*.py` file fails to parse |
| `AF-MONGO-HEURISTIC-BINDING` | receivers matched by name, not constructor |
| `AF-DYNAMO-PARSE` | a `*.py` file fails to parse |
| `AF-DYNAMO-HEURISTIC-BINDING` | receivers matched by name, not constructor |

## Graph-database adapters (Neptune, Neo4j)

`model graph-access|neptune-access|neo4j-access` emit `data.graph.query` facts
(`vendor`, `language`, `bounded`, `mutation`, shape-risk booleans) and a
`GraphAccessIR`; `model graph-explain` turns one explain/profile dump into a
`GraphPlanIR` and a `data.graph.plan` fact. Rules live in area `GDB`
(`AF-GDB-001..010` on call sites, `AF-GDB-020..025` on plans) plus
`AF-DATA-013`. `AF-GRAPH-*` stays reserved for the system graph.

| Code | Meaning |
|---|---|
| `AF-GDB-PARSE` | a `*.py` file fails to parse; the scan continues |
| `AF-GDB-HEURISTIC` | receivers matched by name (Python) or call sites matched by pattern (Java/Go/TypeScript) |
| `AF-GDB-DYNAMIC-QUERY` | query text is not a literal; bounds stay unresolved |
| `AF-GDB-PLAN-FORMAT` | a dump matches no known plan format, or `--format` is outside the closed set; unlock: pass `--format` |
| `AF-GDB-PLAN-PARSE` | a dump is missing, empty or yields no operators; unlock: pass the unmodified explain/profile output |
| `AF-GDB-COLLECT-ARG` | `collect neptune-explain` got an unknown language, an empty query/endpoint, or both/neither of `--query`/`--query-file` |
| `AF-GDB-COLLECT-OP` | an operation outside the read-only `neptunedata` allowlist was requested |
| `AF-GDB-EXPLAIN-SPARQL` | SPARQL explain has no `neptunedata` operation; unlock: import a dump with `model graph-explain` |
| `AF-GDB-PROFILE-MUTATION` | the query mutates the graph; only read queries are explained |
| `AF-GDB-PROFILE-READER` | `--profile` executes the query and needs `--reader-endpoint` equal to `--endpoint` |
| `AF-GDB-PROFILE-DYNAMIC` | `--profile` needs literal query text |

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
| `AF-PLAN-PROFILE-INVALID` | WorkloadProfile payload unreadable or schema-invalid |

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
| `AF-DEBATE-PARTICIPANTS` | adaptive plan cannot satisfy its bounded quorum |
| `AF-DEBATE-BUDGET` | adaptive debate exceeded its declared round/participant budget |

The adaptive debate extension records a bounded participant plan, retry budget,
replay id and dissent alongside the existing debate state machine. It never
turns an unsupported participant into evidence.

## Experience and compatibility surfaces

| Code | Meaning |
|---|---|
| `AF-TUI-UNAVAILABLE` | optional Textual dependency is unavailable; use the Rich/JSON fallback |
| `AF-MIGRATION-RECEIPT` | a runtime receipt names an ecosystem/version absent from the declared matrix |
| `AF-MIGRATION-INTERPRETER` | a matrix probe was not an allowlisted Python interpreter or could not complete |
| `AF-HOST-DECLARATION` | a local host capability declaration is unreadable or schema-invalid |
| `AF-DEVIN-OBJECTIVE` | Devin payload objective is empty |
| `AF-DEVIN-PAYLOAD` | Devin payload input is malformed or outside its closed vocabulary |
| `AF-DEVIN-SANDBOX-UNAVAILABLE` | Devin CLI sandbox was requested on native Windows; use WSL 2 or remove the flag |
| `AF-DEVIN-DESTRUCTIVE-COMMAND` | Devin hook blocked an irreversible repository or Docker cleanup command |

## Dispatch and agent mirrors

`dispatch run --coordinator <name> --case <dir>` executes each playbook step
whose verb is dispatchable and whose inputs are in the context; ran steps
record `output_sha256`, pending steps name their missing inputs, and
`collect *` is refused inside dispatch (it touches AWS). The run record
persists under `case/dispatch/`.

`agents sync` renders `.agents/agents/`, `.claude/agents/` and
`.codex/agents/` from `agents/*.md` (see *Agent roster* below); `agents check`
and the release gate fail on drift. A deprecated coordinator name resolves
through `rules/agent_aliases.yaml` with `AF-AGENT-ALIAS-DEPRECATED`.

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
(baseline needs a daemon/docker, not a bare binary). The result records
`tool_version` (measured via `<binary> --version`, `null` when the probe
yields nothing — never guessed) and `environment` (os/arch), plus the
fixed argv, exit code, report path and input hashes.

| Code | Meaning |
|---|---|
| `AF-RUN-TOOL-UNKNOWN` | tool not in the allowlist |
| `AF-RUN-TOOL-MISSING` | binary absent from PATH; names the install path |
| `AF-RUN-CONFIG-MISSING` | semgrep without a local `--config` (`auto` hits the network) |
| `AF-RUN-TIMEOUT` | the run exceeded `--timeout` |
| `AF-RUN-NO-REPORT` | the tool exited without writing the report file |
| `AF-RUN-IMPORT-ONLY` | tool is in the registry as a report reader only — `run` never executes it; feed the report to `model <tool>` |
| `AF-RUN-PROD-GATE` | load script targets a remote or unresolvable URL — policy gate `sensitive` requires `approval`; all-localhost scripts run free |

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

## Context Gateway (`context capsule`, `context expand`, `economy stats|explain`, `evals economy`)

`context capsule` emits `ContextCapsule/v1`: evidence for one operation as
`ctx://sha256/<hex>` refs selected from the persisted case graph (L0 intent →
L1 fingerprint → L2 impact → L3 refs → L4 inline focused code) under a byte
budget. Objects live in `<root>/.apiforge/ctx/` and are hash-verified on
`context expand`. Budget exhaustion and a missing case are partial results
(exit 0, explicit `status` + refusal inside the capsule); integrity and
reference errors are refusals (exit 2). Attribution rows in `economy.jsonl`
carry `payload_bytes: 0` so `economy report` totals are unchanged.

| Code | Meaning |
|---|---|
| `AF-CONTEXT-TARGET-INVALID` | `--target` is not `<METHOD> /path` (or `<METHOD>:/path`); unlock: pass an operation such as `POST /orders` |
| `AF-CONTEXT-BUDGET-EXHAUSTED` | not every selected ref fits `--budget-bytes`; capsule returned with `status: unresolved` and whole refs only; unlock: raise the budget or lower `--level` |
| `AF-CTX-GRAPH-UNAVAILABLE` | no `case.json` under the case dir; capsule degraded to L0/L1; unlock: `apiforge analyze --out-dir <case>` |
| `AF-CTX-REF-INVALID` | ref is not `ctx://sha256/<64 hex>`; unlock: pass a ref exactly as emitted |
| `AF-CTX-REF-NOT-FOUND` | ref absent from `<root>/.apiforge/ctx`; unlock: rebuild the capsule in the same root |
| `AF-CTX-HASH-MISMATCH` | stored object no longer hashes to its ref; content is never returned; unlock: delete the object and rebuild |
| `AF-ECONOMY-RUN-NOT-FOUND` | `economy explain` has no attribution rows for the run id; unlock: pass a `run_id` printed by `context capsule` |
| `AF-ECONOMY-USAGE-EMPTY` | `economy record-usage` called without `--transcript` or `--estimate`; unlock: pass one or both |
| `AF-ECONOMY-PRICING-MISSING` | `economy cost` found no `ProviderPricing` row for provider/model (at the horizon); unlock: declare an entry in the pricing catalog yaml |
| `AF-GOV-ACTION-INVALID` | `governor gain`/`stop` action outside the §24 names; unlock: pass one of the declared action names |
| `AF-GOV-FAILURE-CLASS-UNKNOWN` | `governor recover` failure class outside the closed §26 vocabulary; unlock: classify into one of the declared classes |
| `AF-GOV-RECOVERY-UNDECLARED` | failure class is valid but absent from the recovery policy; escalates by default |
| `AF-GOV-RECOVERY-EXHAUSTED` | recovery attempts exhausted for the class; the ladder's terminal action fires |
| `AF-GOV-LOOP-DETECTED` | strategy fingerprint repeated inside the declared window; the cycle is blocked |
| `AF-GOV-GAIN-UNRESOLVED` | expected gain is unmeasurable; continuing is not justified — stop |
| `AF-GOV-STOP-LOW-GAIN` | expected gain at or below the threshold; stop, not "budget remains" |
| `AF-GOV-ROUTE-UNKNOWN` | `control eval/promote/demote` target route not declared in `rules/control_plane.yaml`; unlock: declare the route |
| `AF-GOV-MODE-TRANSITION-INVALID` | lifecycle step skipped or already terminal (active→active); unlock: move one stage at a time shadow→assisted→active |
| `AF-GOV-PROMOTION-INCOMPLETE` | §31 requirements unmet; `missing` names each absent requirement |
| `AF-GOV-PROMOTION-NOT-APPROVED` | active promotion without an approved `ApprovalGate` matching `evidence.approval_id` |
| `AF-GOV-FALLBACK-MISSING` | active route degraded and no `fallback_route` declared; the route refuses (fail-closed) |
| `AF-GOV-TRIGGER-INVALID` | `control eval` trigger name outside the §32 vocabulary; unlock: pass one of the five triggers |
| `AF-ROUTE-POLICY-INVALID` | `rules/model_router.yaml` (or `--policy`) schema unexpected; unlock: align `version: 1` |
| `AF-ROUTE-NO-ELIGIBLE-MODEL` | every candidate failed a declared constraint; `ranked[].reasons` names each refusal |
| `AF-ROUTE-PROMOTION-EVIDENCE` | `route promote` without a scorecard reaching min_evaluations + quality_floor; a small synthetic benchmark never promotes |
| `AF-EVALS-ECONOMY-BASELINE-MISSING` | corpus case has no recorded baseline; unlock: `apiforge evals economy --record-baseline` |
| `AF-EVALS-ECONOMY-BASELINE-STALE` | fixture digest differs from the recorded baseline; unlock: re-record and commit the baseline |
| `AF-CONTEXT-QUALITY-CAPSULE` | `context quality --capsule` is missing, unreadable or not a `ContextCapsule/v1` payload; unlock: record it with `context capsule ... > capsule.json` |
| `AF-CONTEXT-QUALITY-GATE` | `context quality --gate` is not `strict\|evidence\|permissive` |

## Cache & delta (`cache stats|invalidate`, `context delta|gc`, `evals cache`)

The cache is advisory (`rules/cache_policies.yaml`): layers `parse`, `graph`,
`impact` and `capsule` are enforced; `knowledge`, `routing` and `validation`
are declared and disabled until a caller exists; `model_response` is disabled.
L4 caches the capsule's evidence *selection*, never the envelope, so output is
byte-identical with `--no-cache`. Entries carry dependency probes (file, line
span or JSON-pointer hashes, graph neighborhood hash, model-definition and
test-mention symbols) plus a TTL; a changed dependency always invalidates,
an expired entry is recomputed (`on_stale: recompute`) or reused with a
warning (`on_stale: warn`). Corrupt entries or tampered objects are misses,
never errors. The shared tier (`APIFORGE_CACHE_HOME` / `--cache-home`) is
opt-in and re-hashed on every read. `context delta` reads git with argument
arrays only (`diff --name-status`, `show`) and never mutates.

| Code | Meaning |
|---|---|
| `AF-CACHE-LAYER-UNKNOWN` | `--layer` is not one of the eight declared layers; unlock: pass a declared layer |
| `AF-CACHE-LAYER-DISABLED` | the layer is declared but disabled (e.g. `model_response`); unlock: use an enabled layer |
| `AF-CACHE-POLICY-INVALID` | `rules/cache_policies.yaml` does not match `apiforge/cache-policies/v1`; unlock: restore the shipped schema |
| `AF-DELTA-INPUT-MISSING` | `context delta`/`cache invalidate` got neither `--base` nor `--changed`; unlock: pass one |
| `AF-DELTA-GIT-UNAVAILABLE` | git cannot run or the root is not a work tree; unlock: pass `--changed <file>` instead |
| `AF-DELTA-REF-INVALID` | `git diff` refused `--base`/`--head`; unlock: pass refs that exist (`git rev-parse <ref>`) |
| `AF-EVALS-INVALID` | an eval corpus is empty, has duplicate ids or a mutation that does not apply; unlock: fix the corpus yaml |

## Verification, retrieval, evidence and providers (`verify plan`, `knowledge search`, `evidence resolve`, `economy doctor`, `economy tier`, `agentops prompt`, `workspace locality`, `evals economy-extras`)

All read-only: `verify plan` names the ladder level and impacted tests but
never runs them; retrieval expands queries from a declared table and ranks
passages with explicit signals; `evidence://` refs resolve one hop at a time;
the doctor only reports; tiers need benchmark evidence before going cheaper;
the prompt prefix contains nothing run-specific.

| Code | Meaning |
|---|---|
| `AF-VERIFY-RISK-INVALID` | `--risk` is not micro, low, medium or high; unlock: use `apiforge sdd classify` |
| `AF-RETRIEVAL-TIER-INVALID` | `--tier` is not 1, 2 or 3 |
| `AF-RETRIEVAL-EXPANSION-INVALID` | `rules/query_expansion.yaml` is malformed |
| `AF-EVIDENCE-REF-INVALID` | ref is not `evidence://<operation, fact, finding or rule>/<id>` |
| `AF-EVIDENCE-NOT-FOUND` | no case, or the node is not in the case graph; unlock: resolve a listed neighbor or run `analyze` |
| `AF-PROVIDER-POLICY-INVALID` | `rules/providers.yaml` is malformed |
| `AF-WORKSPACE-TARGET-UNKNOWN` | `--target` is not a repository of the workspace |
| `AF-ECONOMY-DOCTOR-CACHE-OFF` | doctor: `APIFORGE_CACHE` disables the caches |
| `AF-ECONOMY-DOCTOR-DEEP-DEFAULT` | doctor: default profile is deep |
| `AF-ECONOMY-DOCTOR-NO-CAPSULE` | doctor: repository-scope context used, no capsule ever built |
| `AF-ECONOMY-DOCTOR-VERBOSE-OUTPUT` | doctor: `APIFORGE_OUTPUT` is not compact |
| `AF-ECONOMY-DOCTOR-NO-SHARED-CACHE` | doctor: no shared cache tier configured |
| `AF-ECONOMY-DOCTOR-STALE-KNOWLEDGE` | doctor: packs verified more than 180 days ago |
| `AF-ECONOMY-DOCTOR-TOKENS-UNRESOLVED` | doctor: no run carries observed tokens |
| `AF-ECONOMY-DOCTOR-ESCALATION-HEAVY` | doctor: more than half of the runs escalated to L3 |
| `AF-ECONOMY-DOCTOR-REPEATED-PARSING` | doctor: extractor cache misses exceed hits |

## Economy hardening (trust boundary, budget invariants, accounting, proof semantics)

Every path read from case, fact or graph data goes through one resolver
(`security/source_paths.py`): it must stay inside the project root or a
repository declared in `.apiforge/workspace.yaml` after symlinks are
followed. A refused ref is reported as unresolved and never read nor stored
in `ctx://`; the rest of the capsule or evidence node is served. The Context
Gateway, `evidence resolve` and `context delta` read cases only through
`case.service.load_verified_case` (containment + sha256 per artifact).

| Code | Meaning |
|---|---|
| `AF-PATH-OUTSIDE-ROOT` | a case/fact/graph path or a `context delta --changed` item is empty, UNC, drive-qualified, traverses `..` or resolves outside the allowed roots (unresolved note, never read); an out-of-root `--case-dir`/`--case` refuses the command (`field=case_dir`); unlock: keep sources inside the project or declare the repository in `.apiforge/workspace.yaml` |
| `AF-CASE-HASH-MISMATCH` | a case artifact changed after `case.json` was written; the capsule/evidence/delta is refused; unlock: re-run `apiforge analyze` |
| `AF-CASE-PATH-TRAVERSAL` | a case manifest artifact path escapes the case directory (also refused by `evidence emit`) |
| `AF-ECONOMY-PROOF-UNSTRUCTURED` | diagnostic: an expected proof is only mentioned in a step, not proven by a `ProofReceipt`; the ladder reaches L1 at most (no early stop) |
| `AF-ECONOMY-PROOF-HASH-MISMATCH` | diagnostic: a `ProofReceipt` artifact is missing or its sha256 differs; never L0 |
| `AF-ECONOMY-PROOF-INVALID` | diagnostic: a step `proofs` entry is not a valid `ProofReceipt` or its artifact leaves the allowed roots |
| `AF-DELTA-UNMAPPED-SOURCE` | a changed source, config or contract file maps to no impacted operation; the delta is `degraded`, never `ready` |
| `AF-EVALS-BASELINE-INVALID` | `evals agentic-quality --baseline` is missing, not JSON, not an `apiforge/agentic-quality-eval/v1` report, has no `benchmark_identity`, misses a profile or has an accuracy outside [0, 1]; unlock: regenerate it with `apiforge evals agentic-quality > baseline.json` |
| `AF-EVALS-BASELINE-MISMATCH` | the baseline's `BenchmarkIdentity/v1` (corpus, case ids, profiles, claim scope) differs from the current benchmark; unlock: use a baseline of the same corpus or pass `--allow-cross-corpus-baseline` (recorded as `cross_corpus`) |
| `AF-EVALS-INPUT-INVALID` | `--min-accuracy` is outside [0, 1] |
| `AF-GITHUB-RULESET-INVALID` | `scripts/github_ruleset_plan.py` got input that is not a ruleset JSON (object with `id`, `name` and typed `rules`); unlock: pass the JSON of `gh api repos/<owner>/<repo>/rulesets/<id>` |
| `AF-ECONOMY-TOKEN-RULE-INVALID` | `rules/token_eligibility.yaml` has another schema, an empty prefix list, a blank or a duplicated prefix; coverage is never computed from a broken policy (fail closed); unlock: restore it |
| `AF-ECONOMY-LEDGER-PERSIST` | an auditable ledger row (runtime role bytes) could not be written; the run's economy block and `economy stats` report it as unresolved; unlock: make `.apiforge` writable and re-run |

`BudgetEnvelope.context_bytes` is a global budget: each context class gets a
pool (`share × context_bytes`) split across its instances, and
`RoleContextPlan` refuses totals above the envelope. The ControlPlane counts
every provider call, including shadow challengers (`calls_by_kind`), so
checkpoints and resumes see real spend. `economy stats` reports
`token_coverage` (`complete`, `partial`, `unresolved`); `observed_tokens` is a
number only when coverage is complete. Only token-eligible rows count
(model-facing verbs declared in `rules/token_eligibility.yaml`, or any row
with measured tokens). Persist failures are reported per run
(`persist_failures_for_run`) and for the root (`persist_failures_global`);
a run is unresolved only by its own lost rows. `evals agentic-quality`
passes only when every profile reaches `--min-accuracy` (default 1.0) and
none regresses versus deep or an optional `--baseline` report.
The ladder stops at L0 only on structured, re-hashed `ProofReceipt`s. The
layered cache tries the shared tier when a local entry is stale or corrupt,
and an entry with an invalid timestamp is a corrupt miss. In-process knowledge
caches key on a stat-only generation of the pack files, so an edited pack is
seen without restarting a long-lived host; retrieval normalizes with NFKC +
casefold (PT-BR terms such as `autenticação` match as written).

Reporting keeps outcomes honest: `PhaseBudgetPlan` separates
`quality_status` from `budget_status` (`protected_overrun` is not `ok`), run
results and `summary.json` carry `unresolved.routing`, and an unmapped
runtime file degrades a delta. Evidence classes stay apart:
`evals economy-matrix` is `claim_scope: deterministic-safety-economy`,
`evals agentic-quality` grades recorded specialist verdicts against ground
truth under each profile (`recorded-agentic-outputs`, `--responses-dir` for
real recordings), and provider tokens are observed only with transcripts.
`evals economy-hardening` pins path containment, class pools, token
coverage, phase status and delta degradation.

## Freshness, live gating and resume (`knowledge watch`, `evidence gate`, `verify escalate`, `economy phase-budget`, `runtime checkpoint`, `evals economy-freshness`)

`knowledge watch` compares every pack's declared `freshness.upstream`,
`source_hash`, `source_version`, `expires_at` and `window_days` with a local
upstream manifest written by the separate refresh workflow; only stale packs
are `refresh_needed` and nothing is fetched. `evidence gate` sends static
questions to local artifacts and allows `live_read_only` only for questions
that name a runtime effect (`rules/live_evidence_triggers.yaml`).
`verify escalate` stops once a test is conclusive and escalates to read-only
runtime evidence only after an inconclusive test. `economy phase-budget`
splits the profile envelope across SDD phases; contract, verify and secure
are protected — an overrun is reported, never cut. `runtime run` writes
`economy_checkpoint.json`; `runtime resume` keeps at least its profile and
carries the calls already spent.

| Code | Meaning |
|---|---|
| `AF-KNOW-WATCH-MANIFEST` | the upstream manifest is missing, not JSON or has no `sources` mapping; unlock: record fingerprints with the refresh workflow |
| `AF-KNOW-WATCH-CLOCK` | `--now` is not ISO8601 |
| `AF-EVIDENCE-TRIGGERS-INVALID` | `rules/live_evidence_triggers.yaml` is malformed |
| `AF-EVIDENCE-QUESTION-EMPTY` | `evidence gate` got an empty question |
| `AF-EVIDENCE-MODE-INVALID` | `--mode` is not `static`, `fixture`, `live_read_only` or `live_mutation` |
| `AF-EVIDENCE-MUTATION-REFUSED` | `live_mutation` is never granted to answer a question; unlock: use `live_read_only`; a mutation needs a separate approved change |
| `AF-VERIFY-ESCALATE-INPUT` | a verdict is unknown, both `--test` and `--test-slice` were passed, or the slice is not `TestSlice/v1` |
| `AF-VERIFY-ESCALATE-EXHAUSTED` | unresolved note: test and read-only runtime evidence are both inconclusive; unlock: add a targeted test or a human review |
| `AF-BUDGET-PHASE-POLICY` | `rules/phase_budgets.yaml` is malformed or its shares do not sum to 1.0 |
| `AF-BUDGET-PHASE-USAGE` | `--usage` is not a JSON object of `{phase: {calls, context_bytes}}` |
| `AF-BUDGET-PHASE-UNKNOWN` | usage names a phase outside the SDD chain |
| `AF-BUDGET-PHASE-EXCEEDED` | a non-protected phase used more than its share; plan is unresolved; unlock: raise the profile or narrow the phase |
| `AF-BUDGET-PHASE-PROTECTED` | diagnostic: a protected phase overran its share; reported, never cut |
| `AF-BUDGET-STORE-CORRUPT` | an append-only hierarchical budget row failed its closed contract |
| `AF-BUDGET-PLAN-CONFLICT` | a plan id was reused with a different content hash |
| `AF-BUDGET-PLAN-NOT-FOUND` | a budget check named a plan absent from the local plan journal |
| `AF-BUDGET-TASK-MISMATCH` | spend task or plan identity does not match the loaded budget plan |
| `AF-BUDGET-TOKENS-UNRESOLVED` | token limit enforcement lacks observed token measurements |
| `AF-ECONOMY-CHECKPOINT-INVALID` | `economy_checkpoint.json` is unreadable; unlock: restore the run directory or delete the checkpoint |
| `AF-ECONOMY-CHECKPOINT-NOT-FOUND` | the run has no economy checkpoint |
| `AF-ECONOMY-RESUME-PINNED` | diagnostic: a resume requested a profile below the checkpoint; the checkpoint profile is kept |

## Economy evals (`evals economy-matrix`, `evals gate`, `evals replay`, `economy roi`)

The matrix runs canonical contract changes under the three profiles and keeps
quality, evidence, cost, context and latency on separate axes. An economy
change ships only through `evals gate`: any safety regression rejects,
quality regressions are tolerated only up to `--max-quality-regression`
(default 0), and holdout or mutation regressions reject. `evals replay`
re-plans stored decisions under the current policy without providers.
`ScorecardRoutingPolicy.quality_floor` (opt-in) excludes candidates below the
floor (`quality-below-floor`) and orders champions by observed cost.

| Code | Meaning |
|---|---|
| `AF-EVALS-GATE-INVALID` | a report passed to `evals gate` is not `EconomyMatrix/v1`; unlock: use `evals economy-matrix --out` |
| `AF-EVALS-GATE-MISMATCH` | the two reports cover different case × profile rows; unlock: run both on the same corpus |
| `AF-REPLAY-RUN-INCOMPLETE` | replay reason: a stored run lacks its decision, economy plan or task spec; reported unresolved, never guessed |

## Tool/host economy (`--output`, `slice tests`, `slice log`, `mcp surface`, `agentops projection`, `apiforge-mcp --surface/--host`, `evals tool-economy`)

`--output compact` (or `APIFORGE_OUTPUT=compact`) minifies payloads and drops
only null and empty values; `--output json` (default) is unchanged. Slicers
store the whole log in the ctx CAS and return every failing test or distinct
error signature with spans. `apiforge-mcp --surface compact` publishes six
gateways (`apiforge_discover`, `apiforge_call`, `apiforge_context`,
`apiforge_expand`, `apiforge_analyze`, `apiforge_evidence`); every full tool
stays reachable through `apiforge_call`.

| Code | Meaning |
|---|---|
| `AF-OUTPUT-MODE-INVALID` | `--output`/`APIFORGE_OUTPUT` is not `json` or `compact` |
| `AF-SLICE-INPUT-NOT-FOUND` | the log passed to `slice tests`/`slice log` does not exist |
| `AF-SLICE-INPUT-INVALID` | the log is over 25 MB, not valid JUnit XML, or `--format` is unknown |
| `AF-SLICE-XML-REFUSED` | JUnit XML declares a DOCTYPE; entities are never expanded; unlock: export without a DOCTYPE |
| `AF-MCP-TOOL-UNKNOWN` | `apiforge_call` got a tool name that is not registered; unlock: use `apiforge_discover` |
| `AF-MCP-TOOL-ARGS` | `apiforge_call` arguments do not bind to the tool signature |
| `AF-MCP-SURFACE-INVALID` | surface is not `full` or `compact` |
| `AF-HOST-UNKNOWN` | host not declared in `rules/host_projections.yaml` |
| `AF-HOST-PROJECTION-INVALID` | `rules/host_projections.yaml` is malformed |

## Selective agentics (`knowledge select`, `debate packet`, `agents audit`, `evals selective-agentics`)

`knowledge select` loads only packs named by `rules/expertise_triggers.yaml`
(intent keywords, observed frameworks, capability); no trigger selects no
pack. Economy runs build one capsule for the TaskSpec `target=` and give each
role a subset (`rules/role_context.yaml`): specialists `focused`, reviewers
`evidence_plus_delta`, critics `decision_plus_evidence`, referees
`disagreements_only`, each capped at `share × envelope.context_bytes`.
Requests carry `context_class`, `context_refs` and `expertise`;
`role-context.json` and ledger rows `runtime role:<kind>` record the bytes.
Challengers run in a bounded shadow (`envelope.shadow_share`, deterministic
sampling by run id, only from calls left after the verification reserve) and
never enter artifacts, gaps or status. `agents audit` is report-only.

| Code | Meaning |
|---|---|
| `AF-EXPERTISE-TRIGGERS-INVALID` | `rules/expertise_triggers.yaml` is malformed or names a pack that does not exist; unlock: restore it or name existing packs |
| `AF-ROLE-CONTEXT-POLICY` | `rules/role_context.yaml` does not map every role kind to a declared class, shares exceed 1.0 or a `policies:` row fails `RoleContextPolicy/v1` validation |
| `AF-ROLE-CONTEXT-BUDGET` | unresolved note: a role's refs exceeded its share of `context_bytes` and were trimmed (listed in `trimmed`); unlock: raise the profile |
| `AF-ROLE-CONTEXT-DENIED` | unresolved note: a v2 policy `denied_kinds` removed a ref the class would otherwise allow; unlock: grant the kind or route the evidence through an allowed kind |
| `AF-ROLE-CONTEXT-TRUST` | unresolved note: a ref's provenance `origin` is below the role's `minimum_origin_rank`; unlock: attest the ref from a higher-trust origin |
| `AF-ROLE-CONTEXT-REQUIRED` | unresolved note: a `required_kinds` ref existed in the capsule but did not fit the role budget; unlock: widen the budget or drop other kinds |
| `AF-ROLE-CONTEXT-TOOL` | a v2 policy `tool_visibility` allowlist does not name the requested tool; unlock: add the tool to the role's allowlist |
| `AF-ECONOMY-SHADOW-BUDGET` | shadow reason: the run was sampled but no call remained after the verification reserve |
| `AF-DEBATE-DELTA-INVALID` | `--disagree` is not `point=reason`, a point is empty or `--confidence` is outside [0, 1] |
| `AF-AGENTS-AUDIT-INVALID` | the agents directory is missing or an agent frontmatter is not valid YAML |

## Economic routing (`runtime run|resume|debate --profile`, `sdd classify`, `evals economy-routing`)

Profiles `economy`/`balanced`/`deep` (`rules/economy_profiles.yaml`) resolve
`--profile` > `.apiforge/project.yaml` `economy_profile` > policy default
`balanced`. Risk sets a floor the effective profile can never go below; trims
touch only parallel slots, fallbacks and challengers. The supervisor caps
calls at `min(policy, TaskSpec, envelope)`, holds a verification reserve,
stops at L0 on deterministic proof and escalates L2→L5 only on deterministic
triggers. Partial outcomes keep `final_status: REVIEW` and report
`economy.status: unresolved`.

| Code | Meaning |
|---|---|
| `AF-ECONOMY-PROFILE-INVALID` | `--profile` is not `economy`, `balanced` or `deep`; unlock: pass a valid profile |
| `AF-ECONOMY-ESCALATED` | diagnostic: risk raised the effective profile above the requested one (never a refusal) |
| `AF-ECONOMY-CEILING` | an escalation (L3 review or L4 debate) exceeded the profile's ladder ceiling at non-forced risk; run stays unresolved; unlock: rerun with a higher profile |
| `AF-ECONOMY-ROLE-INVARIANT` | an economy trim would have changed a risk-required reviewer/critic/referee; the run refuses instead of proceeding |
| `AF-ECONOMY-ESCALATION-NOT-USED` | control step note: the reserved escalation reviewer was not needed |
| `AF-BUDGET-EXHAUSTED` | planned invocations exceeded the economy call budget; no silent downgrade; unlock: `--profile balanced\|deep` or raise TaskSpec budgets |
| `AF-SDD-PROFILE-BELOW-RISK` | a feature's `intent.md` carries `risk_class` and declares an SDD profile below its minimum; unlock: declare the required profile or higher |
| `AF-SDD-RISK-UNRESOLVED` | `sdd classify` found no classifying signal (defaults to `medium`) or got only one of `--baseline`/`--candidate` |

## Field validation (`field record|annotate|verify|report|export`, `workspace graph --infer`)

Field records join existing run artifacts (economy ledger, `summary.json`,
`economy_checkpoint.json`); a missing source leaves the value `null` with an
`unresolved` reason. Inference is opt-in and audited: `workspace graph --infer
--run-id <id>` appends a `workspace.infer` ledger row, which `field record
--phase baseline` treats as contamination.

| Code | Meaning |
|---|---|
| `AF-FIELD-CORPUS-INVALID` | `docs/field/corpus.yaml` or `hypothesis.md` missing, malformed, duplicate task id, unknown repo ref, or own repo ref not `sha256:` |
| `AF-FIELD-TASK-UNREGISTERED` | task id is not pre-registered in the corpus |
| `AF-FIELD-LATE-REGISTRATION` | task `registered_at` is after the cycle start |
| `AF-FIELD-ENUM` | `exit_reason`, `phase`, `verdict` or a count is outside its closed set |
| `AF-FIELD-TIME-ORDER` | `--ended` precedes `--started`, a timestamp is not RFC3339, or a linked run checkpoint lies outside the task window (±60s) |
| `AF-FIELD-RUN-MISSING` | no field record for task/phase, or a run id has neither run directory nor ledger rows |
| `AF-FIELD-FLAG-CONTAMINATION` | a baseline task's linked runs used `workspace.infer` |
| `AF-FIELD-EXPORT-LEAK` | export would expose a private repo name/path or an absolute path |
| `AF-FIELD-CYCLE-MUTATED` | the sealed cycle changed: corpus, hypothesis, gate, tasks, repos or `cycle_started_at` differ from `docs/field/cycle.lock.json`, the lock is missing after the cycle started, or a lock exists without `cycle_started_at`; `field=cycle.<component>` |
| `AF-FIELD-CYCLE-EXPIRED` | `field record` on an expired cycle (`max_runs` or `max_weeks` reached without coverage), or a new baseline record beyond `max_runs` |
| `AF-FIELD-VERIFIER-NOT-INDEPENDENT` | `field verify` by the same actor that executed the task |
| `AF-FIELD-ACTOR-INVALID` | `--executor`/`--verifier` is not `agent:<name>` or `human:sha256:<64 hex>` |
| `AF-WORKSPACE-INFER-AMBIGUOUS` | unresolved: an outbound call matches routes in more than one repository; edges capped at 0.45 |
| `AF-WORKSPACE-INFER-UNATTRIBUTED` | unresolved: `--infer` ran without `--run-id`, so field records cannot see it |
| `AF-WORKSPACE-INFER-EXTRACT` | unresolved: a route extractor failed on one repository |

## Agent roster (`agents sync|check|lint|references|audit`, `evals agent-routing`)

`agents/*.md` is the only hand-edited agent source. `agents sync` renders
`.claude/agents/*.md` (Claude Code: `tools` from `access`, `model` from
`model_tier`), `.agents/agents/*.md` (Devin: name/description) and
`.codex/agents/*.toml` (Codex: `sandbox_mode`, `model_reasoning_effort`,
`developer_instructions`). `access` is `read-only` (host read tools; Codex
`read-only`), `state-writer` (writes only through `apiforge` commands into its
`write_scope`; no Claude Edit/Write; Codex `workspace-write`) or `writer`
(Edit/Write within `write_scope`). Sources without `access` are legacy and mirror
verbatim. Files in a mirror directory that are not generated agents are
reported as `(non-agent file)` and never deleted.

| Code | Meaning |
|---|---|
| `AF-AGENT-CONTRACT-FRONTMATTER` | missing/invalid frontmatter or field value |
| `AF-AGENT-CONTRACT-NAME` | `name` differs from the file stem |
| `AF-AGENT-CONTRACT-DESCRIPTION` | empty, over 300 chars, or missing `Use when` / `Not for` |
| `AF-AGENT-CONTRACT-ACCESS` | `access` not declared, or a writer/state-writer without `write_scope` |
| `AF-AGENT-CONTRACT-SECTIONS` | a required `## <section>` is missing |
| `AF-AGENT-CONTRACT-WORDS` | body outside 250–600 words |
| `AF-AGENT-CONTRACT-LANGUAGE` | description/body not in English |
| `AF-AGENT-CONTRACT-TOOLS` | no owned `apiforge_tools` |
| `AF-AGENT-CONTRACT-TOOL-OWNER` | an `apiforge` command is owned by more than one agent |
| `AF-AGENT-CONTRACT-UNKNOWN-TOOL` | an `apiforge_tools` entry is not a command of the `apiforge` CLI |
| `AF-AGENT-CONTRACT-PLAYBOOK` | missing playbook, playbook executor not declared in frontmatter, or playbook verb not an `apiforge` command |
| `AF-AGENT-ALIAS-DEPRECATED` | warning: a deprecated agent name was resolved to its roster successor |
| `AF-AGENT-ALIAS-INVALID` | alias table malformed, chained or self-referencing |
| `AF-EVAL-AGENT-ROUTING` | routing golden corpus missing |

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

### Agentic runtime

The local runtime is provider-neutral and executes only against a sealed TaskSpec. It persists invocations, artifacts, events and replay material; model output cannot widen scope, approve mutations or bypass verification.

| Code | Meaning |
|---|---|
| `AF-RUNTIME-ADAPTER` | adapter failed or returned an adapter-level error |
| `AF-RUNTIME-POLICY` | requested runtime policy is missing or malformed |
| `AF-RUNTIME-MUTATION` | external mutation is refused by the local safety policy |
| `AF-RUNTIME-TOOL` | tool name is not allowlisted for the runtime |
| `AF-RUNTIME-REGISTRY` | capability registry is missing or malformed |
| `AF-RUNTIME-TASK-STATE` | TaskSpec is not sealed, ready or running |
| `AF-RUNTIME-TASK-OUTCOME` | TaskSpec outcome is empty |
| `AF-RUNTIME-TASK-PROOF` | TaskSpec has no expected proofs |
| `AF-RUNTIME-TASK-ACCEPTANCE` | TaskSpec has no acceptance criteria |
| `AF-RUNTIME-TASK-ROLLBACK` | TaskSpec has no rollback statement |
| `AF-RUNTIME-TASK-INPUT` | declared runtime input is missing |
| `AF-RUNTIME-TASK-PATHS` | mutating task has no declared writable paths |
| `AF-RUNTIME-BUDGET` | parallel execution bound is invalid |
| `AF-RUNTIME-DEPENDENCY` | invocation dependency graph is cyclic or incomplete |
| `AF-RUNTIME-TIMEOUT` | invocation exceeded its bounded timeout |
| `AF-RUNTIME-SCHEMA` | adapter output is not a structured object |
| `AF-RUNTIME-HASH` | runtime artifact hash could not be computed |
| `AF-RUNTIME-NOT-FOUND` | requested runtime run is not persisted |
| `AF-RUNTIME-ROUTING` | persisted routing decision is malformed; field=runtime.routing; unlock=regenerate the trace from the versioned routing contracts |
| `AF-RUNTIME-PROFILES` | agent profile registry is missing or malformed; field=runtime.profiles_file; unlock=provide the versioned local profile registry |
| `AF-RUNTIME-COMPATIBILITY` | legacy runtime payload lacks a proven compatible state; field=runtime.run; unlock=record a versioned migration and independent proof |
| `AF-RUNTIME-DEPENDENCY-FAILED` | invocation dependency failed; field=invocation.dependencies; unlock=resolve the prerequisite failure and resume |
| `AF-RUNTIME-EVAL-GATE` | mandatory golden/holdout/mutation evidence is missing or failed; field=runtime.eval_gate; unlock=run the missing cases and preserve their evidence |
| `AF-CAPABILITY-ELIGIBILITY` | no capability satisfies state, profile, risk, prerequisite and evidence requirements; field=capability; unlock=provide the missing evidence/prerequisite or choose a supported capability |
| `AF-SCORECARD-INVALID` | persisted agent scorecard is malformed; field=scorecard; unlock=regenerate it from validated eval results |
| `AF-CONTROL-RUN-NOT-FOUND` | control run is not persisted; field=run_id; unlock=provide an existing local control run |
| `AF-CONTROL-STEPS` | control run has no steps; field=steps; unlock=declare at least one bounded step |
| `AF-CONTROL-DEPENDENCY` | control step dependency is missing from the declared DAG; field=steps.dependencies; unlock=declare the prerequisite or remove the edge |
| `AF-CONTROL-TERMINAL` | transition targets a terminal control run; field=run.status; unlock=resume only a non-terminal run |
| `AF-CONTROL-BUDGET` | control run call budget is exhausted; field=max_calls; unlock=increase the declared policy budget or split the TaskSpec |
| `AF-CONTROL-STEP-NOT-FOUND` | control step is not persisted; field=step_id; unlock=use a step from the control run |
| `AF-CONTROL-NOT-READY` | step prerequisites are not complete; field=step_id; unlock=complete dependencies before claiming the step |
| `AF-CONTROL-LEASE` | lease owner or lease boundary is invalid; field=lease; unlock=claim with a valid worker and lease or recover expiry |
| `AF-CONTROL-LEASE-EXPIRED` | persisted worker lease expired and work was returned to the queue; field=step.lease_until; unlock=claim the recovered step with a new lease |
| `AF-CONTROL-STEP-STATE` | step transition is invalid for its current state; field=step.status; unlock=follow the persisted state machine |
| `AF-CONTROL-REVIEW-STATE` | review was requested before all required steps reached review; field=run.status; unlock=complete or recover the run first |
| `AF-CONTROL-IDEMPOTENCY-CONFLICT` | same idempotency key has a different result hash; field=step.idempotency_key; unlock=preserve both receipts and reconcile manually |
| `AF-BRIEF` | outcome brief rendering failed |
| `AF-RECIPE-INVALID` | `recipes.yaml` is malformed |

### Graph (`graph`)

`graph build` reads a case directory into `nodes.jsonl`/`edges.jsonl` —
canonical lines sorted by id, each node line carrying a `sha256` over its
`{id,kind,props}` payload so a tampered line is detected on load. Queries
are closed-vocabulary (`--kind`, `--edge`, `--prop k=v`); `impact` traverses
in reverse, `trace` returns the shortest directed path or names the pair
unreachable, `coverage` names unverified findings / unimplemented
operations / unreferenced facts. `export` copies canonical bytes plus a
digest manifest; `--format neptune` writes Neptune Gremlin-load CSV
(`vertices.csv`, `edges.csv`, every property `:String`) and `--format rdf`
writes RDF 1.1 N-Triples (`graph.nt`); both are re-validated before
`export.json` lists their digests.

| Code | Meaning |
|---|---|
| `AF-GRAPH-NOT-FOUND` | no `nodes.jsonl` under the graph directory |
| `AF-GRAPH-NO-CASE` | `graph build` found no `case.json` under `--case` |
| `AF-GRAPH-INVALID` | a node/edge line fails the contract schema |
| `AF-GRAPH-HASH-MISMATCH` | a node line's `sha256` diverges from its payload |
| `AF-GRAPH-KIND` | query names an unknown node or edge kind |
| `AF-GRAPH-NODE` | `impact`/`trace` name a node absent from the graph |
| `AF-GRAPH-INPUT` | a source artifact is unreadable or malformed |
| `AF-GRAPH-FORMAT` | export format outside `jsonl`, `neptune`, `rdf` |
| `AF-GRAPH-EXPORT-INVALID` | a projection failed its loader-grammar validation; nothing is listed in `export.json` |

### Index (`index`)

`index build` writes 12 canonical JSONL kinds under `.apiforge/index/` —
`files`, `symbols`, `routes`, `facts` from the extractor, plus eight kinds
derived from existing facts only (never new parsers): `schemas`
(`contract.*`), `dependencies` (`data.*`), `calls` (`resilience.http_call`),
`tests` (`test.*`), `iac` (`infra.*`), `databases` (`data_access_ir`),
`findings` (`--findings <case>/findings.json`), `decisions` (the autonomy
ledger). `index.json` manifests all 12 with counts — empty kinds are
emitted empty, never skipped.
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
| `AF-INDEX-DECISIONS-CORRUPT` | the autonomy ledger line feeding `decisions.jsonl` is malformed |

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

`model elasticache-access --path <dir>` reuses the identical scan —
ElastiCache speaks the Redis protocol — and rewrites the inventory
`framework` to `elasticache`; the `DataAccessIR` provider/database fields
carry the declared provider. The provider is named by the operator's verb
choice, never inferred from the code.

`model mongo`, `model dynamodb-access` and `model neptune-access` apply the
same contract to MongoDB/DocumentDB (pymongo/motor + Java/Go driver names),
DynamoDB (boto3 `Table`/`client` ops) and Neptune (gremlin/SPARQL/openCypher
strings). Composite postures — `full_scan`, `unfiltered_write`, `unbounded`
— are computed only from declared arguments, and the AF-DATA-009..013 rules
judge them.

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
| `AF-OTEL-SENSITIVE-ATTRIBUTE` | local agent span contains a secret-like attribute key |
| `AF-OTEL-STORE-CORRUPT` | local agent span row failed its closed contract |
| `AF-OTEL-SPAN-CONFLICT` | a span id was reused with a different content hash |
| `AF-OTEL-TRACEPARENT-INVALID` | §51 traceparent is not `00-<32hex>-<16hex>-<flags>`; unlock: pass valid W3C ids |
| `AF-OTEL-EXPORT-INVALID` | OTLP payload failed the deterministic structural acceptance; `problems[]` names each defect |
| `AF-OTEL-COLLECTOR-REFUSED` | §52 collector answered a non-2xx or rejected the payload; unlock: fix payload/endpoint and retry |
| `AF-OTEL-COLLECTOR-TIMEOUT` | span ids did not reach the collector output file within the declared timeout |
| `AF-OTEL-COLLECTOR-UNRESOLVED` | collector endpoint unreachable — acceptance stays unresolved, never claimed |
| `AF-AGENTOPS-WASTE-POLICY` | `agentops waste` policy file unreadable or `detectors` mapping missing; unlock: restore `rules/agentops_waste.yaml` or pass `--policy` |
| `AF-MCP-SURFACE-POLICY` | `mcp audit` policy file unreadable, `thresholds` mapping missing or `accepted` rows malformed; unlock: restore `rules/tool_surface.yaml` or pass `--policy` |
| `AF-MCP-DISCLOSURE-POLICY` | `mcp disclose` policy file unreadable or `task_classes` mapping missing; unlock: restore `rules/tool_disclosure.yaml` |
| `AF-MCP-BENCHMARK-POLICY` | `mcp benchmark` policy file unreadable or `samples` mapping missing; unlock: restore `rules/tool_benchmark.yaml` |
| `AF-FORGE-POLICY` | `forge_protocol.yaml` unreadable or `engine`/`protocol_version`/`risk_gate`/`engines` missing; unlock: restore the rules file |
| `AF-FORGE-TASK-ID` | forge task id does not match `^[a-z0-9][a-z0-9-]{1,62}$` |
| `AF-FORGE-TASK-EXISTS` | `forge submit` on an existing task id |
| `AF-FORGE-TASK-NOT-FOUND` | `forge inspect|result|evidence|attach|handoff` on an unknown task id |
| `AF-FORGE-CAPABILITY-UNKNOWN` | `forge submit` names a capability_id absent from the public matrix |
| `AF-FORGE-RISK-GATE` | gated risk class submitted without `--acknowledge-risk` |
| `AF-FORGE-STATE` | `forge attach` on a task already completed/failed/refused |
| `AF-FORGE-ENGINE-UNKNOWN` | `forge handoff --to` an engine not declared in `rules/forge_protocol.yaml` |
| `AF-FORGE-HANDOFF-EXISTS` | `forge handoff` re-run for the same task+engine pair |
| `AF-FORGE-HANDOFF-NOT-FOUND` | handoff lookup on an unknown id |
| `AF-FORGE-STORE` | persisted forge row fails contract validation or is unreadable |
| `AF-PERF-RUN-INVALID` | compare input is not a PerformanceRun payload |
| `AF-PERF-MEMORY-CORRUPT` | a `runs.jsonl` line is malformed — the store refuses, never skips |
| `AF-PERF-SUGGEST-INPUT` | `perf suggest` got neither a readable case dir nor a findings file |
| `AF-SCENARIO-TOOL` | `perf scenario` asked for a generator outside k6/jmeter/locust |
| `AF-SCENARIO-SCHEMA` | scenario JSON is not an object or has no usable `endpoints` |

`perf memory add` appends a validated `PerformanceRun` to the append-only
`.apiforge/perf/runs.jsonl` (payload hash recorded; `recorded_at` is an
explicit argument, never a hidden clock read). `perf memory search` filters
by declared `subject`/`tool`/`since` and returns zero matches when nothing
declared matches — fields are never inferred. `perf suggest` composes
confirmed findings with the catalog's `remediation` text into an
`ActionPlan` carrying a `proposed_diff` as data; the module has no write
path — suggesting never mutates the repository. `--repeat-baseline <dir>`
on `compare`/`verdict` measures the noise floor across repeated runs of the
same subject (`(max-min)/mean`, needs ≥2 runs — fewer leaves the floor
`None` and the verdict names it unproven); a delta inside the measured
floor is suppressed rather than reported as a regression.

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

The v1 vocabulary (`observe`/`recommend`/`sandbox`/`approved`/`continuous`)
is reconciled by `V1_MODE_MAP` — `recommend`→`observe`,
`sandbox`/`approved`→`supervised` — because those v1 "modes" are class
behaviors the policy engine already expresses. `autonomy set recommend`
resolves through the map and ledgers the requested name (ADR-010).

`autonomy heal` walks the named self-healing pipeline
`detect→explain→propose→authorize→execute→verify→compare→accept|rollback`. Every stage appends a
`heal.stage` ledger entry; `authorize` puts the plan's declared class
through `decide()` and a `deny`/`gate` halts with missing requirements
named; `execute` only runs dispatchable verbs; rollback restores the
pre-execute snapshot of every `--writable-path` file and re-hashes it.

| Code | Meaning |
|---|---|
| `AF-AUTONOMY-MODE-UNKNOWN` | mode string not in observe/supervised/continuous |
| `AF-AUTONOMY-MODE-CORRUPT` | `mode.json` unreadable or fails schema |
| `AF-AUTONOMY-SET-REFUSED` | policy refused the mode change; missing requirements named |
| `AF-AUTONOMY-RUNBOOK-UNKNOWN` | no runbook with that name |
| `AF-AUTONOMY-RUNBOOK-SCHEMA` | runbooks.yaml malformed |
| `AF-AUTONOMY-DETAIL` | `--detail` pair is not `key=value` |
| `AF-HEAL-NO-FINDINGS` | `autonomy heal` without `--findings` — detect has no signal |
| `AF-HEAL-FINDINGS-INVALID` | the findings file is unreadable or fails schema |
| `AF-HEAL-ROLLBACK-CONFLICT` | current target bytes differ from the recorded post-state; field=writable_path; unlock=reconcile the concurrent change and rerun with a new snapshot |
| `AF-HEAL-ROLLBACK-VERSION-UNKNOWN` | pre/post rollback evidence is incomplete; field=heal.snapshot; unlock=record both states before attempting rollback |

### Knowledge packs (`knowledge`)

`knowledge/<domain>/` holds data packs: `pack.yaml` (identity, rule areas,
the catalog rules it backs), `source_authority.yaml` (every normative claim
cited with authority class and verification date — sources are cited, never
copied), optional `matrix.yaml` (runtime version guard) and `evals.yaml`
(declared adversarial probes — the project never calls a model, so evals
are data for external runners). Every eval declares a `type` from the
closed 11-value vocabulary (`unit`, `golden`, `integration`,
`adversarial`, `holdout`, `regression`, `economy`, `security`,
`compatibility`, `performance`, `end-to-end`). `knowledge check` validates
the schema and
cross-checks every `rule_id` against the catalog; the release gate runs it.

| Code | Meaning |
|---|---|
| `AF-KNOW-ROOT` | `--root` is not a knowledge directory |
| `AF-KNOW-SCHEMA` | a pack file is missing, malformed or lacks a required field |
| `AF-KNOW-DOMAIN` | `pack.yaml` domain does not match the directory name |
| `AF-KNOW-NO-AUTHORITY` | `source_authority.yaml` missing or lists no sources |
| `AF-KNOW-AUTHORITY` | source authority class outside the closed set |
| `AF-KNOW-EVAL` | eval `expect.kind` outside rule/fact-kind/refusal |
| `AF-KNOW-EVAL-TYPE` | eval `type` outside the closed 11-value vocabulary |
| `AF-KNOW-CHECK` | `knowledge check` found cross-catalog problems (exit 4) |

### Resilience (`model resilience`, `perf chaos`)

`model resilience --path <project>` is a regex-based static scan of
`.py`/`.java`/`.go` sources for the statically checkable resilience
signals: `resilience.http_call` (with `has_timeout`), `resilience.retry`
(`has_backoff`, `has_jitter`, `mutating_target`), `resilience.pool`
(`bounded`), and one `resilience.summary` fact per project carrying the
declared booleans plus computed `*_gap` measures — a gap counts only when
`dependency_surface` exists, so a file with no dependency calls never
reads as "missing a circuit breaker". Pattern matches are heuristic: every
fact carries `heuristic: pattern-match` and the inventory carries the
`AF-RES-HEURISTIC` diagnostic naming the blind spot. The catalog family
`AF-PERF-101..008` (area PERF) judges these facts.

`perf chaos` lists the declared controlled failure-injection scenarios
(`CHAOS-001..013`): each names the fault to inject, the expected signal,
the blast-radius guard and the evidence a run must produce. Injection is
never executed by API Forge — the data is for the environment's own chaos
tooling.

| Code | Meaning |
|---|---|
| `AF-RES-HEURISTIC` | diagnostic: resilience signals are pattern-matched; absence of a match is a blind spot, not proof of absence |
# Observability control-plane codes

The observability control plane uses `TelemetryRecord/v1`, `ObservationSnapshot/v1`, `SLODefinition/v1`, `SignalSummary/v1`, `SLOResult/v1`, `Capability/v1`, `VendorIntent/v1`, `IntentDiff/v1`, `OperationReceipt/v1` and `ObservabilityFinding/v1`. Datadog and Dynatrace mutations require a credential broker and approval; the default path is local, CI-safe and read-only.

# gRPC control-plane codes

The gRPC control plane uses `GrpcIR/v1`, `GrpcCompatibilityReport/v1`, `GrpcCodegenResult/v1`, `GrpcGatewayProjection/v1`, `GrpcRuntimePolicy/v1`, `GrpcPerformanceReport/v1`, `GrpcSecurityReport/v1`, `GrpcPlan/v1` and `GrpcVerification/v1`. `protoc`, Buf, Envoy and descriptor runtime integrations are capability-gated; absent toolchains produce explicit `unsupported` or `REVIEW`, never inferred success. External mutation remains approval-and-broker gated.
