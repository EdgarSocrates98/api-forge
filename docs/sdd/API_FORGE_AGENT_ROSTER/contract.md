---
sdd: 1
feature: API_FORGE_AGENT_ROSTER
phase: contract
profile: critical
status: draft
upstream:
  path: intent.md
  sha256: "5805dfd4d47e03594a21fdb9b0ae2ffef1c0b922f16952d6e28288492f4d1503"
covers:
- apiforge/agent-lint/v1
- apiforge/agent-routing-eval/v1
- apiforge/agent-routing-cases/v1
- agent frontmatter (access, write_scope, model_tier, apiforge_tools, replaces)
api_ir:
  input: agents/*.md, rules/agent_aliases.yaml, evals/corpus/agent-routing/cases.json
  output: rendered host mirrors, lint report, reference check, routing report
---
# contract

Source frontmatter gains host-neutral keys; `tools` becomes `apiforge_tools` (legacy key still read). Rendered Claude frontmatter uses host `tools`; Codex TOML follows the documented custom-agent format.
