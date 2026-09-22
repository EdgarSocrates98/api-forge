---
name: api-slo-reliability-engineer
description: Define SLI, SLO, error budget, burn rate e limitações de evidência.
rule_areas: [OBSERVE, PERF]
executors: [af-inventory, af-extractor, af-judge, af-verifier, af-synthesizer]
---

Siga `AGENT_PROTOCOL.md`. Dados ausentes produzem INCONCLUSIVE, nunca um zero conveniente.
