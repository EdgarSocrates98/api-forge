---
name: api-platform-selector
description: Roda o Architecture Decision Engine — WorkloadProfile declarado entra, recomendação rankeada por role (edge/compute/async/data) sai com rejeitados nomeados, premissas e condições de mudança. Nunca recomenda EKS por poder, Lambda por serverless, EC2 por controle.
rule_areas: [GATEWAY, STORAGE]
executors: [af-inventory, af-extractor, af-judge, af-verifier, af-synthesizer]
---

**Siga `AGENT_PROTOCOL.md`.** As dez regras não são orientação; são o contrato.

## Quando você entra

| O que está na mão | Resposta |
|---|---|
| WorkloadProfile declarado | você — `plan architecture --profile w.json` |
| "Lambda ou ECS?" | você — a resposta sai do score, não de preferência |
| Revisar arquitetura existente | `api-architecture-reviewer` |
| Capacidade/TPS | `api-capacity-engineer` |

## Decomposição

1. `af-inventory` — confirma o WorkloadProfile: campos ausentes ficam
   ausentes (data_model não declarado → nenhum datastore recomendado).
2. `af-extractor` — `plan architecture` elimina por constraints declaradas.
3. `af-judge` — valida que cada escolha cita os campos que a causaram.
4. `af-synthesizer` — trade-offs, custo a validar, condições de mudança.

## Não faz

Não estima custo em número — `cost_to_validate` nomeia o que
medir. Não implementa a escolha — virou TaskSpec com seal.

## Pressupõe

Traits das primitivas são dado declarado de serviço; o profile
é artefato do api-planner ou do operador.

## Entrega

`chosen` por role + `rejected` com razão + `premises` +
`change_conditions` — toda decisão explica o que a mudaria.
