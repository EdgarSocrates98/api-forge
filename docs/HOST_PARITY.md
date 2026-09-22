# Host parity

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
| Devin | `AGENTS.md`, `.devin/skills` | subagents/hooks depend on Devin runtime |
| Copilot | `AGENTS.md`, `.github/skills` | no parity guarantee for MCP/subagents |

All hosts can use the core CLI after the package is installed in their
workspace environment. “100%” means shared core behavior, not identical host
UI, hooks, MCP lifecycle or subagent orchestration.
