# API Forge — Claude Operating Guide

Follow [AGENTS.md](AGENTS.md) and [AGENT_PROTOCOL.md](AGENT_PROTOCOL.md).
This repository is local-first: Claude must inspect persisted evidence before
reasoning and must keep complete artifacts available when using compact output.

## Routing

- discovery/API-IR: `.claude/skills/api-forge-discovery`
- contracts/OpenAPI/gRPC: `.claude/skills/api-forge-contract`
- architecture/AWS: `.claude/skills/api-forge-architecture`
- Redis, MongoDB, DynamoDB, Neptune: `.claude/skills/api-forge-data-access`
- tests/security/resilience: `.claude/skills/api-forge-verification`
- load, stress, TPS and capacity: `.claude/skills/api-forge-performance`
- OTel, Datadog and Dynatrace: `.claude/skills/api-forge-observability`
- context, TokenSave and Graphify: `.claude/skills/api-forge-context`
- SDD and release gates: `.claude/skills/api-forge-sdd`

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
- run `apiforge sdd check --root docs/sdd` before shipping.
