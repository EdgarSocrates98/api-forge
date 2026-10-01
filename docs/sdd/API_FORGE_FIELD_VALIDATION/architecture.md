---
sdd: 1
feature: API_FORGE_FIELD_VALIDATION
phase: architecture
profile: critical
status: draft
upstream:
  path: contract.md
  sha256: "01b082d3bb08ac975b8a49df22cba3503c9bf211da6d2618670c09c0baf94c9c"
files:
- src/apiforge/contracts/field.py
- src/apiforge/field/
- src/apiforge/cli_field.py
- src/apiforge/adapters/http_targets.py
- src/apiforge/workspace/inference/
- src/apiforge/workspace/graph.py
- src/apiforge/workspace/service.py
- src/apiforge/cli_workspace.py
- src/apiforge/mcp/tools.py
decisions:
- id: join-never-collect
  decision: field records project existing ledger/summary/checkpoint; missing source is null plus unresolved
  rollback: delete src/apiforge/field
- id: evidence-derived-contamination
  decision: inference appends a workspace.infer ledger row; baseline records with that row are refused
  rollback: drop the --infer flag
- id: default-graph-unchanged
  decision: build_graph adds inferred edges only when passed; default output is byte-identical
  rollback: revert graph.py
---
# architecture

Track F (field harness) and track S (inference) never import each other; they meet only through the ledger row.
