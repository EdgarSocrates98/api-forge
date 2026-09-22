# API Forge Agent Instructions

API Forge is a deterministic, offline-first platform for API construction,
evolution, migration, testing, performance, observability, data access,
streaming and messaging.

## Operating contract

1. Read `AGENT_PROTOCOL.md` and load or create a persisted case under
   `.apiforge/case/` before substantive analysis.
2. Run `apiforge next-step` before selecting a specialist when a case has
   findings.
3. Prefer deterministic facts, rules, indexes, Graphify and adapters over model
   memory. Never invent versions, TPS, costs, evidence or runtime capabilities.
4. Use SDD for non-trivial work. Required flow:
   `discover -> intent -> contract -> architecture -> plan -> build -> verify -> secure -> benchmark -> ship`.
5. Build only in sandbox, branch or worktree. Cloud, database and destructive
   actions stay read-only unless an explicit policy gate and approval exist.
6. A compact response is a projection, never the source of truth. Preserve full
   artifacts, hashes, critical errors, findings, contracts and evidence.
7. Do not declare `DONE` without independent verification, holdout/mutation
   checks when applicable, and an Outcome Brief with unresolved gaps.
8. Record tools, versions, commands, results, artifacts and hashes in the case.

## Agentic runtime

The supervisor is deterministic. Agents propose; TaskSpec governs; sandbox
executes; Verifier decides. Dynamic parallelism is allowed only for independent
sealed tasks with budgets. Debate triggers: high risk, contradiction, missing
evidence, or explicit human request.

Use native project capabilities:

- `apiforge context compact` for RTK-style output reduction;
- `apiforge agentops workflows` for Caveman-inspired workflows;
- `apiforge economy report` for measured bytes and transcript-backed tokens;
- `apiforge graph` for provenance and impact;
- `apiforge task`, `runtime`, `sandbox`, `evidence` and `brief` for governed work.

## Data and messaging specializations

Route by engine instead of treating every datastore or broker as generic:

- relational/RDS: `model rds-access`, `model postgres-access`, `model mysql-access`;
- Kafka/MSK/Kinesis: `model kafka-access`, `model msk-access`;
- AWS messaging: `model sqs-access`, `model sns-access`,
  `model eventbridge-access`, `model kinesis-access`;
- low-latency and partitioned data: Redis/Valkey and DynamoDB profiles;
- analytics: `model opensearch-access`, `model redshift-access`;
- brokers: `model rabbitmq-access`, `model nats-access`, `model pulsar-access`;
- document/graph: MongoDB/DocumentDB and Neptune profiles.

Use the corresponding IR (`DataAccessIR`, `StreamingAccessIR`,
`MessagingAccessIR`, `AnalyticalAccessIR`) and preserve the distinction
between observed signals and runtime claims. Never infer indexes, hot keys,
consumer lag, query plans, throughput or delivery guarantees without evidence.

## Safety and evidence

Never suppress critical evidence to save context. Preserve `AF-*` codes, errors,
warnings, failed tests, status codes, security findings and unresolved states.
Local adapters must not call model SDKs, AWS or live databases. External
integrations belong behind explicit read-only adapters and policy gates.
Collectors may create hashed AWS posture dumps only through `collect`; source
models never publish, consume, execute SQL, commit offsets or mutate topology.

## Validation

Before handoff, run focused tests, full tests when practical, Ruff, mypy and
the relevant SDD check. Report exact results and the remaining `unresolved`
items. Use the project handoff shape:

```text
Status:
Outcome:
Human action:
Proof:
Gaps:
Next:
Open:
```
