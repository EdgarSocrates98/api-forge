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

## Open engineering directions

Future cycles can deepen TokenSave/Graphify integration, language-specific API
generation, production-safe performance runners, observability correlation,
database access-pattern analysis, dependency impact and host capability
negotiation. The local graph remains the source of truth; external systems must
be accessed through explicit adapters and receipts.
