# API Forge Portable Distribution and Workspace

This guide covers the first portable distribution slice for machines with
restricted network, filesystem or administrative access.

[Português (Brasil)](API_FORGE_PORTABLE_DISTRIBUTION.pt-BR.md) · [Platform
usage in English](API_FORGE_PLATFORM_USAGE.en.md) · [Uso da plataforma em
português](API_FORGE_PLATFORM_USAGE.md)

## Quick start: the complete path

Run these steps from the consumer repository. Every step is local and can be
performed without a host agent, network daemon or provider SDK.

1. Install into a user-owned virtual environment or prefix.
2. Point `APIFORGE_HOME`, `APIFORGE_CONFIG` and `APIFORGE_CACHE` at writable
   locations when the project or system path is restricted.
3. Run `inspect` and `doctor` before creating project state.
4. Run `init` to create only the minimal project manifest.
5. Resolve repository context with `context resolve --scope repo`.
6. Create a virtual workspace and add independent repositories when needed.
7. Resolve `repo`, `workspace` or `target` scope and choose `direct`,
   `transitive` or `all` impact.
8. Inspect host/MCP capabilities and request an activation plan only when an
   integration is needed.

The grouped commands are also available as
`apiforge distribution inspect|init|status|doctor`; the top-level aliases
shown below are equivalent and shorter.

## Install without administrator access

Use a user-owned virtual environment or prefix. The examples do not write to a
system directory:

```powershell
uv venv E:\tools\api-forge-env
E:\tools\api-forge-env\Scripts\python.exe -m pip install apiforge[all]
$env:PATH = "E:\tools\api-forge-env\Scripts;$env:PATH"
```

```bash
uv venv "$HOME/.local/share/api-forge-env"
"$HOME/.local/share/api-forge-env/bin/python" -m pip install 'apiforge[all]'
export PATH="$HOME/.local/share/api-forge-env/bin:$PATH"
```

If `PATH` cannot be changed, invoke the executable by its absolute path. API
Forge does not require a global installer, symlink or admin permission.

## Move runtime state

```powershell
$env:APIFORGE_HOME = "E:\portable\api-forge-state"
$env:APIFORGE_CONFIG = "E:\portable\api-forge.yaml"
$env:APIFORGE_CACHE = "E:\portable\api-forge-cache"
apiforge doctor
```

`APIFORGE_HOME` is user-owned state/cache, not the installed package root.
`inspect` and `doctor` show the resolved package, executable, state, config and
cache paths. No path is created during inspection.

## Hostless first run

```text
apiforge inspect
apiforge init
apiforge status
apiforge doctor
apiforge context resolve --scope repo
```

These commands continue to work with network blocked and without Claude,
Codex, Devin, Copilot, MCP or provider SDKs. Optional gaps are explicit and do
not erase local SDD, agents, skills, graph, evidence or verification.

For a nested module or a workspace target:

```text
apiforge context resolve --scope workspace
apiforge context resolve --scope target --target repository:<stable-id>
apiforge context resolve --scope workspace --impact direct
apiforge context resolve --scope workspace --impact transitive
```

The accepted scopes are `repo`, `workspace` and `target`; accepted impact
values are `direct`, `transitive` and `all`. An unknown target returns
`AF-CONTEXT-TARGET-NOT-FOUND` instead of silently widening the selection.

## Minimal manifests

`apiforge init` creates only `.apiforge/project.yaml`. Use
`apiforge init --workspace` to create `.apiforge/workspace.yaml`, then register
independent repositories:

```text
apiforge workspace init --root C:\work\platform
apiforge workspace add C:\work\orders --root C:\work\platform
apiforge workspace status --root C:\work\platform
apiforge context resolve --root C:\work\platform --scope workspace
```

The first graph wave accepts declared relationships and bounded local signals.
It does not infer every language/provider relationship and never claims runtime
deployment from a directory name.

For POSIX or WSL, the same sequence is:

```bash
apiforge workspace init --root "$HOME/work/platform" --name platform
apiforge workspace add "$HOME/work/orders" --root "$HOME/work/platform"
apiforge workspace status --root "$HOME/work/platform"
apiforge context resolve --root "$HOME/work/platform" --scope workspace
```

## Host adapters and MCP

Host activation is generated from package-owned templates and defaults to a
plan/preview. It includes source hashes, limitations and `mutation: none`.
Conflicting user-owned files are not overwritten. MCP is local stdio and is
optional; its absence is `AF-MCP-OPTIONAL-UNAVAILABLE`, not a failure of core
operation.

Inspect the optional host boundary with:

```text
apiforge agentops hosts
apiforge agentops parity
apiforge agentops negotiate --capability mcp
apiforge agentops activation-plan --host claude
```

Activation remains `plan_only`, includes source hashes and requires approval
for mutation. The separate `apiforge here` command is intentionally not part
of this wave; context resolution is internal.

## Troubleshooting

| Situation | Safe action |
|---|---|
| The default state path is not writable | Set `APIFORGE_HOME` and `APIFORGE_CACHE` to user-owned paths. |
| The executable is not on `PATH` | Invoke it by absolute path from the selected environment. |
| Network or host is unavailable | Continue offline; use `doctor` to inspect named optional gaps. |
| MCP is missing | Install the `mcp` extra only when local MCP stdio is required. |
| A manifest is invalid | Preserve the file and correct the field named by `AF-MANIFEST-INVALID`. |
| A host file conflicts | Review the plan and source hash; do not enable automatic overwrite. |
| Root discovery is unresolved | Run from the repository or pass an explicit `--root`. |

## Security boundary

Discovery never executes consumer code, shell hooks or prompts. Manifests do
not accept secrets. Network freshness, production runtime behavior and host
parity require their own evidence receipt. Deferred items remain in the
evolution map and are not silently enabled by this slice.
