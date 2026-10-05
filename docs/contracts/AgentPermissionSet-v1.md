# AgentPermissionSet/v1

Allowlist-first authorization for one agent role/capability (step11 §13),
sourced from `rules/tool_risk.yaml` under `permissions:`.

| Field | Meaning |
|---|---|
| `subject` | Role or capability the grant applies to |
| `allowed_tools` | Tools the role may invoke |
| `allowed_risk_classes` | Risk classes the role is granted |
| `denied_tools` | Explicit denials; always win over both allowlists |
| `notes` | Free-text rationale |

Default is DENY: `authorize()` requires the tool in `allowed_tools`, not in
`denied_tools`, and every class of its `ToolRiskProfile` inside
`allowed_risk_classes`. Refusals carry `AF-TOOL-*` codes with field + unlock.
