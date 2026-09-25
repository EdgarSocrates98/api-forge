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
| GPT/Codex | `AGENTS.md`, `.agents/skills`, `.agents/agents` | native `.codex` hooks are host-managed |
| Devin | `AGENTS.md`, `.devin/` | payloads are local; Desktop/CLI/Cloud/subagents/hooks depend on Devin runtime |
| Copilot | `AGENTS.md`, `.github/skills` | no parity guarantee for MCP/subagents |

All hosts can use the core CLI after the package is installed in a user-owned
environment. “Shared core” means local package behavior, not identical host
UI, hooks, MCP lifecycle or subagent orchestration. A host is never a
prerequisite for `inspect`, `init`, `status`, `doctor` or context resolution.

Capability negotiation is available through `apiforge agentops negotiate`.
Host-owned declarations may be placed under `.apiforge/hosts/*.json`; absent
declarations use the conservative static layout and retain host limitations.
The resolver publishes intersections only, never host equivalence.

The installed package owns host templates. Generated adapters are small,
hash-labelled and preview-only. A conflict is surfaced as `AF-HOST-CONFLICT`;
automatic synchronization, overwrite and symlink modes are intentionally not
enabled.

For Devin-specific work, use `apiforge devin payload`, `apiforge devin probe`
and `apiforge devin capabilities`. The payload adapter keeps product claims at
`declared` until a local executable or repository artifact is observed. See
[API Forge + Devin](integrations/API_FORGE_DEVIN.md) for Desktop/CLI/Cloud
launch shapes, MCP, skills, hooks, permissions and handoff boundaries.
