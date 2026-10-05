# API Forge — Evo Convergence Outcome Brief

Date: 2026-10-05 (America/Sao_Paulo)  
Branch: `codex/evo-convergence`  
Baseline: `daae355a78664befabbc4321eeefa5c049ba37cb`

## Status

Local convergence is verified and release-ready for the host-controlled
Git/CI boundary. Provider freshness, vulnerability feeds, deployment safety,
automatic merge and post-merge main verification remain external gates.

## What was delivered

The implementation followed the required SDD chain:

`discover → intent → contract → architecture → plan → build → verify → secure → benchmark → ship`

| Wave | Commit | Delivery |
|---|---|---|
| Baseline and SDD | `29cf213` | persisted case/routing, baseline, gap matrix and convergence SDD |
| AgentOps P0 | `f2834d9` | canonical context metrics, tri-state decision aggregation, truthful model-call/token/provider/latency dimensions |
| Runtime governance | `c9ea769` | persisted `RunGovernanceContext/v1`, governor ceilings, expected-gain stop, loop fingerprint and recovery classification |
| Routing/retrieval/memory | `f222acf` | risk/budget/freshness routing constraints, champion/challenger admission, scorecard provenance and memory coverage semantics |
| Protocol/lab hardening | `092d6f3` | MCP optional lock/probe, default-deny gateway authorization, 13-scenario lab catalog, loop/recovery runtime integration |
| Trust/context/supply chain | `5c20396` | evidence-aware context quality, counterfactual ablation, bounded graph traversal, tool authorization crossing, deterministic CycloneDX SBOM |
| Final hardening | `f12b549` | budget regression fix, retrieval graph-dir contract, CLI exposure, SDD evidence and documentation refresh |

## Architecture convergence

Before this work, the platform had strong deterministic primitives but several
parallel projections: `execute_run()` bypassed governance context, AgentOps
used legacy metric names and booleans, L2 retrieval implied graph behavior
without a graph artifact, and the optional MCP dependency was not locked.

After this work, the runtime persists a small governance context before
expansion, routes through declared constraints, authorizes gateway/tool
crossings, preserves evidence and unresolved states, and records a replayable
trajectory. Retrieval and memory expose provenance and explicit missing-input
states. The lock, protocol probe and SBOM are deterministic local artifacts;
they do not claim provider or production behavior.

## Verification

- Full suite: `1723 passed, 2 skipped` using the controlled external basetemp
  `E:/pytest-apiforge-evo-convergence-final`.
- `uv run ruff check src tests`: passed.
- `uv run ruff format --check src tests`: passed.
- `uv run mypy`: passed, 557 source files.
- Release, skills/mirror, agent drift, capabilities and SDD checks: passed.
- Platform runtime probes: 6/6 local fixture verticals passed.
- Lab scenarios: 13/13 covered, 0 declared gaps.
- Retrieval eval: 1/1 case passed; graph absence and cost rate are explicit
  unresolved fields when no graph directory or cost rate is supplied.
- MCP benchmark: 10 sampled tools, no unresolved benchmark output; token
  counts are labeled estimated.
- `uv.lock` check and lock audit: 68 packages, 67 hashed registry packages.
- MCP protocol probe: SDK 2.3.0 observed with protocol revision 2026-07-28.
- Supply-chain audit: `ok=true`, with external CVE and local `pip check`
  limitations preserved.

## Safety and evidence boundaries

No provider, cloud, database, live model, deployment or external mutation was
used. Local runtime probes prove committed fixtures only. A production claim
requires an independent receipt. The host's default pytest temp directory is
ACL-inaccessible; the controlled basetemp is recorded rather than hiding that
environmental failure.

## External research applied

- MCP protocol claims follow the official [MCP 2026-07-28 specification
  announcement](https://blog.modelcontextprotocol.io/posts/2026-07-28/), while
  local support remains an observed SDK/protocol probe.
- Locking and reproducibility follow the official [uv projects
  guide](https://docs.astral.sh/uv/guides/projects/) and [uv sync
  documentation](https://docs.astral.sh/uv/concepts/projects/sync/).
- The SBOM projection follows the official [uv export
  documentation](https://docs.astral.sh/uv/concepts/projects/export/) as a
  CycloneDX-compatible lock projection.

## Open items

1. Push this branch and let the dedicated green-validation CI job create or
   reuse the PR; only that job may perform the PR mutation.
2. Observe all required CI checks and automatic merge policy.
3. After merge, observe the main-branch validation run.
4. Obtain external CVE/advisory, provider freshness, deployment and
   production-SLO receipts before closing the corresponding deviations.

The complete phase artifacts and hashes are in
[`docs/sdd/API_FORGE_EVO_CONVERGENCE/`](../sdd/API_FORGE_EVO_CONVERGENCE/),
and the persisted execution case is in
[`.apiforge/case/`](../../.apiforge/case/).
