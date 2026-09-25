# API Forge — Evolution Map (English)

This is the English companion for the Portuguese evolution map. It records the
shipped portable-distribution wave and the work intentionally deferred to later
SDD cycles.

[Português (Brasil)](API_FORGE_EVOLUTION_MAP.md) · [Portable guide](guides/API_FORGE_PORTABLE_DISTRIBUTION.md) · [Platform usage](guides/API_FORGE_PLATFORM_USAGE.en.md)

## Current baseline

API Forge already provides deterministic API IR, facts, findings, provenance,
hash cascades, evidence receipts, sealed TaskSpecs, sandbox execution,
verification, holdouts, graph queries, contract intelligence, performance and
observability plans, migration control and read-only external adapters.

The safety boundary is intentional: local/static evidence and explicitly
authorized read-only adapters come before network mutation or production claims.

## Shipped program: portable distribution, workspace and host activation

The first portable wave is shipped and archived. It provides:

- user-local, virtual-environment and user-selected-prefix installation without
  administrator privileges;
- package-owned agents, skills, knowledge, contracts, SDD assets and host
  templates, with user-owned state/config/cache overrides;
- hostless `inspect`, `init`, `status`, `doctor` and `context` operation with
  blocked-network and missing-optional-capability diagnostics;
- internal context resolution for `repo`, `workspace` and `target` scopes with
  `direct`, `transitive` and `all` impact modes;
- minimal `.apiforge/project.yaml` and `workspace.yaml` manifests for
  independent repositories, without forcing a monorepo;
- bounded architecture graph and context payloads that preserve observed,
  declared, inferred, heuristic, verified and unresolved evidence states;
- optional local MCP stdio and plan-only host adapters with source hashes and
  explicit conflict/overwrite limits.

The implementation and verification record is archived at:

`.claude/sdd/archive/API_FORGE_PORTABLE_DISTRIBUTION_WORKSPACE/`

## Shipped program: adaptive routing in three waves

The three waves were completed in sequence:

1. `RoutingPlan/v1`: primary, fallbacks, parallel, reviewers, critic and
   referee, with a compatible decision, persisted plan and auditable
   `ControlPlane` transitions.
2. Scorecards/evals: quality dimensions, cost, duration, tokens, freshness,
   receipts for observed signals and an optional `adversarial` gate.
3. Expertise: versioned local packs, family selection, multiple
   implementations and explicit refusals when required knowledge is missing.

The default remains offline-first, deterministic and bounded. Run artifacts are
`routing.json` and `routing-plan.json`; no wave depends on a host, network,
model SDK or external mutation.

## Post-ship roadmap

The following capabilities remain in the program and were not removed:

1. autonomous high-level orchestration through `ask`, `improve`, `migrate` and
   `fix`;
2. complete relationship inference across repository, language, provider and
   infrastructure types;
3. a separate `apiforge here` command in addition to internal context
   resolution;
4. auto-update and remote Knowledge Pack updates;
5. symlink as an installation mode;
6. automatic synchronization that overwrites host-owned files;
7. complete configuration precedence down to task scope;
8. distributed multi-agent debate across a workspace;
9. a promise of total functional parity between hosts.

Each item must return to:

```text
discover → intent → contract → architecture → plan → build → verify
→ secure → benchmark → ship
```

Every future item needs its own evidence, limitations, security policy and
independent verification. No deferred item is enabled as a side effect of the
portable distribution release.

## Detailed engineering backlog

The open directions below deepen TokenSave/Graphify integration,
language-specific API generation, production-safe performance runners,
observability correlation, database access-pattern analysis, dependency impact
and host capability negotiation. The local graph remains the source of truth;
external systems must be accessed through explicit adapters and receipts.

### 1. Agentic runtime and governance

- make the supervisor dynamically schedule work using complexity, dependencies,
  budgets and risk;
- persist leases, retries, checkpoints, cancellation, resumption and run
  idempotency;
- make task review an independent gate before `DONE`;
- make debate rooms reproducible with positions, rebuttals, quorum, referee and
  decision;
- measure agent quality through cost, latency, rework, acceptance and
  regression;
- add real model adapters with fallback, task routing and data policy without
  claiming unsupported host features.

### 2. Context, TokenSave and Graphify

- apply the context funnel automatically across all phases;
- connect facts, findings, tasks, tests, traces, decisions, commits and
  releases in the provenance graph;
- add impact queries for endpoint, database and SLO changes;
- consolidate hash-based caching, deduplication, compression and per-agent
  budgets;
- measure saved tokens, avoided bytes, cache hits and cost per result;
- export to Neptune only through an approved adapter, keeping the local graph
  authoritative.

### 3. Contracts and API design

- complete OpenAPI design-first linting, style guides, mocks, examples and
  contract tests;
- evolve gRPC with a protobuf registry, breaking checks, real code generation
  and a gateway;
- close GraphQL and AsyncAPI with schema diff, compatibility, mocks and event
  tests;
- generate and compile Java/Spring, Go and Python/FastAPI vertical slices in a
  sandbox;
- standardize RFC 7807, versioning, pagination, idempotency and semantic
  compatibility policies.

### 4. Code construction and evolution

- implement complete vertical slices with tests, documentation and IaC;
- provide safe Java, Go and Python migration paths;
- generate small migration patches with build, test, benchmark, rollback and
  risk evidence;
- detect frameworks, runtimes, breaking changes and dependency
  vulnerabilities;
- add independent diff review, mutation checks and contract-to-patch proof;
- keep templates aligned with dated version matrices and knowledge sources.

### 5. Testing, performance and capacity

- run approved k6, JMeter, Locust, Gatling, Vegeta, wrk and hey runners;
- distinguish RPS, business TPS, concurrency, latency, throughput, saturation
  and errors;
- implement load, stress, spike, soak, capacity, failover and controlled
  degradation tests;
- validate warmup, steady state, generator saturation, repeat baselines and
  statistical noise;
- derive capacity and scaling recommendations only from evidence.

### 6. Operational observability

- connect exporters through host-owned clients with timeout, retry, rate limit
  and redaction;
- validate real OTel, Datadog and Dynatrace schemas and conventions;
- create dashboards, alerts and runbooks only through approved mutation gates;
- correlate API, gateway, application, database, cache, Kafka, queue and
  downstream traces;
- complete SLI/SLO, error budget, burn rate and incident timelines.

### 7. Data and dependencies

- evolve Redis, Mongo/DocDB, DynamoDB and Neptune analysis for schema, indexes,
  TTL, hot keys, query plans, pagination and consistency;
- distinguish observed facts, user declarations and bounded inference;
- add read-only adapters with credentials, timeouts, budgets and sanitized
  fixtures;
- model contract impact across consumers, jobs, events and data.

### 8. AWS, infrastructure and delivery

- complete WorkloadProfile with quotas, regions, cost, RTO/RPO and dependencies;
- generate Terraform/SAM/CDK only in sandbox with plan, policy, diff, approval
  and rollback;
- validate IAM least privilege, VPC, private endpoints, WAF, Secrets Manager,
  KMS and tagging;
- add read-only drift and explicit reconciliation;
- produce SBOM, provenance and release bundles with integrity evidence.

### 9. Security and reliability

- automate threat modeling for API, data, identity, network and toolchain;
- orchestrate SAST, SCA, DAST, secrets, IaC, container and dependency scans;
- test authentication, authorization, RBAC/ABAC, mTLS, JWT, OAuth/OIDC,
  rate limiting and tenant isolation;
- add contract fuzzing, property tests, mutation tests and adversarial agent
  tests;
- define universal redaction for logs, traces, payloads, prompts, receipts and
  exporters.

### 10. Evals, knowledge and skills

- build golden/holdout corpora for Java, Go, Python, REST, gRPC, GraphQL,
  events and databases;
- measure planner, builder, reviewer, verifier, debate and synthesis quality;
- add prompt-injection, tool-misuse, exfiltration and scope-creep evals;
- version knowledge packs with authority, dates, runtime matrices, validity and
  source;
- publish portable skills for Claude, GPT/Codex, Devin and Copilot through a
  common protocol;
- test command, contract, capability and evidence parity without claiming
  unsupported host equivalence.

### 11. Product and experience

- consolidate CLI, MCP and a control-plane API over the same contracts;
- keep terminal-first TUI and Rich/JSON fallback projections consistent;
- provide project templates, onboarding, vertical-slice examples and
  troubleshooting;
- add consistent `explain`, `dry-run`, `review`, `approve`, `resume` and
  `export` modes;
- keep architecture, boundaries, threat model, ADR, skill and compatibility
  documentation current.

## Strategic order

| Phase | Objective | Exit criterion |
|---|---|---|
| A | Agentic runtime integrity | Resumable runs, independent reviewer and quality metrics |
| B | Contracts and multi-language codegen | Compiling Java, Go and Python vertical slices |
| C | Real testing and capacity | Statistically valid load/TPS evidence with rollback |
| D | Operational observability | Authenticated OTel/Datadog/Dynatrace with approved runbooks |
| E | Governed data and AWS | Read-only analysis and gated apply paths |
| F | Security and resilience | Security gates, fuzz/mutation and controlled failure |
| G | Evals and portability | Measured quality and explicit host capability boundaries |
| H | Product/platform | Reproducible onboarding and contract-driven operation |

## Rules that preserve direction

1. Start every evolution with intent, contract, architecture, plan and risk.
2. Give every task a test or proof, owner, rollback and evidence.
3. Keep external integrations host-owned, approval-gated and disabled by
   default.
4. Require independent verification, holdout/mutation where applicable and a
   gap-aware brief before `DONE`.
5. Never replace a fact with silent inference.
6. Measure cost improvements through tokens, bytes, time and quality.
7. Select the next work by dependency and risk, not a fixed linear list.

## Integrated cycle completed

Phases A–G were implemented sequentially, each with its own commit and SDD
evidence. Phase H consolidates documentation, executes the full suite and
closes the release. Future cycles should activate real adapters only in
approved environments, with load runners, vendor schemas, read-only queries,
Terraform plans and compilable multi-language evals.

## Completed data and messaging specializations

| Order | Area | Delivery |
|---|---|---|
| 1 | RDS/Aurora and relational | SQL scanner, pools, transactions, pagination and RDS collector |
| 2 | Kafka/MSK | `StreamingAccessIR`, topics, groups, roles and delivery signals |
| 3 | AWS messaging | `MessagingAccessIR` for SQS, SNS, EventBridge and Kinesis |
| 4 | Low latency and scale | Redis/Valkey and DynamoDB profiles based on facts |
| 5 | Analytics | `AnalyticalAccessIR` for OpenSearch and Redshift |
| 6 | Brokers | RabbitMQ, NATS and Pulsar in the streaming IR |
| 7 | Document/graph | MongoDB/DocumentDB and Neptune bounded profiles |

Live query plans, consumer lag, proven throughput, hot keys, explain plans,
cluster health, replay, provisioning and external mutations still require
approved adapters and independent evidence.
