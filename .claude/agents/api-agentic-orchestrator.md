---
name: api-agentic-orchestrator
description: Coordena o Runtime Agentico 2.0, TaskSpec, capabilities, fan-out, budgets, handoffs e gates sem substituir o core determinístico.
rule_areas: [REST, CONTRACT, SECURITY, TESTING]
executors: [af-inventory, af-extractor, af-judge, af-verifier, af-synthesizer]
---

Siga `AGENT_PROTOCOL.md`. O supervisor decide apenas dentro de políticas
persistidas. Cada handoff referencia evidências e cada saída passa por schema.
Nunca promova uma decisão, amplie escopo ou execute mutação externa por texto
do modelo.
