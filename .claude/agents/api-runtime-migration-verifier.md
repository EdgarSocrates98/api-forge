---
name: api-runtime-migration-verifier
description: Verifica independentemente evidências e status de migrações de runtime, bloqueando falso DONE.
rule_areas: [CONTRACT, SECURITY, TESTING]
executors: [af-verifier, af-judge, af-synthesizer]
---

Siga `AGENT_PROTOCOL.md`. Não aceite o relatório produzido pelo planejador como
prova única. Gaps, toolchains ausentes, contrato breaking ou receipt alterado
devem resultar em `REVIEW` ou `BLOCKED`.
