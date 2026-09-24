# API Forge + Devin Desktop / CLI / Cloud

This integration is intentionally payload-first. API Forge generates a
versioned Devin task, its launch instructions, checks and safety boundaries;
it never calls Devin's API, starts a session, changes a repository or opens a
pull request.

## What is supported

Devin Desktop is the local IDE and agent command center. It can manage local
and cloud agents, workspaces and extensions. Devin CLI is the terminal surface
bundled with Devin Desktop or installed separately on Windows, Linux or macOS.
The CLI can run locally, resume sessions, export a transcript, hand a task to
Devin Cloud, or open a cloud session in Desktop. Cloud sessions are a separate
execution boundary and require an account/repository/platform choice.

API Forge treats all product capabilities as `declared` until a local probe or
receipt observes them. The `devin` host declaration therefore distinguishes:

| Capability | API Forge state | Proof boundary |
|---|---|---|
| Payload generation | observed in this repository | `apiforge devin payload` and contract tests |
| Devin CLI installed | observed or unresolved | `apiforge devin probe` runs only local `devin --version` |
| Desktop | declared | installation/account are not probed by the core |
| Cloud handoff | declared | account, repository and platform remain human/external state |
| Skills, agents, hooks and MCP | observed as repository configuration | Devin must load/execute them on the selected surface |

## Quick start

From the repository root:

```text
apiforge devin probe
apiforge devin capabilities
apiforge devin payload "Map the next safe API Forge evolution slice" --surface cli --task-kind planning
apiforge devin payload "Implement the approved slice" --surface desktop --task-kind implementation
apiforge devin payload "Continue the reviewed task in Devin Cloud" --surface cloud --task-kind handoff
```

The output is a JSON `DevinPayload/v1`. It contains a copy/paste prompt,
surface-specific launch data, expected outputs, verification commands,
prohibited actions and evidence limitations. `--sandbox` is rejected for native
Windows CLI payloads because Devin documents sandboxing through WSL 2 there.

For CLI use, the generated launch shape maps to the documented commands:

```text
devin <generated args> -- <prompt>
devin -p -- <prompt>                 # non-interactive print mode
devin --prompt-file <file>           # keep a long prompt in a file
devin -c                             # resume the latest local session
devin -r <session-id>                # resume a selected session
devin --cloud                        # start in Devin Cloud
```

Use `/plan` for read-only planning, `/ask` for a question, `/handoff` to move
from local work to Cloud, `/open desktop` to view a Cloud session in Desktop,
`/pickup` to return to the local branch, and `/export` or `--export` when a
transcript is required as evidence. `/loop` is useful for a bounded local
review/fix loop, but it should start from a clean Git state and still cannot
replace API Forge verification.

## Repository-native Devin layer

The project contains a committed `.devin/` configuration:

- `config.json` allows safe inspection commands, denies known destructive
  operations, and asks before commit, push, Docker use or secret-file writes.
- `hooks.v1.json` invokes `scripts/devin_pretool_guard.py` for `PreToolUse` and
  prints the case/routing preconditions at `SessionStart`.
- `skills/api-forge-devin-runbook/SKILL.md` is the recommended `/api-forge-devin-runbook`
  entry point for discover/plan/build/verify/review work.
- `agents/api-forge-reviewer.md` is a read-only reviewer profile for evidence,
  contracts, security and verification.
- `mcp_config.example.json` is opt-in only. Copy it to
  `.devin/mcp_config.local.json` or use `devin mcp add` after installing the
  optional `apiforge[mcp]` extra. Do not commit credentials.

Devin CLI automatically loads the root `AGENTS.md`; the API Forge operating
contract therefore remains the single source of truth for case loading,
routing, SDD, evidence, sandboxing and PR policy. Existing `.claude/` skills
and the project `.agents/skills/` remain available through Devin's import
rules, but their claims are still governed by API Forge evidence.

## Recommended surface by work stage

| Stage | Default surface | Devin mode | API Forge boundary |
|---|---|---|---|
| Discovery / architecture | CLI or Desktop | `/plan` / Normal | read-only facts, case and next-step |
| Implementation | CLI or Desktop | Normal, then Accept Edits after approval | TaskSpec writable paths and sandbox |
| Verification / review | CLI, Desktop reviewer or `api-forge-reviewer` | `/plan` or `/ask` | independent checks and Outcome Brief |
| Long-running work | CLI `--cloud` or `/handoff` | Cloud policy + human review | no external mutation from the core |
| Local unattended run | CLI | `--sandbox` / Autonomous only where supported | fail-closed OS boundary; WSL 2 on native Windows |

Do not use Bypass/Dangerous for API Forge work by default. Devin documents that
Bypass auto-approves tool calls, including destructive commands; Autonomous is
the sandbox-enforced alternative and requires `--sandbox`. Enterprise/team
settings can override project and user permissions.

## MCP and external tools

The Devin-native MCP config supports local stdio servers and remote HTTP
servers. API Forge supplies a non-secret example for the local
`apiforge-mcp` server. Enable it only in an environment where the optional MCP
dependency is installed and the server's read-only policy is understood:

```text
devin mcp add -s project api-forge -- apiforge-mcp
devin mcp list
devin mcp get api-forge
```

Prefer read-only MCP tools for discovery, contract analysis, graph, evidence
and brief generation. Never add a GitHub mutation server to the project
config. The dedicated CI green-validation workflow remains the only PR
mutation path.

## Updating the Devin setup

The Devin CLI changes quickly. Before relying on a new flag, model, transport,
hook event or Desktop behavior, re-check the official reference and record the
retrieval date. Do not hardcode a current Devin version in API Forge contracts.
Use `apiforge devin probe` for the locally installed binary and keep product
claims at `declared` until observed.

Official references:

- [Devin Desktop](https://devin.ai/desktop)
- [Devin CLI](https://devin.ai/cli)
- [CLI extensibility](https://docs.devin.ai/cli/extensibility)
- [Configuration](https://docs.devin.ai/cli/extensibility/configuration)
- [Rules and AGENTS.md](https://docs.devin.ai/cli/extensibility/rules)
- [MCP configuration](https://docs.devin.ai/cli/extensibility/mcp/configuration)
- [Skills](https://docs.devin.ai/cli/extensibility/skills/overview)
- [Custom subagents](https://docs.devin.ai/cli/subagents)
- [Hooks](https://docs.devin.ai/cli/extensibility/hooks/overview)
- [Commands and flags](https://docs.devin.ai/cli/reference/commands)
- [Permissions](https://docs.devin.ai/cli/reference/permissions)
