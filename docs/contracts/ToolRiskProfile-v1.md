# ToolRiskProfile/v1

Declared risk classification for one callable tool, sourced from
`rules/tool_risk.yaml` (step11 §13).

| Field | Meaning |
|---|---|
| `tool` | Tool name as invoked by the orchestrator |
| `risk_classes` | Non-empty closed set: `read_only`, `write`, `destructive`, `reversible`, `external_side_effect`, `financial_impact`, `security_impact`, `production_impact` |
| `reversible` | Whether its effects can be undone locally |
| `notes` | Free-text caveat (e.g. gitleaks output may contain secret material) |

Invariant: a profile without at least one `risk_class` is a validation error —
an unclassified tool is denied as `AF-TOOL-PROFILE-MISSING` at authorize time.
