# API Forge Platform Usage (English)

This is the English operational guide for the portable distribution, hostless
commands, workspace context and evidence-first workflow.

[Português (Brasil)](API_FORGE_PLATFORM_USAGE.md) · [Portable distribution in
English](API_FORGE_PORTABLE_DISTRIBUTION.md) · [Distribuição portátil em
português](API_FORGE_PORTABLE_DISTRIBUTION.pt-BR.md)

## 1. Operating contract

API Forge is deterministic, offline-first and evidence-first. It observes local
artifacts, builds IRs and facts, and produces bounded plans. It does not turn a
parser, prompt, fixture or nominal integration into runtime proof.

Before a governed analysis:

```text
1. Read AGENT_PROTOCOL.md.
2. Load or create a case under .apiforge/case/.
3. If findings exist, run apiforge next-step before choosing a specialist.
4. Preserve diagnostics, hashes, evidence and unresolved states.
```

## 2. Install and diagnose without a host

Use a user-owned virtual environment or prefix. The installed package owns its
agents, skills, knowledge packs, contracts and templates; a consumer repository
does not need a copied Forge tree.

```bash
uv venv "$HOME/.local/share/api-forge-env"
"$HOME/.local/share/api-forge-env/bin/python" -m pip install 'apiforge[all]'
export PATH="$HOME/.local/share/api-forge-env/bin:$PATH"

apiforge inspect
apiforge doctor
```

On Windows, use the `Scripts` directory and PowerShell environment variables as
shown in the [portable distribution guide](API_FORGE_PORTABLE_DISTRIBUTION.md).
If the default state path is not writable:

```bash
export APIFORGE_HOME="$HOME/.local/state/api-forge"
export APIFORGE_CONFIG="$HOME/.config/api-forge/config.yaml"
export APIFORGE_CACHE="$HOME/.cache/api-forge"
```

`doctor` names optional capabilities as `ready`, `unavailable`, `degraded`,
`unresolved` or `blocked`; an unavailable host or network does not disable local
SDD, agents, skills, graph, evidence or verification.

## 3. Initialize a project and resolve repository context

```bash
apiforge init
apiforge status
apiforge context resolve --scope repo
```

`init` writes only `.apiforge/project.yaml`. Context discovery is bounded and
read-only: current module, Git repository, project manifest and optional parent
workspace. There is intentionally no separate `apiforge here` command.

## 4. Connect independent repositories as a workspace

```bash
apiforge workspace init --root "$HOME/work/platform" --name platform
apiforge workspace add "$HOME/work/orders" --root "$HOME/work/platform"
apiforge workspace add "$HOME/work/billing" --root "$HOME/work/platform"
apiforge workspace discover --root "$HOME/work/platform"
apiforge workspace status --root "$HOME/work/platform"
apiforge context resolve --root "$HOME/work/platform" --scope workspace
```

Each repository keeps its own `.git`. Workspace manifests are a virtual
registry, not a monorepo conversion. Declared, observed, inferred and
unresolved relations remain distinct.

## 5. Narrow scope and impact

The closed context scopes are:

```bash
apiforge context resolve --scope repo
apiforge context resolve --scope workspace
apiforge context resolve --scope target --target repository:<stable-id>
apiforge context resolve --scope workspace --impact direct
apiforge context resolve --scope workspace --impact transitive
apiforge context resolve --scope workspace --impact all
```

The result is the canonical payload for CLI, JSON, MCP and host projections. It
contains selected targets, included repositories, graph data, the measured
funnel, evidence, gaps and `unresolved` diagnostics.

## 6. Run the deterministic proof chain

```text
analyze -> next-step -> graph -> evidence -> brief
```

```bash
apiforge analyze \
  --contract tests/fixtures/openapi/orders-v1.yaml \
  --project tests/fixtures/fastapi_orders \
  --out-dir .apiforge/case
apiforge next-step --findings .apiforge/case/findings.json --phase verify
apiforge graph build --case .apiforge/case --out .apiforge/graph
apiforge evidence emit --case .apiforge/case --out .apiforge/evidence/receipt.json
apiforge evidence verify --receipt .apiforge/evidence/receipt.json
apiforge task create platform-review --outcome "review platform readiness" --root .apiforge
apiforge brief show --task platform-review --root .apiforge
```

`DONE` is not a substitute for independent evidence. Keep missing artifacts,
failed checks, stale receipts and unresolved gaps visible.

## 7. Hosts and local MCP

Hosts are optional adapters, not API Forge authorities or prerequisites:

```bash
apiforge agentops hosts
apiforge agentops parity
apiforge agentops negotiate --capability mcp
apiforge agentops activation-plan --host claude
apiforge agentops activation-plan --host gpt-codex
apiforge agentops activation-plan --host devin
apiforge agentops activation-plan --host copilot
```

Activation is `plan_only`, source-hash-aware and approval-gated. It does not
overwrite user-owned files automatically. MCP uses local stdio; if the optional
extra is absent, the named refusal is `AF-MCP-OPTIONAL-UNAVAILABLE`.

## 7.1 Three-wave adaptive routing

The supervisor persists two complementary run artifacts: `routing.json` keeps
the compatible decision/ranking trace, while `routing-plan.json` exposes
execution roles (`primary`, `fallbacks`, `parallel`, `reviewers`, `critic` and
`referee`). Consumers must not interpret `fallback_order` as mandatory calls.

Local walkthrough:

```bash
apiforge task create routing-demo --outcome "review contract" --root .apiforge
apiforge runtime run routing-demo --root .
apiforge runtime status routing-demo --root .
```

1. The TaskSpec and policy produce a `RoutingRequest`.
2. The registry, scorecards and evidence produce a `RoutingDecision`.
3. The runtime derives a stable, bounded `RoutingPlan/v1`; parallel review is
   the compatible default.
4. Unused fallbacks are recorded as `skipped` with an auditable reason; risk,
   failures and evidence gaps remain visible as `AF-*` codes.

Scorecards are promoted only after an evidence gate and can carry dimensions,
cost, duration, tokens and freshness. The adaptive gate covers `golden`,
`holdout`, `mutation` and `adversarial` cases:

```bash
apiforge evals list --path tests/evals/cases/adaptive_routing.yaml
apiforge evals validate --path tests/evals/cases/adaptive_routing.yaml
apiforge knowledge check --root knowledge
apiforge knowledge freshness --root knowledge
```

Every observed signal needs a receipt; `stale` or `unresolved` signals do not
promote quality. A missing expertise pack refuses a candidate with
`field=capability.expertise_packs` and an explicit unlock. Packs are local and
declarative: families can compare multiple implementations without download,
auto-update, symlink or automatic host-file overwrite.

The canonical machine-readable references are [`RoutingPlan/v1`](../contracts/RoutingPlan-v1.md)
and [`ExpertisePack/v1`](../contracts/ExpertisePack-v1.md). They describe the
persisted plan and local knowledge metadata without authorizing provider calls
or host-file mutation.

## 8. Capabilities and external evidence

```bash
apiforge capabilities list
apiforge capabilities verify
```

Use read-only adapters and receipts for GitHub, health endpoints and other
external sources. A receipt proves the observed bytes and declared freshness;
it does not prove authorship, permissions, deployment, rollback or production
health.

## 9. Validation before commit or release

```bash
uv run --no-sync ruff check .
uv run --no-sync mypy src/apiforge
uv run --no-sync pytest -q
uv run --no-sync python scripts/check_release.py
```

The core remains safe to use offline. Automatic host overwrite, symlink
installation, remote knowledge updates, task-level precedence, distributed
workspace debate, complete relation inference, high-level autonomous
orchestration and total host parity remain deferred roadmap items.
