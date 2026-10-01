---
sdd: 1
feature: API_FORGE_AGENTOPS_CONTROL_PLANE_2
phase: architecture
profile: standard
status: done
upstream:
  path: contract.md
  sha256: "338ed019db2e31b6d070414abac09386718e241ab3c903394151a08ddb569b0d"
files:
  - src/apiforge/runtime/control.py
  - src/apiforge/runtime/__init__.py
  - src/apiforge/cli.py
  - tests/runtime/test_control_plane.py
decisions:
  - id: append-only
    decision: persistir run.json e events.jsonl localmente
    rollback: remover ControlPlane sem alterar AgenticRun
  - id: dependency-ready
    decision: supervisor/host decide execução; ControlPlane só expõe steps prontos
    rollback: fixar largura no policy atual
  - id: independent-review
    decision: status completed exige reviewer diferente do executor conceitual
    rollback: manter awaiting_review e bloquear promoção
---

# architecture

`ControlPlane` é uma máquina de estados pura sobre artefatos locais. O scheduler
existente continua responsável pela execução assíncrona; o Control Plane fornece
planejamento, claim, conclusão, falha, cancelamento e revisão auditáveis.
