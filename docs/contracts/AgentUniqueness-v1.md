# AgentUniqueness/v1

`AgentUniqueness/v1` is one row of `agents audit`, the anti-agentic-theater
gate.

| Field | Meaning |
|---|---|
| `agent` | Agent name from `agents/*.md` or the runtime catalog |
| `capabilities` / `decision_roles` | Runtime capabilities and reviewer/critic/referee kinds it owns |
| `rule_areas` / `executors` / `tools` | Declared frontmatter |
| `unique_capability` / `unique_expertise` / `unique_validator` / `unique_tool` / `unique_decision_role` | Owned by no other agent |
| `verdict` | `keep` when any flag is true, else `merge-candidate` |
| `overlaps` | Agents whose rule areas cover a merge candidate |

The audit is report-only; merging or removing agents is a human decision.
