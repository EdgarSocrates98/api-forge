---
name: api-forge-devin-runbook
description: Execute a governed API Forge task through Devin Desktop, CLI or Cloud handoff.
argument-hint: "[objective]"
allowed-tools:
  - read
  - grep
  - glob
---

# API Forge Devin runbook

Use this skill when the user wants Devin to inspect, plan, implement, verify or
review API Forge work.

1. Read `AGENT_PROTOCOL.md` and `AGENTS.md` first.
2. Load or create the persisted case in `.apiforge/case/` before substantive
   analysis. Run `apiforge next-step` before selecting a specialist when the
   case has findings.
3. Keep the route deterministic: `discover -> intent -> contract -> architecture
   -> plan -> build -> verify -> secure -> benchmark -> ship`.
4. Use the project-owned `.agents/skills/` or `.devin/skills/` specialist that
   matches the actual evidence. Do not invent versions, costs, throughput,
   capabilities or production health.
5. Treat Devin Desktop, CLI and Cloud as execution surfaces, not evidence
   sources. A product declaration is not local observation.
6. Never call a provider SDK, publish a PR, force-push, deploy, or mutate an
   external system. The only PR mutation path is the configured green-validation
   CI workflow with its least-privilege credential.
7. Before reporting completion, run focused checks plus independent verification
   and produce an Outcome Brief with unresolved gaps.

Return exactly:

```text
Status:
Outcome:
Human action:
Proof:
Gaps:
Next:
Open:
```

For a Cloud handoff, include the explicit repository, platform, branch and
human approval boundary. For unattended CLI work, use the sandbox only where
the host supports it and keep permissions fail-closed.
