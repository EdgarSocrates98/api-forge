# API Forge Experience and Interoperability (English)

The terminal, JSON, MCP, Rich/TUI and host surfaces project the same canonical
application results. Presentation can change; status, evidence, gaps and safety
semantics cannot.

[Português (Brasil)](API_FORGE_EXPERIENCE_INTEROPERABILITY.md) · [Portable
distribution in English](API_FORGE_PORTABLE_DISTRIBUTION.md) · [Distribuição
portátil em português](API_FORGE_PORTABLE_DISTRIBUTION.pt-BR.md)

## TUI and fallback

Install the optional terminal UI only when needed:

```bash
python -m pip install -e '.[tui]'
apiforge tui TASK --root .
```

In CI or without Textual:

```bash
apiforge tui TASK --root . --fallback
```

The fallback preserves the same `ExperienceSnapshot`. The legacy commands
remain supported, and the modular projection is:

```bash
apiforge experience status TASK
apiforge experience doctor TASK
apiforge experience review TASK
```

## Portable distribution and context

The first-wave hostless path is:

```text
apiforge inspect
apiforge init
apiforge status
apiforge doctor
apiforge workspace status
apiforge context resolve --scope repo
```

The same application facades feed CLI, JSON, MCP and host projections. A
separate `apiforge here` command is intentionally deferred; context resolution
is internal. The local path works without an agent host, network port or
provider SDK.

## Evidence levels

Portable, run, verification and host contracts use:

```text
observed · declared · inferred · heuristic · verified · unknown
```

Missing evidence is not success. A `verified` result must point to an
independent receipt or proof at the layer that produced it.

## Knowledge freshness

Knowledge packs can declare `freshness.window_days`, `freshness.source_hash` and
`freshness.authority`:

```bash
apiforge knowledge freshness rest-design \
  --receipt .apiforge/source-receipt.json \
  --now 2026-09-23T00:00:00Z
```

The core does not rewrite packs or perform automatic refresh. Missing receipts
remain `unresolved`; mismatched hashes or expired windows are `stale`.

## Host capabilities and activation

```bash
apiforge agentops negotiate --capability mcp
apiforge agentops negotiate --capability subagents --host claude
apiforge agentops activation-plan --host claude
```

Host declarations may be placed under `.apiforge/hosts/*.json`. The resolver
publishes intersections and limitations, never host equivalence. Packaged host
templates include source hashes and previews are `mutation: none`; conflicts
are explicit, and automatic overwrite and symlink modes remain deferred.

## Python matrix and adaptive debate

Observed interpreter cells use receipts:

```bash
apiforge migration matrix --ecosystem python \
  --receipt .apiforge/python-3.12.json \
  --receipt .apiforge/python-3.14.json
```

Adaptive debate is bounded by policy, quorum, rounds and retry budget. Positions
must cite facts; real providers remain external adapters and deterministic fakes
are used for mandatory local gates.

## Adaptive routing, scorecards and expertise

CLI, MCP, TUI and bridge surfaces project the same decision and
`RoutingPlan/v1`. A run keeps `routing.json` for compatibility and writes
`routing-plan.json` with `primary`, `fallbacks`, `parallel`, `reviewers`,
`critic` and `referee`, so the plan can be reviewed without a host.

Scorecards are promoted only after an evidence gate and can carry
multidimensional quality, cost, duration, tokens and freshness. The adaptive
corpus can require `golden`, `holdout`, `mutation` and `adversarial` cases;
observed signals need receipts, while stale/unresolved states remain
unpromoted.

Capabilities may declare a family, implementation and expertise packs. A family
request compares eligible implementations. A missing pack returns
`AF-CAPABILITY-ELIGIBILITY` with `field=capability.expertise_packs`; the core
does not download knowledge or alter host-owned files.

## Gates

```text
uv run --no-sync ruff check .
uv run --no-sync mypy src/apiforge
uv run --no-sync pytest -q
uv run --no-sync python scripts/check_release.py
```

See the [Portuguese interoperability guide](API_FORGE_EXPERIENCE_INTEROPERABILITY.md)
for the broader platform examples and the [catalog contract](../catalog-contract.md)
for refusal codes and unresolved-state semantics.
