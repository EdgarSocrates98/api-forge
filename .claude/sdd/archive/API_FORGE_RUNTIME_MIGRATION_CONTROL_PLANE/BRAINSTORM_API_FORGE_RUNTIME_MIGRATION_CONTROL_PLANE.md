# Brainstorm: API Forge Runtime Migration Control Plane

**Status:** ✅ Complete (Defined)  
**Feature ID:** API_FORGE_RUNTIME_MIGRATION_CONTROL_PLANE  
**Data:** 2026-09-22

## 1. Intenção

Tornar o API Forge especialista em analisar, planejar, executar com segurança e verificar migrações de runtime de APIs e serviços existentes. Exemplos: Java 11→17, Java 17→21, Java 11→21, Python 2→3, Python 3.8→3.14 e Go 1.21→1.24.

O recurso deve funcionar como um control plane unificado, agnóstico de linguagem e extensível por metadados/adaptadores. O objetivo do MVP não é apenas alterar o arquivo de versão: é produzir uma decisão migratória verificável, com impacto em código, dependências, build, containers, CI/CD, contratos, cloud, observabilidade, bancos e performance.

## 2. Contexto técnico existente

O projeto já possui fundamentos reutilizáveis:

- Runtime Agentic 2.0, TaskSpec, sandbox/worktree, gates e resultados `DONE/REVIEW/BLOCKED`;
- verificação independente, holdout/mutation checks e coleta de evidências;
- Graphify, observabilidade e controle de contratos REST/gRPC;
- extratores Spring/Java e Go, serviço de build Java e contratos de versionamento;
- knowledge packs de versioning, Spring Boot, Terraform/API, testes, AWS e observabilidade;
- especializações de arquitetura, performance, segurança, dados e acesso a bancos.

O control plane deve compor essas capacidades sem duplicar o supervisor nem criar um agente monolítico por versão.

## 3. Decisões confirmadas

### Abordagem selecionada

**Abordagem A — Runtime Migration Control Plane.**

O núcleo será único e receberá um `MigrationSpec`, produzindo um `TaskSpec` selado, plano executável, mudanças em sandbox, evidências e decisão independente. Packs e adaptadores de linguagem serão detalhes de implementação e conhecimento, não produtos isolados.

### Autonomia e segurança

- execução apenas local/sandbox/CI no MVP;
- nenhum deploy, push, merge ou mutação em AWS/bancos reais;
- adapters externos inicialmente read-only;
- paralelismo dinâmico decidido pelo supervisor, limitado por risco, dependências, orçamento e recursos;
- debates entre agentes somente em alto risco, divergência ou solicitação humana;
- revisor independente obrigatório antes da decisão final em mudanças críticas;
- rollback, evidência e aprovação humana como requisitos de segurança.

### Versões iniciais

| Ecossistema | Matriz inicial |
|---|---|
| Java | 11, 17, 21 e 25 |
| Python | 2→3; Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13 e 3.14 |
| Go | 1.18 até 1.27, com foco operacional em 1.20–1.25 e trilha atual 1.26–1.27 |

A matriz deve aceitar saltos não adjacentes e explicar quando recomenda migração intermediária.

## 4. Fluxo proposto

1. **Discovery Agent:** identifica runtime, versão, framework, build tool, dependências, OS, container, CI/CD, contratos, bancos e integrações.
2. **Compatibility Agent:** constrói origem→destino, detecta APIs removidas/deprecadas, mudanças semânticas e riscos com confiança e evidência.
3. **Dependency Agent:** avalia dependências diretas/transitivas, plugins, SDKs, imagens base e toolchains.
4. **API Contract Agent:** verifica OpenAPI/gRPC, compatibilidade backward/forward, serialização, erros, auth e comportamento HTTP.
5. **Data Access Agent:** analisa Redis, MongoDB, DynamoDB, Neptune, drivers, SDKs, serialização e mudanças de concorrência/pooling.
6. **Cloud Runtime Agent:** verifica Lambda, ECS, EKS, EC2, Docker, Terraform, secrets, IAM, pipelines e observabilidade.
7. **Migration Planner:** converte achados em tarefas independentes, ordenadas por dependências, risco e paralelismo possível.
8. **Patch Executor:** aplica patches controlados somente em sandbox/worktree.
9. **Test/Performance Agents:** executam testes unitários, integração, contrato, smoke, regressão, carga e comparação de baseline quando disponíveis.
10. **Independent Reviewer/Verifier:** procura evidências ausentes, executa holdout/mutation checks e decide `DONE`, `REVIEW` ou `BLOCKED`.

## 5. Modelo conceitual

### MigrationSpec

Deve conter:

- projeto, serviço, linguagem e runtime de origem/alvo;
- framework, build system e package manager;
- restrições de compatibilidade e política de salto;
- contratos HTTP/gRPC/eventos;
- bancos, caches, filas e SDKs;
- container, CI/CD, IaC, cloud e observabilidade;
- baseline de testes/performance;
- nível de autonomia, limites e gates de aprovação.

### TaskSpec de migração

Cada tarefa deve possuir objetivo, entradas, pré-condições, arquivos permitidos, comandos permitidos, risco, dependências, critérios de aceite, evidências obrigatórias, estratégia de rollback e agente responsável. O supervisor poderá particionar tarefas independentes, mas não poderá esconder conflitos ou transformar uma incerteza em sucesso.

### Evidências mínimas

- runtime detectado e versão declarada;
- dependências e toolchain resolvidos ou explicitamente indisponíveis;
- diff aplicado e arquivos afetados;
- saída de build/testes, incluindo comandos e códigos de saída;
- comparação de contratos e comportamento;
- análise de segurança e compatibilidade;
- baseline e resultado de performance quando configurados;
- limitações, suposições e itens não verificados.

## 6. Especializações por ecossistema

### Java

Cobrir Java 11/17/21/25, Maven e Gradle, JDK/JRE, `jdeps`, `jdeprscan`, testes, Spring/Spring Boot, Jakarta migration, bytecode, módulos, reflection, GC, virtual threads quando aplicável, containers, Lambda e imagens base.

### Python

Cobrir Python 2→3 e Python 3.8–3.14, `pip`, Poetry, uv e virtualenv. Detectar sintaxe legada, APIs removidas, dependências sem suporte, mudanças de typing/asyncio, C extensions, wheels, packaging, Docker, testes e frameworks web.

### Go

Cobrir Go 1.18–1.27, Go Modules, toolchain directive, `go mod tidy`, vet, test, race detector, fuzzing, cgo, mudanças de stdlib, generics, comportamento de loops/concurrency, `net/http`, imagens scratch/distroless e cross-compilation.

## 7. Integrações de dados e plataforma

O MVP deve analisar, sem mutar, impacto da migração em:

- Redis: clientes, pooling, timeouts, serialização e TLS;
- MongoDB: drivers, codecs, transações, timeouts e compatibilidade de wire protocol;
- DynamoDB: AWS SDK, retries, marshalling, async clients e configuração regional;
- Neptune: drivers Gremlin/SPARQL, TLS, timeouts e pooling;
- Kafka/MSK e eventos quando contratos ou clientes forem afetados;
- ECS, EKS, Lambda, EC2, API Gateway, ALB, WAF, Terraform, Secrets Manager e SSM;
- CloudWatch, X-Ray, OpenTelemetry, Datadog e Dynatrace como superfícies de configuração e evidência.

## 8. Escopo MVP — YAGNI

### Incluído

- análise offline/read-only e execução local/CI;
- matriz Java, Python e Go acima;
- descoberta de dependências e toolchains;
- detecção de breaking changes e recomendações;
- TaskSpec, sandbox, patch controlado e rollback;
- testes/builds disponíveis no ambiente;
- verificação independente, holdout/mutation e brief final;
- fixtures sintéticas para migrações representativas;
- relatório reproduzível com confiança, evidência e limitações.

### Adiado

- deploy automático e mutação de AWS/bancos reais;
- merge/push automático;
- migração de dados ou schema executável;
- instalação irrestrita de JDKs, runtimes e ferramentas;
- transformação binária ou garantia formal de equivalência semântica;
- cobertura total de todos os frameworks e provedores cloud;
- tuning automático de produção e aprovação sem humano em alto risco.

Esses itens permanecem como extensões compatíveis com o mesmo `MigrationSpec`, sem fazer parte do primeiro corte.

## 9. Amostras e evals

O usuário indicou que possui relatórios de migração, diffs e erros, mas ainda não forneceu caminhos ou um conjunto completo. O inventário inicial deve registrar essa lacuna como `N/A` e criar fixtures sintéticas em:

```text
tests/fixtures/migrations/java/
tests/fixtures/migrations/python/
tests/fixtures/migrations/go/
```

Casos representativos mínimos:

1. Spring/Java 11→21 com dependências e contrato REST;
2. Python 2→3 com sintaxe legada, pacote incompatível e testes quebrados;
3. Go 1.21→1.24 com `go.mod`, mudança de stdlib e teste concorrente;
4. serviço containerizado com Terraform/ECS e Redis/Mongo/DynamoDB;
5. migração que deve resultar em `REVIEW` por toolchain ausente;
6. migração que deve resultar em `BLOCKED` por contrato incompatível.

Evals devem medir detecção, precisão de risco, completude de evidência, segurança do sandbox, correção do status final, qualidade do rollback, economia de tokens e resistência a falso `DONE`.

## 10. Validações incrementais realizadas

### Validação 1 — arquitetura

Foi apresentada uma arquitetura de control plane unificado, com `MigrationSpec`, `TaskSpec`, adaptadores, sandbox, evidências e verificação independente. O usuário confirmou com **Ok**.

### Validação 2 — fluxo e MVP

Foi apresentado o fluxo de dez etapas, agentes especializados, debates condicionais, paralelismo dinâmico e limites YAGNI. O usuário confirmou com **Ok**.

## 11. Abordagens consideradas

- **A — Control plane unificado:** selecionada; maximiza reuso e mantém governança central.
- **B — Packs independentes por par de versão:** útil como camada futura, mas fragmentaria o núcleo.
- **C — Toolchain-first:** útil para evidências, mas não deve ser requisito de funcionamento.

Abordagem A pode incorporar B como metadados e C como adaptadores opcionais sem mudar o contrato central.

## 12. Critérios de sucesso

- uma intenção de migração gera `MigrationSpec` e `TaskSpec` determinísticos e auditáveis;
- o sistema identifica versão, dependências e impactos sem inventar evidência;
- mudanças ocorrem somente no sandbox autorizado;
- testes e verificações são reproduzíveis;
- alto risco ou divergência dispara revisão/debate;
- nenhuma limitação de ambiente é mascarada como sucesso;
- o resultado final é corretamente `DONE`, `REVIEW` ou `BLOCKED`;
- novas versões podem ser adicionadas por metadados/adaptadores;
- os evals demonstram economia de tokens sem reduzir cobertura crítica.

## 13. Próximo passo

Executar:

```text
/define .claude/sdd/features/DEFINE_API_FORGE_RUNTIME_MIGRATION_CONTROL_PLANE.md
```


## Shipment Record

Shipped and archived on 2026-09-22.

