# API Forge

Deterministic, offline, local-first agentic API engineering. API Forge covers
discovery, construction, evolution, migration, contracts, gRPC, testing,
performance, TPS validation, observability, data access and governed agentic
execution. Given an existing project or contract, it produces provenance-backed
IR, evidence, plans, verifiable tasks and bounded decisions instead of guesses.

> Resultado correto, verificável e reproduzível por token consumido.

## Install

```bash
python -m pip install -e '.[dev]'   # Python >=3.12,<3.13
```

The repository also carries the native Caveman/Cavekit assets under `vendor/`,
with pinned provenance and a SHA-256 manifest. RTK project filters live under
`.rtk/`; the optional RTK binary is not silently installed by API Forge.

```bash
python scripts/vendor_caveman.py --check
apiforge agentops native
```

## Agentic platform

The deterministic supervisor turns intent into sealed `TaskSpec` work, runs
independent tasks in a sandbox, preserves full artifacts, invokes verification
and refuses `DONE` when evidence is missing. Debate is triggered by risk,
divergence, missing proof or explicit human request. The main building blocks
are:

- `task`, `runtime`, `sandbox`, `verification`, `brief` and `evals`;
- native provenance graph and measured context/token accounting;
- contract intelligence for OpenAPI and gRPC;
- offline Digital Twin scenarios for validation, auth, timeout, 5xx, rate limit,
  idempotent retry and contract mismatch;
- declarative performance plans for load, stress, spike, soak and capacity;
- OTel-first health correlation with SLO, error budget and performance signals;
- read-only plans for OTel, Datadog, Dynatrace and CloudWatch.

## Host support

The Python core and CLI are shared across Claude Code, GPT/Codex, Devin and
Copilot. Repository mirrors expose the same skills and agents where each host
supports them. Host hooks, MCP lifecycle, slash commands and subagent APIs are
host-specific and are not falsely reported as identical.

```bash
apiforge agentops parity
apiforge agentops activation-plan --host claude
apiforge agentops activation-plan --host gpt-codex
apiforge agentops activation-plan --host devin
apiforge agentops activation-plan --host copilot
```

Activation plans are `plan_only` and approval-gated; they do not alter user
configuration. See [docs/HOST_PARITY.md](docs/HOST_PARITY.md).

## Contract, performance and observability examples

```bash
apiforge contract-intel impact \
  --protocol openapi \
  --baseline tests/fixtures/openapi/orders-v1.yaml \
  --candidate tests/fixtures/openapi/orders-v2-breaking.yaml

apiforge contract-intel twin \
  --protocol openapi \
  --contract tests/fixtures/openapi/orders-v1.yaml \
  --scenario dependency-timeout

apiforge perf plan \
  --subject orders --endpoint 'POST /orders' --target-tps 100

apiforge observability health \
  --source telemetry.json --service orders

apiforge observability read-plan \
  --provider dynatrace --service orders \
  --start 2026-09-22T00:00:00Z --end 2026-09-22T01:00:00Z
```

These commands are offline by default. Real provider reads, credentials,
load-generator execution and external mutations remain explicit adapters and
policy-gated phases.

## Analyze

```bash
apiforge analyze \
  --contract tests/fixtures/openapi/orders-v1.yaml \
  --project tests/fixtures/fastapi_orders \
  --out-dir .apiforge/case
```

Prints a compact JSON summary and writes a case directory:

| Artifact | Meaning |
|---|---|
| `api-ir.json` | Canonical API-IR: operations keyed by method+path, contract and code projections, provenance, input hashes, diagnostics |
| `facts.json` | Immutable evidence facts (code routes, contract operations) with source path/line/sha256 |
| `findings.json` | Rule verdicts — `confirmed` or `unresolved`, always evidence-backed |
| `changes.json` | Contract diff results — only when `--baseline` is given |
| `case.json` | Manifest written last; sha256 of every declared artifact |

Individual stages: `apiforge discover --project .`, `apiforge model build
--contract c.yaml --project .`, `apiforge diff contract --baseline a.yaml
--candidate b.yaml`, `apiforge judge --contract c.yaml --project .`.

Frameworks: `analyze --framework fastapi|spring|go|auto` — `auto` counts
`.java`/`.py`/`.go` files (none → `AF-INPUT-FRAMEWORK-UNKNOWN`). The Spring adapter
parses `*.java` with tree-sitter (`@RestController`/`@RequestMapping`/
`@GetMapping`…, `RouterFunctions.route`, JAX-RS); non-literal annotation args
emit `AF-SPRING-UNRESOLVED-ROUTE`, never inference. The Go adapter covers
chi (`Route` scopes, verb calls), `net/http` (`Handle`/`HandleFunc` with Go
1.22 `"METHOD /path"` patterns) and gin/echo verb calls; `Mount`, middleware
and non-literal paths emit `AF-GO-UNRESOLVED-ROUTE`. Every JSON command accepts
`--detail-level summary|normal|full`; `summary` drops verbose text fields
while refusal codes and `fact_id`s survive.

## Governance

| Command | Purpose |
|---|---|
| `apiforge policy check --verb fs.delete --class destructive` | Evaluate an action against the policy catalog (allow/gate/deny) |
| `apiforge sdd check --root docs/sdd [--strict]` | Validate phase frontmatter, upstream hash cascade and evidence gates |
| `apiforge sdd status --root docs/sdd` | Per-feature phase status summary |
| `apiforge sdd stamp --artifact f/plan.md --upstream f/contract.md` | Write the upstream sha256 into frontmatter (line surgery only) |
| `apiforge sdd set-phase --root R --feature F --phase P --status S [--strict]` | Transition a phase; gates need evidence or a recorded override |
| `apiforge sandbox apply --root . --diff change.diff` | Apply a diff to copied before/after trees and report the finding delta |
| `apiforge sandbox clean --root .` | Remove `.apiforge/sandbox` only |
| `apiforge evidence emit --case .apiforge/case --out receipt.json` | Receipt binding artifact paths to sha256 (proves correspondence, not authorship) |
| `apiforge evidence verify --receipt receipt.json` | Re-hash every artifact the receipt lists |
| `apiforge next-step --findings findings.json --phase verify` | Route the dominant finding area to the specialist agent |
| `apiforge rules list [--area SECURITY]` | List catalog rules — the knowledge base every finding cites |
| `apiforge rules lookup AF-SEC-001` | Print one rule's rationale/remediation/reference |
| `apiforge collect api-gateway --api-id X --out dump/` | Fetch API Gateway config into an offline dump (needs `pip install apiforge[aws]`; the only family that touches AWS) |
| `apiforge model api-gateway --path dump/` | Read the dump into facts — offline, no credentials |
| `apiforge build endpoint --contract c.yaml --operation-id X --project .` | Synthesize a Spring skeleton, prove it in the sandbox (main tree untouched) |
| `apiforge build endpoint ... --into-worktree NAME --approve` | Promote generated files into a policy-gated git worktree |
| `apiforge playbook api-governance-reviewer` | Render the coordinator's executor decomposition — works without dispatch |
| `apiforge economy report [--root .]` | Measured call sizes; `detail_level_effect` shows what `summary` saves |
| `apiforge context funnel --case .apiforge/case` | Measured bytes per case stage (api-ir → facts → findings → summary) |
| `apiforge-mcp` | MCP server for the read/compose verbs (needs `pip install apiforge[mcp]`; every tool takes `detail_level`) |
| `apiforge collect lambda --function-name X --out dump/` | Fetch Lambda config into a dump (Code.Location never persisted) |
| `apiforge collect sqs\|sns\|eventbridge\|iam-role\|cognito\|waf ... --out dump/` | Messaging/identity collectors — same offline-dump contract |
| `apiforge collect dynamodb\|docdb\|neptune\|stepfunctions\|cloudwatch\|xray\|kms\|secrets\|vpc-endpoints\|s3 ... --out dump/` | Datastore/ops collectors — secrets reads metadata only, S3 posture only (objects never listed), unset S3 config recorded as measured absence |
| `apiforge collect alb\|ecs\|eks\|ec2\|msk\|elasticache ... --out dump/` | Compute/LB collectors — describe-only posture (never user-data, console output or broker payloads) |
| `apiforge model sqs\|sns\|eventbridge\|iam-role\|cognito\|waf --path dump/` | Dump → `aws.<svc>.*` facts; boolean measures record declared absence |
| `apiforge model dynamodb\|docdb\|neptune\|stepfunctions\|cloudwatch\|xray\|kms\|secrets\|vpc-endpoints\|s3 --path dump/` | Same contract for the datastore/ops dumps; KMS rotation rule applies only to customer-managed keys |
| `apiforge model alb\|ecs\|eks\|ec2\|msk\|elasticache --path dump/` | Same contract for the compute/LB dumps; plain-HTTP only flags on internet-facing ALBs |
| `apiforge model lambda --path dump/` | Lambda facts offline — env var names only, values never read |
| `apiforge model terraform --path infra/` | API Gateway + Lambda resources from HCL; `${...}` → `AF-TF-UNRESOLVED` |
| `apiforge model sam --path template.yaml` | Serverless resources; `!Ref`/`!Sub` → `AF-SAM-UNRESOLVED` |
| `apiforge model pact\|schemathesis\|k6\|coverage --path r.json` | Test-tool reports → `test.*` facts (tools never run) |
| `apiforge model locust\|jmeter\|gatling\|vegeta\|wrk\|hey\|pytest-benchmark --path r` | Load-tool reports → `test.<tool>.summary` facts — RPS/TPS kept distinct, microbenchmarks never read as load runs |
| `apiforge model zap\|semgrep\|trivy\|gitleaks --path r.json` | Security reports → `sec.*` facts (gitleaks never emits secrets) |
| `apiforge report build --case .apiforge/case --out report.json` | Compose the release evidence bundle |
| `apiforge report sign --report report.json` | Pin body/evidence/catalog hashes into the signature block |
| `apiforge report verify --report report.json` | Name the diverged part (body\|evidence\|catalog\|signature_version); exit 4 |
| `apiforge report keygen --name k [--keys-dir D]` | Ed25519 keypair; `report sign --key`/`verify --pubkey` prove key possession, never identity |
| `apiforge dispatch run --coordinator C --case DIR` | Execute the playbook's dispatchable steps; missing inputs land in `pending`, never crash |
| `apiforge run tool semgrep\|trivy\|gitleaks\|k6 --target T --out R` | Allowlisted scanner execution (fixed argv, no shell, `--dry-run` prints argv) |
| `apiforge run list` | Tool registry — declared metadata (license, capabilities, modes, evidence producer) plus *measured* install status; import-only tools refuse `run` with `AF-RUN-IMPORT-ONLY` |
| `apiforge debate open|submit|close` | Deterministic debate machine — positions cite `fact:` evidence, quorum of 2 sides |
| `apiforge plan strangler --project P --contract C` | Per-route cut plan; migrated routes name the parity evidence still due |
| `apiforge plan architecture --profile w.json` | Decision engine: ranks AWS primitives per role over a declared `WorkloadProfile`; every rejection names its cause, cost stays `cost_to_validate` |
| `apiforge contract list\|show <name>` | Versioned canonical contracts (JSON schema per `<Name>/v1`) |
| `apiforge knowledge list\|show\|check` | Domain packs — source authority dates, runtime matrices, declared evals; `check` cross-validates rule ids |
| `apiforge task create|review|seal|run|accept|reject|status` | Sealed, budgeted unit of work; executor never holds the seal key; acceptor != executor |
| `apiforge brief show --task <id>` | OutcomeBrief — `DONE` is refused while gaps or missing acceptance remain |
| `apiforge graph build --case D --out G` | Canonical provenance graph (nodes.jsonl/edges.jsonl) — same inputs, same bytes |
| `apiforge graph query|impact|trace|coverage --graph G` | Closed-vocabulary queries; coverage names unverified findings and unimplemented ops |
| `apiforge graph export --graph G --out D` | Byte-identical copy + digest manifest; `--format neptune` is a named stub |
| `apiforge model redis --path P` | Static Redis/Valkey call-site scan (py/java/go) → `data.redis.*` facts + `data_access_ir`; `binding: name` is named, never proven |
| `apiforge model elasticache-access --path P` | Same Redis-protocol scan with the inventory declared as ElastiCache — provider named, never inferred |
| `apiforge model mongo\|dynamodb-access\|neptune-access --path P` | MongoDB/DocDB, DynamoDB and Neptune call-site scans → `data.<db>.*` facts + `data_access_ir`; composite postures (full_scan, unfiltered_write, unbounded) come only from declared arguments |
| `apiforge model otel --path export.json` | OTLP/JSON trace export → `perf.otel.*` facts + `performance_run`; incomplete spans named unresolved |
| `apiforge perf compare --baseline A --candidate B --threshold-pct N [--repeat-baseline dir]` | `compare_runs`/`detect_regression` over two PerformanceRuns; `added`/`removed`/`insufficient_data` always named; `--repeat-baseline` measures the noise floor and suppresses deltas inside it |
| `apiforge perf verdict --run run.json [--repeat-baseline dir]` | `passed`/`failed`/`inconclusive` per run — validity conditions (baseline, generator saturation, TPS = completed transactions) name unevaluable evidence, never guess |
| `apiforge perf memory add --run r.json` / `perf memory search --subject S --tool T` | Append-only PerformanceRun store at `.apiforge/perf/runs.jsonl` (hash-backed); search filters declared fields, never infers |
| `apiforge perf suggest --case C` | `suggest_fix`: composes findings + catalog remediation into an `ActionPlan` with `proposed_diff` — never writes |
| `apiforge perf scenario --tool k6\|jmeter\|locust --scenario s.json` | Generate the tool's script for a declared scenario — deterministic template, never executes |
| `apiforge perf chaos` | List the declared controlled failure-injection scenarios (`CHAOS-001..013`) — injection is never executed |
| `apiforge model resilience --path <project>` | Static resilience scan (timeouts, retries, pools, breaker/shutdown/idempotency declarations) → `resilience.*` facts; heuristic, blind spots named |
| `apiforge autonomy status|set|run|runbook|heal|ledger` | Modes observe→supervised→continuous (v1 `recommend`/`sandbox`/`approved` map via `V1_MODE_MAP`, ADR-010) over the policy engine; `set` is itself policy-gated; `heal` runs the 8-stage self-healing pipeline; every evaluation lands in `ledger.jsonl` |
| `apiforge index build|status --project P [--findings f.json]` | Content-hash indexes — 12 kinds (files/symbols/routes/facts + 8 derived); status names added/changed/removed |
| — | `analyze`/`discover` extractors run through `.apiforge/cache/` — hits are recorded in the ledger and named in the payload |

## Agentic layer

Twenty coordinator profiles in `agents/*.md` (one per specialty, each declaring
`rule_areas` and the five executors) plus five executors in
`agents/executors/*.md` (`af-inventory`, `af-extractor`, `af-judge`,
`af-verifier`, `af-synthesizer`). `AGENT_PROTOCOL.md` is the operating
contract every profile points at; `next-step` routes by data, `playbook`
is the dispatch floor, and `.apiforge/economy.jsonl` measures every call.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 2 | input/validation refusal (`AF-INPUT-NOT-FOUND`, `AF-OPENAPI-*`, `AF-CASE-*` storage) |
| 3 | integrity failure or denied/blocked governance result (`AF-CASE-HASH-MISMATCH`, `AF-POLICY-DENY`, `sdd check` not ok, ...) |
| 4 | confirmed finding at `--fail-on` severity or worse |

## Guarantees

- **No network.** No SDK, no model call, no `$ref` resolution over the wire.
- **No code execution.** FastAPI sources are parsed with `ast.parse`, never
  imported.
- **Read-only inputs.** Analyzed files are only read; `out_dir` overlapping an
  input is refused.
- **Reproducible.** Two runs on the same inputs produce byte-identical
  artifacts.

## Supported / unsupported

Supported: OpenAPI 3.1 (JSON or strict YAML — aliases, merge keys, duplicate
keys and custom tags rejected); FastAPI `FastAPI`/`APIRouter` decorators with
literal paths and `include_router`, including cross-file imports; local refs
`#/components/schemas/...` in the contract diff.

Unsupported (emits named `unresolved` diagnostics, never guesses): dynamic
route prefixes/paths, non-literal include targets, external or cyclic `$ref`,
arbitrary JSON Schema inference. See `docs/architecture/mvp-boundaries.md`.

## Verify a case

```bash
python -c "from apiforge.case.service import load_case; print(load_case('.apiforge/case').case_id)"
```

`load_case` re-hashes every declared artifact; tampering raises
`CaseIntegrityError` (`AF-CASE-HASH-MISMATCH`).

## Development

```bash
pytest -q
ruff check . && ruff format --check .
mypy src/apiforge
python scripts/check_release.py
```
