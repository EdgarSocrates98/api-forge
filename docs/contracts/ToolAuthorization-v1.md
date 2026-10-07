# ToolAuthorization/v1

The recorded decision for one `(subject, tool)` pair under the §13
allowlist-first model.

| Field | Meaning |
|---|---|
| `subject` / `tool` | The evaluated pair |
| `decision` | `allow` or `deny` |
| `risk_classes` | The tool's declared risk profile at decision time |
| `code` / `field` / `unlock` | `AF-TOOL-*` refusal triad; `None` when allowed |
| `reason` | Human-readable justification |

Denials are first-class output, never silent exceptions — every `deny` carries
a cataloged code so the caller can project a safe unlock.

Runtime authorization separates the adapter boundary from requested tools:
the boundary uses the orchestrator's single `agent-invocation` grant, while
`AgentRequest.authority_subject` selects the effective role for every named
tool. `delegated_from` and `delegated_scope` are checked against declared
delegation edges before a tool is allowed. MCP dynamic dispatch applies the
same decision to the resolved target after the gateway gate; registry misses
remain `AF-MCP-TOOL-UNKNOWN`.
