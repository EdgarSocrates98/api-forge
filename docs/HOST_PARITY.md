# Host parity

[Português (Brasil)](HOST_PARITY.pt-BR.md) · [Portable distribution in English](guides/API_FORGE_PORTABLE_DISTRIBUTION.md) · [Distribuição portátil em português](guides/API_FORGE_PORTABLE_DISTRIBUTION.pt-BR.md)

API Forge has one Python core and host-specific discovery mirrors. Run:

```text
apiforge agentops parity
```

The audit checks the repository layout; it does not claim that a host supports
features it does not expose.

| Host | Repository entrypoints | Current boundary |
| --- | --- | --- |
| Claude Code | `CLAUDE.md`, `.claude/skills`, `.claude/agents` | hooks/MCP depend on Claude installation |
| GPT/Codex | `AGENTS.md`, `.agents/skills`, `.codex/agents` | native `.codex` hooks are host-managed |
| Devin | `AGENTS.md`, `.devin/`, `.agents/agents` | payloads are local; Desktop/CLI/Cloud/subagents/hooks depend on Devin runtime |
| Copilot | `AGENTS.md`, `.github/skills` | no parity guarantee for MCP/subagents |

All hosts can use the core CLI after the package is installed in a user-owned
environment. “Shared core” means local package behavior, not identical host
UI, hooks, MCP lifecycle or subagent orchestration. A host is never a
prerequisite for `inspect`, `init`, `status`, `doctor` or context resolution.

Capability negotiation is available through `apiforge agentops negotiate`.
Host-owned declarations may be placed under `.apiforge/hosts/*.json`; absent
declarations use the conservative static layout and retain host limitations.
The resolver publishes intersections only, never host equivalence.

Tool surface per host is declared in `rules/host_projections.yaml`:
`apiforge agentops projection --host <host>` shows it and
`apiforge-mcp --surface compact` (or `--host claude`) publishes six gateway
tools instead of the full list; every full tool stays reachable through
`apiforge_call`. `apiforge mcp surface` measures the bytes of each surface.

The installed package owns host templates. Generated adapters are small,
hash-labelled and preview-only. A conflict is surfaced as `AF-HOST-CONFLICT`;
automatic synchronization, overwrite and symlink modes are intentionally not
enabled.

For Devin-specific work, use `apiforge devin payload`, `apiforge devin probe`
and `apiforge devin capabilities`. The payload adapter keeps product claims at
`declared` until a local executable or repository artifact is observed. See
[API Forge + Devin](integrations/API_FORGE_DEVIN.md) for Desktop/CLI/Cloud
launch shapes, MCP, skills, hooks, permissions and handoff boundaries.

## Opening a host session

`apiforge ai` is the host-open flow: it observes each host binary
(`claude`, `devin`, `codex`, `copilot`), reads its version, checks the
official authentication status subcommand (the receipt carries only the
`logged_in` boolean, never credential paths), and reads the install
integration state — ledger health plus the managed `.mcp.json` key.

Use it after `apiforge install`, or when a host session does not see the
MCP server. `apiforge ai` measures all four hosts; `apiforge ai <host>`
measures one and prints the `launch_command` the operator runs to open a
session in the repo. `apiforge ai <host> --launch` opens the binary here —
a human boundary: one host only, TTY required, a logged-out host is never
launched (the receipt names the official login command instead).
