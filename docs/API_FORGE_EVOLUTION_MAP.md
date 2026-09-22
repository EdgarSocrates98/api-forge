# API Forge — mapa de evolução

Este documento substitui a sequência informal de “próximo passo”. Ele é o mapa de
produto, arquitetura e engenharia para transformar o API Forge em uma plataforma
agentica autônoma, verificável e segura para construir, evoluir e operar APIs.

## Estado atual

O núcleo já possui:

- API-IR, facts, findings, provenance, hash cascade e evidências verificáveis;
- TaskSpec selado, supervisor determinístico, sandbox, verificador, holdout e brief;
- debate condicionado por risco/divergência e integração nativa de Caveman/RTK;
- contratos OpenAPI, gRPC, performance, migração e acesso a Redis, Mongo, DynamoDB e Neptune;
- planos e adapters read-only para OTel, Datadog, Dynatrace e CloudWatch;
- safety budgets, paginação bounded, retry bounded, circuit breaker e control plane de eventos;
- exporters opcionais e binding de host com credencial, endpoint allowlist e aprovação explícita;
- agentes especializados para arquitetura, contratos, performance, segurança,
  observabilidade, gRPC, migração, dados, AWS e revisão de tarefas.
- gates versionados de capacidade (`CapacityAssessment`), prontidão de
  exporters (`ObservabilityExportReadiness`), governança de dados
  (`DataAccessReadiness`), segurança/resiliência (`ApiSafetyAssessment`) e
  qualidade/paridade (`AgenticQualityAssessment`), todos com evidência local.
- especializações de dados e mensageria: RDS/Aurora, PostgreSQL/MySQL,
  Kafka/MSK, SQS/SNS/EventBridge/Kinesis, Redis/DynamoDB, OpenSearch/Redshift,
  RabbitMQ/NATS/Pulsar e MongoDB/Neptune.

O estado atual ainda é predominantemente local, offline e com callbacks/adapters
fake ou host-owned. Isso é intencional: a segurança e a reprodutibilidade vêm
antes da ativação de rede ou mutação externa.

## Lacunas principais

### 1. Runtime agentico e governança

- transformar o supervisor em scheduler realmente dinâmico, com paralelismo baseado
  em complexidade, dependências, orçamento e risco;
- persistir leases, retries, checkpoints, cancelamento, retomada e idempotência de runs;
- materializar o revisor de tarefas como gate independente obrigatório antes de `DONE`;
- tornar salas de debate reproduzíveis, com posições, refutações, quorum, referee e decisão;
- medir qualidade de cada agent/subagent: custo, latência, taxa de retrabalho, aceitação e regressão;
- adicionar adapter real de modelos com fallback, roteamento por tarefa e política de dados;
- garantir a mesma semântica em Claude, GPT/Codex, Devin e Copilot, mesmo quando o host
  não oferecer MCP, hooks ou subagents equivalentes.

### 2. Contexto, TokenSave e Graphify

- aplicar o context funnel automaticamente em todas as fases e não apenas em casos manuais;
- conectar fatos, findings, tarefas, testes, traces, decisões, commits e releases no grafo;
- adicionar consultas de impacto para “o que quebra se eu mudar este endpoint/banco/SLO?”;
- consolidar cache por hash, deduplicação, compressão e orçamento por agent;
- criar métricas de economia: tokens poupados, bytes evitados, hits de cache e custo por resultado;
- exportar o grafo para Neptune somente por adapter aprovado, preservando o grafo local como fonte.

### 3. Contratos e design de APIs

- completar OpenAPI design-first com lint, style guides, mock server, examples e contract tests;
- evoluir gRPC para protobuf registry, buf-like lint/breaking checks, codegen real e gateway;
- fechar GraphQL e AsyncAPI com schema diff, compatibilidade, mocks e testes de eventos;
- gerar contratos e skeletons para Java/Spring, Go e Python/FastAPI com compilação real em sandbox;
- padronizar RFC 7807, versionamento, paginação, idempotência e erros como políticas reutilizáveis;
- adicionar compatibilidade semântica: tipos, auth, comportamento, SLO e dependências downstream.

### 4. Construção e evolução de código

- implementar vertical slices completos por linguagem, incluindo testes, documentação e IaC;
- criar modernização segura Java 11→17→21→25, Go nas versões suportadas e Python 2→3/3.8→3.14;
- gerar plano de migração, patches pequenos, build, testes, benchmark, rollback e relatório de risco;
- detectar APIs, bibliotecas, frameworks, runtimes, breaking changes e vulnerabilidades de dependências;
- adicionar revisão independente de diff, mutation check e prova de que o patch atende o contrato;
- manter templates atualizados por matriz de versões e fontes de conhecimento datadas.

### 5. Testes, performance e capacidade

- executar k6, JMeter, Locust, Gatling, Vegeta, wrk e hey somente por runner aprovado;
- separar RPS, TPS de negócio, concorrência, latência, throughput, saturação e erro;
- implementar testes de carga, stress, spike, soak, capacity, failover e degradação controlada;
- validar warmup, steady state, generator saturation, repeat baseline e ruído estatístico;
- derivar capacidade de ECS, EKS, Lambda, EC2, API Gateway, ALB, MSK e bancos;
- gerar recomendações de autoscaling, pool, cache, fila, particionamento e custo com evidência;
- conectar resultados de performance a regressões, SLOs e gates de release.

### 6. Observabilidade operacional

- conectar exporters a clientes HTTP/SDK do host com timeout, retry, rate limit e redaction;
- validar schemas e semantic conventions reais de OTel, Datadog e Dynatrace;
- criar dashboards, alertas e runbooks versionados, mas nunca escrevê-los sem aprovação;
- correlacionar API, gateway, aplicação, banco, cache, Kafka, fila e downstream por trace/correlation id;
- completar SLI/SLO, error budget, burn rate, incident timeline e diagnóstico assistido;
- adicionar replay de fixtures e comparação entre backends para detectar divergência.

### 7. Dados e dependências

- evoluir scans de Redis, Mongo/DocDB, DynamoDB e Neptune para schema, índices, TTL,
  hot keys, query plans, scans, paginação e consistência;
- distinguir fato observado, declaração do usuário e inferência heurística em toda análise;
- adicionar adapters read-only reais com credenciais, timeouts, budgets e fixtures sanitizados;
- gerar recomendações de cache, índices, access patterns, transações e particionamento;
- modelar impacto de alterações de contrato em consumidores, jobs, eventos e dados.

### 8. AWS, infraestrutura e entrega

- completar WorkloadProfile com quotas, limites, regiões, custo, RTO/RPO e dependências;
- gerar Terraform/SAM/CDK apenas em sandbox, com plan, policy check, diff, approval e rollback;
- validar IAM least privilege, VPC, private endpoints, WAF, Secrets Manager, KMS e tagging;
- adicionar drift read-only e reconciliação explícita; nenhuma correção cloud automática por padrão;
- criar pipelines CI para contratos, testes, segurança, performance, evidência e assinatura;
- produzir SBOM, provenance e release bundle compatível com SLSA/integridade do projeto.

### 9. Segurança e confiabilidade

- threat modeling automático por API, dados, identidade, rede e cadeia de ferramentas;
- orquestrar SAST, SCA, DAST, secrets, IaC scan, container scan e dependency advisories;
- testar authn/authz, RBAC/ABAC, mTLS, JWT, OAuth/OIDC, rate limit e tenant isolation;
- adicionar fuzzing de contrato, property tests, mutation tests e testes adversariais dos agents;
- definir redaction universal para logs, traces, payloads, prompts, receipts e exportadores;
- criar chaos plans declarativos com execução separada e aprovação de alto risco.

### 10. Evals, conhecimento e skills

- construir corpus golden/holdout por Java, Go, Python, REST, gRPC, GraphQL, eventos e bancos;
- medir planner, builder, reviewer, verifier, debate e synthesis com mutation score e pass rate;
- adicionar evals de segurança: prompt injection, tool misuse, data exfiltration e scope creep;
- versionar knowledge packs com autoridade, data, runtime matrix, validade e fonte;
- publicar skills portáveis para Claude, GPT/Codex, Devin e Copilot com protocolo comum;
- testar paridade de comandos, contratos, capacidades e evidências entre hosts.

### 11. Produto e experiência

- consolidar CLI, MCP e uma API control-plane estável sobre os mesmos contratos;
- criar TUI/web UI opcional para casos, planos, debates, evidências, grafo e approvals;
- fornecer templates de projeto, onboarding, exemplos de vertical slice e troubleshooting;
- adicionar modo `explain`, `dry-run`, `review`, `approve`, `resume` e `export` consistente;
- manter documentação de arquitetura, limites, threat model, ADRs, skills e compatibilidade sempre atualizada.

## Ordem estratégica

| Fase | Objetivo | Dependências | Critério de saída |
|---|---|---|---|
| A | Integridade do runtime agentico | TaskSpec, verifier, graph, economy | runs retomáveis, reviewer independente e métricas de qualidade |
| B | Contratos e codegen multi-linguagem | API-IR, gRPC, knowledge packs | vertical slices compilam e passam testes em Java, Go e Python |
| C | Testes e capacidade reais | runners, perf IR, evidence | carga/stress/TPS com validade estatística e rollback |
| D | Observabilidade operacional | host bindings, exporters, redaction | OTel/Datadog/Dynatrace com auth, alertas e runbooks aprovados |
| E | Dados e AWS governados | collectors, adapters, policy | Redis/Mongo/Dynamo/Neptune/AWS com read-only e apply gated |
| F | Segurança e resiliência | threat model, scanners, chaos | gates de segurança, fuzz/mutation e falha controlada |
| G | Evals e portabilidade | golden/holdout, host parity | qualidade medida e mesma experiência nos quatro hosts |
| H | Produto/plataforma | CLI, MCP, UI, docs | onboarding reproduzível e operação completa por contratos |

## Regras para não perder direção

1. Cada evolução deve começar por intenção, contrato, arquitetura, plano e risco.
2. Toda tarefa precisa de teste ou prova, owner, rollback e evidência.
3. Toda integração externa deve ser adapter host-owned, approval-gated e desabilitada por padrão.
4. `DONE` exige verificação independente, holdout/mutation quando aplicável e brief sem gaps.
5. Nenhum agent pode substituir fato por inferência silenciosa.
6. Melhorias de custo devem ser medidas por tokens, bytes, tempo e qualidade, não presumidas.
7. O próximo trabalho deve ser escolhido pela matriz de dependências e pelo maior risco,
   não por uma lista linear fixa.

## Ciclo integrado executado

As Fases A–G foram implementadas sequencialmente, cada uma em commit próprio e
sem push intermediário:

1. A — runtime agentico operacional e revisão independente;
2. B — readiness de migração Java/Go/Python;
3. C — capacidade, TPS, SLO e headroom;
4. D — prontidão de observabilidade host-owned;
5. E — governança de acesso a dados;
6. F — gate de segurança e resiliência;
7. G — avaliação agentica e paridade de hosts.

O fechamento H atualiza esta documentação, executa a suíte completa e consolida
o release. Depois, o próximo grande ciclo deve ativar adapters reais em
ambientes aprovados, com runners de carga, schemas de vendor, queries
read-only, Terraform plan e evals multi-linguagem compiláveis.

## Especialização de dados e mensageria concluída

| Ordem | Área | Entrega |
|---|---|---|
| 1 | RDS/Aurora/relacionais | scanner SQL, pool, transação, paginação e collector RDS |
| 2 | Kafka/MSK | `StreamingAccessIR`, tópicos, grupos, roles e sinais de entrega |
| 3 | AWS messaging | `MessagingAccessIR` para SQS, SNS, EventBridge e Kinesis |
| 4 | baixa latência/escala | perfil Redis/Valkey e DynamoDB baseado em facts |
| 5 | analytics | `AnalyticalAccessIR` para OpenSearch e Redshift |
| 6 | brokers | RabbitMQ, NATS e Pulsar no IR de streaming |
| 7 | documento/grafo | perfil MongoDB/DocumentDB e Neptune com boundedness |

Query plans live, consumer lag, throughput, hot keys comprovadas, explain
plans, cluster health, replay, provisionamento e mutações externas ainda
dependem de adapters aprovados.
