---
name: api-observability-control-plane
description: Coordena descoberta, normalização, análise, planejamento e gates de observabilidade.
rule_areas: [OBSERVE, PERF, SECURITY]
executors: [af-inventory, af-extractor, af-judge, af-verifier, af-synthesizer]
---

Siga `AGENT_PROTOCOL.md`. Preserve OTel como modelo canônico, explicite capabilities e nunca autorize mutação sem policy, aprovação e evidência.
