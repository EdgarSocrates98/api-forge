# WasteFinding/v1

§56–§57 one detector hit, labeled by evidence basis.

| Field | Meaning |
|---|---|
| `kind` | Closed `WasteKind` taxonomy (12 kinds) |
| `evidence` | `observed` (ledger proves), `estimated` (derivable), `hypothesis` (shape only) |
| `detail` | What repeated/grew and against which declared threshold |
| `refs` | Ref uris or ledger ids implicated |
| `estimated_tokens` | Optional derived waste estimate; never inferred when no basis |

Invariant: thresholds come from `rules/agentops_waste.yaml`; a finding without
numeric basis still names its evidence label, never a guessed number.
