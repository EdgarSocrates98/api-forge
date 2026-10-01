---
name: api-forge-core
description: >-
  Ponto de entrada do API Forge para qualquer trabalho substantivo de
  engenharia de API — análise, planejamento, arquitetura, implementação,
  revisão, testes, segurança, performance, AWS, bancos, mensageria,
  modernização ou operação. Use sempre que a tarefa tocar uma API e ainda não
  estiver claro qual especialista assume, ou quando o pedido cruzar mais de
  uma área (ex. "revise esta API", "o que está errado com este serviço",
  "review this endpoint", "plan this API change"). Define o protocolo comum
  (caso persistido, next-step, fact_id, unresolved) e roteia para a skill
  específica. Não substitui as skills especializadas: assim que a área estiver
  clara, carregue-a.
compatibility: >-
  Skill de projeto neutra de host (Codex, Claude Code, Devin, Copilot). Requer
  o CLI local `apiforge`; não exige LLM, rede nem ferramenta externa.
metadata:
  api-forge-skill: "true"
  version: "1.1"
---

# API Forge — núcleo e roteamento

O API Forge é `deterministic-core + agentic orchestration`: o core extrai,
mede, julga e verifica; o agente coordena, explica e recomenda. Esta skill
garante que todo trabalho comece pelo mesmo protocolo e chegue ao mesmo
especialista, independentemente do modelo ou do host. Divergência entre
modelos nasce quando cada um escolhe a rota por intuição — por isso a rota é
dado, não opinião.

## Protocolo (sempre)

1. Leia `AGENT_PROTOCOL.md` — as regras não chegam ao contexto sozinhas.
   Preserve alterações existentes no working tree.
2. Abra ou crie o caso persistido antes de investigar. Sem caso, o trabalho
   não é retomável em outro host.
   ```text
   apiforge analyze --contract <openapi> --project <dir> --out-dir .apiforge [--framework fastapi|spring|go|auto]
   ```
3. Com findings, deixe o catálogo escolher a rota:
   ```text
   apiforge next-step --findings .apiforge/case/findings.json --phase <discover|intent|contract|architecture|plan|build|verify|secure|benchmark|ship>
   ```
4. Consulte regras pelo CLI, não pela memória nem lendo YAML:
   `apiforge rules list [--area <a>]` e `apiforge rules lookup <rule_id>`.
5. Nenhum número sem `fact_id`, fonte e unidade. Sem fact é hipótese, e
   precisa ser rotulada como hipótese.
6. Mantenha os estados separados: `confirmed`, `unresolved`, `refused`,
   `not_observed`, `inconclusive`. Sempre reporte a contagem de `unresolved`.
7. Confirme o framework detectado antes de citar o formato da API; `auto` é
   heurística.
8. Código gerado passa pelo sandbox (`apiforge sandbox apply`) e só chega ao
   tree via worktree com aprovação registrada.
9. Registre no caso cada verbo usado, o resultado e por que alternativas
   foram descartadas.
10. Ações destrutivas, mutações cloud/banco/Git e mudanças de política sobem
    para aprovação humana; recomende, não execute.

## Roteamento

Escolha a skill mais específica depois do protocolo. Quando `next-step`
nomear um especialista, ele prevalece sobre esta tabela.

| Sinal na tarefa | Skill |
|---|---|
| inventário, rotas, API-IR, "o que esta API expõe" | `api-forge-discovery` |
| OpenAPI, AsyncAPI, GraphQL, protobuf/gRPC, breaking change, versão | `api-forge-contract` |
| escolher plataforma, WorkloadProfile, Lambda/ECS/EKS, ADR, migração de runtime | `api-forge-architecture` |
| PostgreSQL, MySQL, Aurora, Redis, MongoDB, DynamoDB, Neptune, OpenSearch, Redshift | `api-forge-data-access` |
| SQS, SNS, EventBridge (filas e eventos AWS) | `api-forge-messaging` |
| Kafka/MSK, Kinesis, RabbitMQ, NATS, Pulsar (streams e brokers) | `api-forge-streaming` |
| estratégia de testes, segurança, OWASP, resiliência, chaos, "pronto para release?" | `api-forge-verification` |
| carga, stress, TPS, RPS, p95/p99, capacidade, regressão | `api-forge-performance` |
| OTel, logs, métricas, traces, SLO, Datadog, Dynatrace, runbooks | `api-forge-observability` |
| contexto grande, handoff, TokenSave, Graphify, economia de tokens | `api-forge-context` |
| feature nova, SDD, tasks, gates, ship, field validation | `api-forge-sdd` |
| prontidão da plataforma, capability matrix, change-control Git/CI | `api-forge-platform-completion` |

Tarefas multiárea: siga a ordem do loop de fases (`discover → contract →
architecture → plan → build → verify → secure → benchmark → ship`) e carregue
uma skill por vez, em vez de todas de uma vez.

## Fluxo de fases

```text
next-step → collect → extract facts → judge → hypothesis → experiment
  → measure → verify evidence → update case → next-step
```

Uma variável primária por experimento. Sem baseline não há impacto a provar.

## Saída

Toda entrega substantiva termina com o Outcome Brief:

```text
Status:        DONE | REVIEW | DECIDE | BLOCKED
Outcome:       o que mudou ou foi decidido, em uma frase
Human action:  o que precisa de decisão/aprovação humana (ou "none")
Proof:         fact_ids, receipts, comandos e artefatos com hash
Gaps:          unresolved com contagem; nunca omita
Next:          próximo verbo ou especialista
Open:          perguntas que ninguém pode responder com a evidência atual
```

`DONE` com gaps obrigatórios é recusado (`apiforge brief show --task <id>`);
use `REVIEW` ou `BLOCKED` e nomeie o que falta.

Toda recomendação segue `docs/agents/AGENT_OUTPUT_CONTRACT.md`: fatos,
premissas, alternativas com trade-offs, riscos, unresolved, evidence_refs,
verificador e confiança limitada.
