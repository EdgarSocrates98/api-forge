# API Forge — Claude Operating Guide

Follow [AGENTS.md](AGENTS.md) and [AGENT_PROTOCOL.md](AGENT_PROTOCOL.md).
This repository is local-first: Claude must inspect persisted evidence before
reasoning and must keep complete artifacts available when using compact output.

## Routing

- discovery/API-IR: `.claude/skills/api-forge-discovery`
- contracts/OpenAPI/gRPC: `.claude/skills/api-forge-contract`
- architecture/AWS: `.claude/skills/api-forge-architecture`
- Redis/Valkey, DynamoDB, MongoDB/DocumentDB, Neptune and RDS/Aurora:
  `.claude/skills/api-forge-data-access`
- PostgreSQL/MySQL, Kafka/MSK, SQS/SNS/EventBridge/Kinesis, OpenSearch/Redshift,
  RabbitMQ/NATS/Pulsar: route through the data-access and architecture skills;
  use the specialized `model *-access` commands documented in `README.md`.
- tests/security/resilience: `.claude/skills/api-forge-verification`
- load, stress, TPS and capacity: `.claude/skills/api-forge-performance`
- OTel, Datadog and Dynatrace: `.claude/skills/api-forge-observability`
- context, TokenSave and Graphify: `.claude/skills/api-forge-context`
- SDD and release gates: `.claude/skills/api-forge-sdd`
- API/Git/CI change governance: `apiforge change-control` with the
  `af-change-bundle/1` replay contract; use `docs/architecture/API_FORGE_API_GIT_CICD_CONTROL_PLANE.md`
  and `docs/security/api-git-cicd-control-plane.md` for the boundary.
- The governed change route is `analyze -> next-step -> graph -> evidence ->
  brief -> verify -> publish`; `collect` is an explicit GitHub GET-only ingress
  and its receipt never proves authorship, deployment safety or freshness.

## Caveman/RTK behavior

Use `apiforge context compact` for command artifacts and select a mode according
to context pressure. Compact output must retain critical lines and point to the
full artifact. Use `apiforge agentops workflow <name>` to expose the declared
phases; do not treat a workflow plan as authorization to mutate.

```text
apiforge agentops filters
apiforge agentops workflows
apiforge agentops hosts
apiforge economy report --root <case>
```

Claude may open a debate room only on risk, divergence, missing proof or human
request. Every position must cite evidence. The final recommendation must name
the verifier, unresolved gaps and next human action.

## Implementation rules

- no provider SDK imports in `src/`;
- no live AWS/database mutation from the core;
- no direct writes to the main tree during build;
- use `apply_patch` for edits;
- update tests and SDD artifacts together;
- update the relevant IR, agent routing and host mirrors when adding a new
  datastore, broker or messaging specialization;
- for API changes tied to Git or CI/CD, preserve the read-only adapter boundary,
  recommendation fields, metrics, receipt and unresolved provider limitations;
- every refusal must preserve an `AF-*` code, `field` and `unlock` in CLI/MCP
  output and the code must be cataloged;
- validate JUnit/Markdown publisher output and the local IDE/UI host when the
  change-control surface is part of the task;
- run `apiforge sdd check --root docs/sdd` before shipping.
