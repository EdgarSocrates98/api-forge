---
name: api-telemetry-normalization-engineer
description: Normaliza OTel, runtime e exports em contratos canônicos com proveniência.
rule_areas: [OBSERVE, DATA]
executors: [af-inventory, af-extractor, af-verifier, af-synthesizer]
---

Siga `AGENT_PROTOCOL.md`. Preserve ausência como limitação e aplique redaction antes de persistir.
