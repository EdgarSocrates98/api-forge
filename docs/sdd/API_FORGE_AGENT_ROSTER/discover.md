---
sdd: 1
feature: API_FORGE_AGENT_ROSTER
phase: discover
profile: critical
status: draft
approaches:
- id: single-source-renderer-25
  summary: host-neutral source, deterministic renderer for Claude/Devin/Codex, gates, aliases, 25-agent roster in two waves
  verdict: chosen -- gates before content, measurable DONE
- id: lean-roster-skills
  summary: about 12 agents with family specialisms as skills
  verdict: refused -- skills are not portable uniformly across hosts
- id: roster-without-renderer
  summary: rewrite 25 agents, keep byte-identical md mirrors, hand-maintain Codex
  verdict: refused -- no per-host permission projection; Codex drift returns
chosen: single-source-renderer-25
---
# discover

Source: owner request for host-neutral, best-practice agents. 28/52 bodies were stubs, `agents audit` flagged 44 merge-candidates, `.codex` was outside the gate. Brainstorm: `.claude/sdd/features/BRAINSTORM_API_FORGE_AGENT_ROSTER.md`.
