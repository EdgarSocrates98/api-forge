---
sdd: 1
feature: API_FORGE_AGENTOPS_CONTROL_PLANE_2
phase: intent
profile: standard
status: done
upstream:
  path: discover.md
  sha256: "3ef80cc745c13e69c212dec01fa95ce21f3d890d4181efd6c8218981dae93e5b"
problem: >
  O runtime não tinha lifecycle explícito para controlar steps, budgets e
  decisões de revisão de uma execução agentica retomável.
success:
  - persisted-control-run
  - dynamic-ready-width
  - retry-budget-cancel
  - independent-review
  - replayable-events
out_of_scope:
  - execução de provider real
  - mutação externa
  - scheduler distribuído
owner: api-forge-runtime
---

# intent

Adicionar um Control Plane local e determinístico que governe a execução sem
assumir autoridade sobre evidências ou sobre a decisão do Verifier.
