# HostProjection/v1

`HostProjection/v1` is `apiforge agentops projection --host H`: the declared
economical projection for a host (`rules/host_projections.yaml`). The core
never branches on host.

| Field | Meaning |
|---|---|
| `host` / `instruction_file` | `claude`, `gpt-codex`, `devin` or `copilot` and its instruction file |
| `mcp_surface` | `full` or `compact` (used by `apiforge-mcp --host`) |
| `output` | `json` or `compact` for CLI payloads |
| `deferred_tools` | The host loads tool schemas on demand, which bounds surface savings |
| `surface_bytes` / `full_surface_bytes` | Measured bytes of the chosen and the full surface |
| `verb_map` | Artifact question → API Forge verb to run before reading files |
| `notes` | Host-specific caveats |
