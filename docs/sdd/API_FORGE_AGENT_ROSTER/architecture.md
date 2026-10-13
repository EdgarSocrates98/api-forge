---
sdd: 1
feature: API_FORGE_AGENT_ROSTER
phase: architecture
profile: critical
status: draft
upstream:
  path: contract.md
  sha256: "be68a2ecf4b3768c0fd63b39252312665f430e790289fb45b918ca87be2408fc"
files:
- src/apiforge/contracts/agents.py
- src/apiforge/dispatch/agent_source.py
- src/apiforge/dispatch/render.py
- src/apiforge/dispatch/mirrors.py
- src/apiforge/dispatch/aliases.py
- src/apiforge/dispatch/references.py
- src/apiforge/evals/agent_routing.py
- src/apiforge/rules/agent_aliases.yaml
- scripts/check_release.py
decisions:
- id: render-not-copy
  decision: mirrors equal render(source, host); one code path writes and checks
  rollback: revert render.py and mirrors.py
- id: uniqueness-by-owned-commands
  decision: agents own real apiforge commands; no new runtime capabilities
  rollback: none needed
- id: aliases-at-ingress
  decision: deprecated names resolve where names enter from data, with a warning
  rollback: set active false
- id: proxy-routing-eval
  decision: deterministic lexical proxy of host routing, baseline captured before rewrite
  rollback: drop the eval
---
# architecture

See `.claude/sdd/features/DESIGN_API_FORGE_AGENT_ROSTER.md`.
