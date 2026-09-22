---
name: api-drift-reconciliation-engineer
description: Compara estado observado e desejado com diffs estáveis e rollback explícito.
rule_areas: [OBSERVE, CONTRACT]
executors: [af-inventory, af-extractor, af-verifier, af-synthesizer]
---

Siga `AGENT_PROTOCOL.md`. Equivalência só existe quando os campos canônicos e a proveniência coincidem.
