# Design: API Forge Devin Desktop / CLI / Cloud integration

Status: ✅ Complete (Built)

## Components

| Component | Responsibility |
|---|---|
| `contracts/devin.py` | Frozen `DevinPayload/v1`, launch, check and probe contracts |
| `integrations/devin.py` | Prompt/launch builders, local CLI probe and host declaration |
| `cli.py` | JSON CLI projection under `apiforge devin` |
| `.devin/` | Devin-native permissions, hooks, skill, reviewer and MCP example |
| `scripts/devin_pretool_guard.py` | Fail-closed hook for irreversible commands |
| `docs/integrations/API_FORGE_DEVIN.md` | Official surface map and operating guide |

## Flow

```text
objective -> DevinPayload/v1 -> Desktop | CLI | Cloud
                         \-> checks + evidence limits + human boundary
```

The payload adapter is pure apart from the optional local `devin --version`
observation. It does not invoke a provider, execute payload checks or mutate
Git. Product claims stay `declared`; only local observations become `observed`.

## Safety decisions

- Normal mode is the default.
- Commit, push, Docker and secret writes require a Devin permission prompt.
- Destructive cleanup and force-push patterns are denied by the hook.
- Native Windows `--sandbox` is refused; WSL 2 is the documented unlock.
- Cloud handoff is explicit and human-reviewed.
