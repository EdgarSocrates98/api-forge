# API Forge Platform Completion Architecture

Language: [English](API_FORGE_PLATFORM_COMPLETION.md) · [Português (Brasil)](API_FORGE_PLATFORM_COMPLETION.pt-BR.md)

API Forge is a deterministic control plane for software engineering work. Its
surfaces can accept a natural-language intent, but the execution boundary is
always a typed request, a persisted case, a policy decision and a verifiable
artifact.

```text
CLI / MCP / IDE / UI
          │
          ▼
CapabilityRequest/v1 → deterministic supervisor → specialist AgentArtifact/v1
          │                       │                         │
          ▼                       ▼                         ▼
       case/IR              policy + adapters       evidence + unresolved
          └───────────────────────┴──────────────────────────┘
                                  ▼
                         graph → receipt → brief
```

The core does not import model, cloud, database or broker SDKs. External
integrations use the read-first gateway. Any mutation needs a policy decision,
approval, rollback and receipt. A provider without proof remains
`unsupported` or `unresolved`.

The same `CapabilityRequest` and `CapabilityResult` contracts are projected by
CLI, MCP, IDE and UI. Presentation can change; support state, evidence, gaps
and safety semantics cannot.

The initial proof set covers APIs, databases, messaging, CI/CD, cloud and
front-end through one fixture, one golden and one holdout per vertical. The
holdout requirement is essential: it proves that agents and adapters preserve
uncertainty instead of manufacturing an optimistic answer.

Operational commands, fixture locations and the production support boundary
are documented in [API Forge Platform Usage](../guides/API_FORGE_PLATFORM_USAGE.md).
