# API Forge — priority execution roadmap

Language: [English](API_FORGE_PRIORITY_EXECUTION_ROADMAP.en.md) · [Português (Brasil)](API_FORGE_PRIORITY_EXECUTION_ROADMAP.md)

## Objective

Evolve API Forge from a deterministic local-first control plane into an
agentic platform that can analyze, execute, verify and operate API changes
with reproducible evidence.

## Execution order

1. Adapter depth
2. Real sandbox execution
3. Independent verification
4. Evals with a real corpus
5. Durable runtime
6. Operational integrations with AWS, databases, brokers and observability
7. Unified product

## Cross-cutting gate

Every adapter must declare an `AdapterExecution` with:

- mode: `static`, `fixture`, `live_read_only` or `live_mutation`;
- status: complete, partial, blocked, failed or inconclusive;
- evidence level: observed, declared, inferred, heuristic or verified;
- input hashes;
- tools and versions used;
- produced evidence;
- limitations and unresolved items.

Declared capability is not execution proof. `live_mutation` never authorizes a
mutation by itself; approval and policy evidence remain mandatory.

## Advancement criteria

A specialization advances to real integration only when it has:

1. a closed and versioned contract;
2. a golden corpus and mutation cases;
3. known false-positive and false-negative tests;
4. a deterministic fake adapter;
5. an optional real read-only adapter;
6. an independent verifier;
7. evidence and limitations exposed in the receipt;
8. rollback and refusal documentation.

## Current state

- **Adapters:** the `AdapterExecution` envelope is integrated into inventory
  and relational, streaming, messaging, analytical and FastAPI adapters;
  dynamic signals remain `unresolved`.
- **Execution:** allowlisted, shell-free commands are available in the
  sandbox, with evidence limited and strong isolation delegated to the host.
- **Verification:** independent verification exists for adapters and sandbox
  results; mutations still fail or remain blocked without policy.
- **Evals:** the initial corpus is based on FastAPI/Spring fixtures and runtime,
  gRPC and observability cases.
- **Runtime:** a persistent control plane provides leases, heartbeats and
  recovery for expired steps.
- **Integrations:** read-only, host-owned boundaries exist for databases,
  brokers and providers; SDKs and credentials remain outside the core.
- **Product:** a shared `ApiForgePlatform` facade is used by CLI/MCP for
  discovery and analysis.

### Completed adaptive-routing waves

- Wave 1: `RoutingPlan/v1` with explicit roles, bounded fallback and replay.
- Wave 2: multidimensional scorecards, freshness and an optional adversarial
  gate.
- Wave 3: local expertise packs, families and multiple implementations.

Each wave was verified and committed separately. Operation remains hostless,
offline-first and without remote updates or automatic overwrite synchronization.

Closing each item requires a real adapter, an authorized environment and
corresponding evidence. Without those, the result remains `REVIEW` or
`BLOCKED`.

## Priority vertical slice

Evolve an existing API using REST, RDS, Redis, Kafka/MSK and OpenTelemetry:

```text
discover → extract → plan → TaskSpec → sandbox → test → load → verify
         → holdout/mutation → receipt → brief DONE/REVIEW/BLOCKED
```

AWS, databases, brokers and exporters remain read-only until identity, scope,
approval, impact and rollback are present in the case.

## Immediate non-goals

- adding more providers without measuring the quality of existing ones;
- declaring production support because a token was detected;
- executing cloud mutations outside approved adapters;
- using model output as evidence without independent verification;
- claiming TPS capability without a reproducible experiment.
