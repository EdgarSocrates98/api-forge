# API Forge — Priority Execution Roadmap

Idioma: [English](API_FORGE_PRIORITY_EXECUTION_ROADMAP.en.md) · [Português (Brasil)](API_FORGE_PRIORITY_EXECUTION_ROADMAP.md)

## Objective

Evoluir o API Forge de um control plane determinístico local-first para uma
plataforma agentica capaz de analisar, executar, verificar e operar mudanças
de APIs com evidência reproduzível.

## Ordem de execução

1. Profundidade dos adapters
2. Execução real em sandbox
3. Verificação independente
4. Evals com corpus real
5. Runtime durável
6. Integrações operacionais com AWS, bancos, brokers e observabilidade
7. Produto unificado

## Gate transversal

Todo adapter precisa declarar um `AdapterExecution` com:

- modo: `static`, `fixture`, `live_read_only` ou `live_mutation`;
- status: concluído, parcial, bloqueado, falho ou inconclusivo;
- nível de evidência: observado, declarado, inferido, heurístico ou verificado;
- hashes das entradas;
- ferramentas e versões utilizadas;
- evidências produzidas;
- limitações e unresolved.

Capacidade declarada não é prova de execução. `live_mutation` nunca autoriza
mutação por si só; aprovação e evidência de policy continuam obrigatórias.

## Critérios de avanço

Uma especialização só avança para integração real quando possui:

1. contrato fechado e versionado;
2. golden corpus e mutation cases;
3. teste de falso positivo e falso negativo conhecido;
4. adapter fake determinístico;
5. adapter real read-only opcional;
6. verificador independente;
7. evidência e limitações expostas no receipt;
8. documentação de rollback e recusa.

## Estado atual desta execução

- **Adapters:** envelope `AdapterExecution` integrado ao inventário e aos
  adapters relacional, streaming, mensageria, analítico e FastAPI; sinais
  dinâmicos permanecem `unresolved`.
- **Execução:** comandos allowlisted e shell-free disponíveis no sandbox, com
  evidência limitada e isolamento forte delegado ao host.
- **Verificação:** verificador independente para adapters e resultados de
  sandbox; mutações continuam falhando ou bloqueadas sem policy.
- **Evals:** corpus inicial baseado nos fixtures FastAPI/Spring e casos de
  runtime, gRPC e observabilidade.
- **Runtime:** control plane persistente com lease, heartbeat e recuperação de
  steps expirados.
- **Integrações:** boundary read-only host-owned para bancos, brokers e
  providers; SDKs/credenciais continuam fora do core.
- **Produto:** fachada `ApiForgePlatform` compartilhada por CLI/MCP em
  descoberta/análise.

### Onda adaptive routing concluída

- Onda 1: `RoutingPlan/v1` com papéis explícitos, fallback bounded e replay.
- Onda 2: scorecards multidimensionais, frescor e gate adversarial opcional.
- Onda 3: expertise packs locais, famílias e múltiplas implementações.

Cada onda foi verificada e commitada separadamente. O funcionamento permanece
hostless, offline-first e sem atualização remota ou sobrescrita automática.

O fechamento de cada item exige adapter real, ambiente autorizado e evidência
correspondente. Sem isso, o resultado permanece `REVIEW` ou `BLOCKED`.

## Vertical slice prioritário

Evoluir uma API existente com REST, RDS, Redis, Kafka/MSK e OpenTelemetry:

```text
discover → extract → plan → TaskSpec → sandbox → test → load → verify
         → holdout/mutation → receipt → brief DONE/REVIEW/BLOCKED
```

AWS, bancos, brokers e exporters permanecem read-only até que identidade,
escopo, aprovação, impacto e rollback estejam presentes no caso.

## Não objetivos imediatos

- adicionar mais providers sem medir qualidade dos existentes;
- declarar suporte de produção apenas porque um token foi detectado;
- executar mutações cloud fora de adapters aprovados;
- usar saída de modelo como evidência sem verificação independente;
- afirmar capacidade de TPS sem experimento reproduzível.
