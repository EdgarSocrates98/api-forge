# API Forge — Especificação Arquitetural

**Status:** aprovado para planejamento  
**Data:** 2026-09-21  
**Escopo:** V1 e fundações de evolução

## 1. Visão

API Forge é uma plataforma local-first de engenharia de APIs, operada por engine, CLI e MCP. Seu objetivo é funcionar como um time profissional de especialistas capaz de descobrir, especificar, construir, evoluir, modernizar, revisar, testar, proteger, otimizar e operar APIs.

A V1 atende prioritariamente times profissionais. A arquitetura incorpora rastreabilidade, políticas, auditoria, isolamento e controles suficientes para uma evolução futura a contextos altamente governados, sem transformar isso em posicionamento público explícito.

Princípio central:

> Resultado correto, verificável e reproduzível por token consumido.

O produto começa com REST contract-first, OpenAPI 3.1, Java/Spring Boot, Go com `net/http` e Chi, Python/FastAPI, AWS, Terraform e AWS SAM. O modelo canônico não bloqueará AsyncAPI, eventos, GraphQL, gRPC, WebSocket ou outros frameworks.

## 2. Limites e decisões estruturais

- O repositório será independente do Spark Forge AWS.
- Os contratos serão compatíveis com um futuro `forge-kernel`.
- O kernel compartilhado não será extraído antes de as abstrações serem comprovadas nos dois domínios.
- O core não dependerá de um provider de LLM.
- Hosts como Codex, Claude, Cursor, Devin e Copilot poderão fornecer inteligência de modelo.
- Adapters opcionais poderão integrar Bedrock, modelos locais e provedores externos futuramente.
- Alterações serão feitas em sandbox, branch ou worktree; mutações externas e sensíveis exigirão gates.
- A V1 não inclui UI web, GraphQL, gRPC, AsyncAPI, WebSocket, CDK, Pulumi ou deploy autônomo em produção.

## 3. Arquitetura em camadas

1. **Foundation:** schemas, policies, autorização, sandbox, armazenamento local e telemetria.
2. **Evidence Engine:** facts, rules, findings, decisions, proveniência, hashes, cache e recusas nomeadas.
3. **Adapters:** linguagens, frameworks, AWS, Terraform e SAM.
4. **API Domain:** API-IR, contratos, compatibilidade, segurança, testes, performance e observabilidade.
5. **SDD adaptativo:** perfis `quick`, `standard`, `critical` e `migration`.
6. **Orquestração agentic:** coordenadores, especialistas, reviewers, handoffs, budgets e debate seletivo.
7. **Interfaces:** CLI, MCP e projeções para diferentes hosts agentic.

Fluxo principal:

`intenção → discovery → API-IR → SDD → sandbox → validação → aprovação → entrega`

## 4. API Intermediate Representation

O API-IR será a linguagem interna neutra do produto. OpenAPI, código, IaC e runtime são projeções observadas ou geradas, e cada campo mantém proveniência.

Cada operação poderá representar:

- ID estável, método, caminho e operation ID;
- requests, responses, schemas, exemplos e erros;
- autenticação, autorização, scopes e tenancy;
- idempotência, retry, timeout, rate limit e limites de payload;
- classificação dos dados e requisitos de privacidade;
- handler, serviço, persistência, dependências e testes;
- recursos AWS e IaC relacionados;
- métricas, traces, logs, SLI, SLO e ownership;
- versão, lifecycle, depreciação e compatibilidade;
- origem, confiança, hash e data de observação.

Comparações entre contrato, implementação, infraestrutura e runtime produzirão findings verificáveis. Divergências incluem handlers sem contrato, endpoints não implementados, schema incompatível, auth divergente, rota pública indevida, timeout incoerente, drift e breaking changes não registrados.

## 5. Evidence Engine

Pipeline canônico:

`Artifact → Fact → Rule → Finding → Decision → Action → Verification`

Um fact é observação imutável com `fact_id`, tipo, fonte, localização, medidas, atributos, extrator e hash do artefato. Um finding aponta para rules e facts, registra severidade, confiança, impacto, condição de prova/refutação, ação proposta, risco e referências versionadas.

Estados de ausência são explícitos: `unknown`, `unresolved`, `not_observed`, `not_applicable` e `refused`. Nenhuma conclusão poderá ser inferida apenas pela narrativa de um modelo.

Afirmações de performance exigem baseline e benchmark comparável. Aprovações de segurança exigem evidências produzidas por verificações adequadas. O verificador não aceita apenas evidência textual criada pelo implementador.

## 6. SDD adaptativo

Fases canônicas:

`discover → intent → contract → architecture → plan → build → verify → secure → benchmark → ship`

- **Discover:** inventário, baseline, lacunas e evidências existentes.
- **Intent:** problema, usuários, escopo, restrições e sucesso.
- **Contract:** API-IR/OpenAPI, exemplos, erros e compatibilidade.
- **Architecture:** componentes, ADRs, dependências, segurança e operação.
- **Plan:** tarefas, riscos, testes, rollout e rollback.
- **Build:** alterações rastreadas em ambiente isolado.
- **Verify:** testes, contract diff, cobertura e validação funcional.
- **Secure:** threat model, scanners, dependências e policies.
- **Benchmark:** baseline, carga e orçamento de performance.
- **Ship:** evidências, release notes, migração, rollback e handoff.

Perfis:

- `quick`: mudança local sem alteração contratual ou risco relevante;
- `standard`: endpoint, serviço ou evolução compatível;
- `critical`: auth, IAM, rede, dados sensíveis, banco ou produção;
- `migration`: legado, breaking change, runtime, framework ou plataforma.

Fases dispensadas serão registradas como `not_required`, com regra e justificativa. Artefatos serão ligados por hashes, impedindo que uma fase validada seja silenciosamente reutilizada depois de alterações no upstream.

## 7. Especialização e knowledge packs

Cada pack contém metadados de roteamento, procedimento, referências oficiais, compatibilidade, regras determinísticas, recipes, anti-patterns, troubleshooting, checklists, exemplos e evals. Conteúdo sensível à versão registra fonte e data de verificação.

Áreas obrigatórias:

- HTTP/1.1, HTTP/2, HTTP/3, TLS, DNS, proxies, caching e compressão;
- REST, recursos, métodos, status, idempotência, paginação, filtros e batch;
- OpenAPI 3.1, JSON Schema, lint, diff, geração e contract-first;
- SemVer, compatibilidade, versionamento, depreciação e consumer impact;
- Problem Details, taxonomia de erros, correlação e retryability;
- OWASP API Security, OAuth 2.1, OIDC, JWT, mTLS, RBAC, ABAC e scopes;
- timeouts, retry com jitter, circuit breaker, bulkhead, backpressure e load shedding;
- transações, locking, idempotency keys, outbox e consistência;
- latência, throughput, profiling, pools, payload, serialização e cache;
- testes unitários, integração, contrato, property-based, fuzz, mutação, carga e chaos;
- OpenTelemetry, logs estruturados, métricas RED/USE, SLI/SLO e alertas;
- modular monolith, microsserviços, DDD, hexagonal, clean architecture e BFF;
- deploy progressivo, rollback, incidentes, runbooks e postmortems;
- catálogo, ownership, scorecards e lifecycle de APIs.

### Java/Spring Boot

Java moderno, JVM, virtual threads, Spring MVC/WebFlux, validação, Jackson, Security, OAuth/OIDC, JPA/JDBC/R2DBC, transações, pools, Resilience4j, Actuator, Micrometer, OpenTelemetry, Maven/Gradle, JUnit, REST Assured, WireMock, Testcontainers, JMH, JFR, async-profiler e GC.

### Go/Chi

`net/http`, Chi, handlers, middleware, contexts, graceful shutdown, concorrência, race/leak prevention, timeouts, transports, pooling, streaming, `database/sql`, slog, OpenTelemetry, `testing`, `httptest`, fuzzing, race detector, benchmarks, pprof, trace, módulos e builds reproduzíveis.

### Python/FastAPI

Typing, async/sync boundaries, Pydantic, dependency injection, lifecycle, auth, SQLAlchemy, pools, migrations, HTTP clients, pytest, Hypothesis, HTTPX, Testcontainers, Ruff, mypy, Bandit, pip-audit, profiling, Uvicorn/Gunicorn, workers e OpenTelemetry.

### AWS

API Gateway REST/HTTP APIs, Lambda, ECS/Fargate, ALB, IAM, Cognito, WAF, KMS, Secrets Manager, VPC endpoints, PrivateLink, SQS, SNS, EventBridge, Step Functions, DynamoDB, RDS/Aurora, ElastiCache, S3, CloudWatch, X-Ray, ADOT, CloudTrail, Config, quotas, tagging e FinOps.

## 8. Agentes e responsabilidades

O sistema terá poucos papéis estáveis e packs carregados sob demanda:

- **Orchestrator:** intenção, risco, workflow, orçamento e handoffs;
- **Inventory & Evidence:** extração sem mutação;
- **API Architect:** contrato, arquitetura e decisões;
- **Builder:** implementação apenas em sandbox/worktree;
- **Verifier:** tentativa independente de reprovação;
- **Security Reviewer:** obrigatório quando o perfil exigir;
- **Migration Specialist:** legado, runtime, framework e cloud;
- **Release Guardian:** evidências, breaking changes, rollout e rollback.

Especializações acionáveis cobrem design, Java, Go, Python, segurança, testes, performance, AWS serverless, containers/networking, IaC, observabilidade/SRE, modernização, bancos/consistência, governança e developer experience.

Debate multiagente só ocorre em decisões concorrentes relevantes, contradição de evidências, mudança crítica, regressão inexplicada ou migração de alto risco. O resultado é uma decisão estruturada, não um transcript longo.

## 9. Economia de tokens e contexto

Cascata:

1. análise determinística;
2. cache verificado por hash;
3. retrieval mínimo;
4. agente especialista;
5. raciocínio avançado;
6. revisão ou debate apenas quando justificado.

O context funnel reduz o repositório a inventário, candidatos, símbolos/trechos relevantes, evidências desduplicadas e snapshot mínimo. Índices locais de símbolos, rotas, schemas, call graph, dependências, contratos, AWS, IaC e testes têm prioridade; banco vetorial não é dependência obrigatória.

Progressive disclosure possui níveis de metadados, procedimento, referências e documentação extensa. Memória é separada em working, episodic, semantic, procedural, decision e evidence, sempre com origem, escopo, sensibilidade, validade e invalidação.

Perfis: `eco`, `balanced`, `quality`, `strict`, `offline` e `budgeted`. Métricas incluem tokens reais quando fornecidos, bytes de contexto, cache hits, descarte de contexto, cobertura de evidências, retries, escalonamentos, custo por sucesso e findings comprovados. Ausência de contagem produz `tokens_unresolved`.

## 10. Testes, segurança e performance

A verificação cobre contrato, compilação/tipos/lint, unidade, integração, provider/consumer contract, DAST/SAST, dependências, secrets, performance, resiliência, IaC e prontidão operacional.

Segurança cobre autenticação/autorização por operação, BOLA/BFLA, validação, mass assignment, exposição excessiva, SSRF, injection, traversal, abuso, rate limiting, CORS, TLS, JWT, IAM, supply chain, logging seguro, APIs privadas e threat modeling.

Performance acompanha p50/p95/p99, throughput, erros, saturação, CPU, memória, GC, conexões, cold start e custo por requisição. O protocolo exige baseline, hipótese, alteração controlada, benchmark comparável e validação funcional.

O release evidence bundle reúne contract diff, findings, testes, segurança, benchmarks, planos de IaC, proveniência, approvals, rollout e rollback.

## 11. Autonomia e políticas

Classes: `read_only`, `local_reversible`, `sensitive`, `external_mutation`, `destructive` e `irreversible`.

Leitura e análise são automáticas. Alterações reversíveis podem ocorrer em worktree. Secrets, IAM, rede, banco, recursos AWS e deploy exigem gates. Operações destrutivas exigem alvo exato, impacto, dry run quando possível, backup/rollback e confirmação específica. Irreversíveis são bloqueadas por padrão.

Antes de cloud mutation, o sistema resolve identidade efetiva, conta, região, role, ação, recurso, policy, impacto, rollback e aprovação. Ambiguidade gera recusa.

Proteções incluem allowlist, redaction, tratamento de conteúdo não confiável, restrições de rede/filesystem, credenciais temporárias, limites de recursos, auditoria e proibição de alteração contratual silenciosa.

## 12. CLI, MCP e estado

Comandos principais: `init`, `discover`, `analyze`, `model build`, `diff contract`, `judge`, `recommend`, `design`, `test`, `secure`, `benchmark`, `verify`, `release check`, `build endpoint`, `modernize`, `investigate`, `review` e grupo `sdd`.

CLI e MCP usam o mesmo application core. O MCP oferece operações coesas como `discover_project`, `analyze_artifacts`, `build_api_model`, `judge_findings`, `run_sdd_phase`, `plan_change`, `apply_in_sandbox`, `run_verification`, `get_evidence` e `get_next_step`. Paginação e `detail_level` controlam volume.

Estado versionável pequeno em `.apiforge/`: case, API-IR, facts, findings, decisions, handoff e manifesto. Artefatos grandes e sensíveis ficam fora do Git.

## 13. Ferramentas integráveis

- Contratos: Spectral, Redocly, OpenAPI Generator, Swagger tooling e `oasdiff`.
- Testes: Schemathesis, Pact, REST Assured, Testcontainers, pytest, JUnit, k6, Gatling e Locust.
- Segurança: OWASP ZAP, Semgrep, Trivy, Grype, Syft e Gitleaks.
- Qualidade: Sonar, SpotBugs, Checkstyle, Error Prone, golangci-lint, Ruff, mypy e Bandit.
- Performance: JMH, async-profiler, pprof, Pyroscope e k6.
- Observabilidade: OpenTelemetry, Prometheus, Grafana, CloudWatch e X-Ray.
- AWS/IaC: AWS CLI, SAM CLI, Terraform, `cfn-lint` e LocalStack opcional.

Ferramentas são adapters; ausência de uma ferramenta degrada capacidade explicitamente, sem inutilizar o core.

## 14. Evals e critérios de sucesso

Evals cobrem unidade, golden cases, integração, cenários, adversarial, holdout, economia e regressão. Laboratórios equivalentes (`orders-spring`, `orders-go`, `orders-fastapi`) terão variantes corretas e falhas deliberadas.

A V1 precisa descobrir runtime; extrair rotas/schemas/handlers/testes; construir API-IR; comparar contrato/código/IaC; detectar breaking changes; executar SDD; criar endpoint em sandbox; testar; encontrar vulnerabilidades controladas; medir performance; validar Terraform/SAM; produzir evidence bundle; manter paridade CLI/MCP; realizar handoff; e medir consumo sem inventar economia.

## 15. Roadmap

0. Constituição arquitetural, schemas, ADRs, threat model e evals.
1. Núcleo determinístico: facts, rules, findings, state, policy, cache e CLI.
2. API-IR, OpenAPI 3.1, normalização, diff e breaking changes.
3. Vertical slice FastAPI ponta a ponta.
4. Adapters Spring Boot e Go/Chi com equivalência semântica.
5. AWS, Terraform, SAM e release evidence.
6. Registry agentic, MCP, exporters, context funnel, budgets e debates seletivos.
7. Hardening, holdouts, segurança adversarial, supply chain, compatibilidade e preparação do futuro kernel.

Primeiro incremento implementável:

> Dada uma API FastAPI existente e um OpenAPI, descobrir rotas e divergências, construir o API-IR, classificar breaking changes e produzir findings verificáveis pela CLI.

## 16. Invariantes

- Determinístico antes de LLM.
- Evidência antes de conclusão.
- Contrato antes de geração significativa.
- Teste e rollback proporcionais ao risco.
- Builder não aprova sozinho o próprio resultado.
- Nenhum ganho quantitativo sem medição.
- Nenhuma mutação cloud com alvo ou identidade ambíguos.
- Nenhuma fase ignorada silenciosamente.
- Nenhuma economia de tokens inventada.
- Nenhuma abstração compartilhada antes de ser comprovada em mais de um Forge.
