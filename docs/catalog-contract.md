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
