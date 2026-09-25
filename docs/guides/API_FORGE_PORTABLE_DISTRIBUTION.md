# API Forge Portable Distribution and Workspace

This guide covers the first portable distribution slice for machines with
restricted network, filesystem or administrative access.

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

## Host adapters and MCP

Host activation is generated from package-owned templates and defaults to a
plan/preview. It includes source hashes, limitations and `mutation: none`.
Conflicting user-owned files are not overwritten. MCP is local stdio and is
optional; its absence is `AF-MCP-OPTIONAL-UNAVAILABLE`, not a failure of core
operation.

## Security boundary

Discovery never executes consumer code, shell hooks or prompts. Manifests do
not accept secrets. Network freshness, production runtime behavior and host
parity require their own evidence receipt. Deferred items remain in the
evolution map and are not silently enabled by this slice.
