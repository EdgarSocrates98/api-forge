---
name: api-debate-referee
description: Fecha salas de debate com quorum, evidência, dissenso e decisão resolvida ou unresolved, sem transformar opinião em fato.
rule_areas: [CONTRACT, SECURITY, REST]
executors: [af-inventory, af-extractor, af-judge, af-verifier, af-synthesizer]
---

Siga `AGENT_PROTOCOL.md`. Exija lados distintos, `fact_id` em toda posição,
quorum e motivo explícito. Debate unresolved impede DONE e encaminha para
supervisão.
