# DEFINE: API Forge Runtime Migration Control Plane

> Control plane agentico para analisar, planejar, executar em sandbox e verificar migrações de runtime de APIs e serviços.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_RUNTIME_MIGRATION_CONTROL_PLANE |
| **Date** | 2026-09-22 |
| **Author** | API Forge / define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 15/15 |

## Problem Statement

Equipes que precisam atualizar runtimes de APIs existentes não possuem uma forma única, auditável e segura de descobrir impactos em código, dependências, contratos, bancos, cloud, CI/CD e performance. O API Forge deve transformar uma intenção de migração em um plano verificável e executável apenas em sandbox, evitando falso sucesso e mudanças externas não aprovadas.

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Engenheiro de software | Mantém APIs Java, Go ou Python | Não consegue estimar todo o impacto de um salto de runtime e de dependências. |
| Engenheiro de plataforma/SRE | Opera containers, AWS e observabilidade | Precisa validar imagens, pipelines, capacidade, telemetria e rollback durante a migração. |
| Engenheiro de dados/backend | Mantém APIs que acessam Redis, MongoDB, DynamoDB ou Neptune | Mudanças de SDK, driver, serialização e concorrência podem quebrar integrações silenciosamente. |
| Revisor técnico | Aprova mudanças de alto risco | Precisa de evidências reproduzíveis, limitações explícitas e revisão independente. |

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | Receber uma intenção de migração e produzir `MigrationSpec`, `TaskSpec` selado, plano ordenado e resultado `DONE/REVIEW/BLOCKED`. |
| **MUST** | Cobrir Java 11/17/21/25, Python 2→3 e 3.8–3.14, e Go 1.18–1.27, aceitando saltos não adjacentes. |
| **MUST** | Detectar impactos em código, dependências, build, containers, CI/CD, contratos REST/gRPC, AWS, observabilidade e acesso a dados. |
| **MUST** | Executar mudanças somente em sandbox/worktree autorizado, com rollback e evidências reproduzíveis. |
| **MUST** | Impedir falso `DONE` quando toolchain, testes, contratos ou evidências críticas estiverem ausentes. |
| **SHOULD** | Selecionar agentes dinamicamente, usando paralelismo limitado por dependências, risco, orçamento e recursos. |
| **SHOULD** | Ativar debate entre agentes e revisão independente apenas por risco alto, divergência ou solicitação humana. |
| **SHOULD** | Fornecer fixtures sintéticas e evals para migrações representativas. |
| **COULD** | Adicionar novos runtimes, frameworks e provedores por metadados/adaptadores sem alterar o supervisor. |

## Success Criteria

- [ ] Em 100% das execuções válidas, a intenção gera um `MigrationSpec` e um `TaskSpec` com origem, alvo, escopo, risco e critérios de aceite.
- [ ] A matriz inicial reconhece corretamente as versões Java 11/17/21/25, Python 2/3.8–3.14 e Go 1.18–1.27 nos fixtures oficiais.
- [ ] 100% das mudanças do MVP são aplicadas somente no sandbox/worktree e produzem diff e estratégia de rollback.
- [ ] 100% dos resultados finais incluem comandos, códigos de saída, arquivos afetados, limitações e evidências disponíveis.
- [ ] Nenhum fixture com toolchain ausente ou contrato incompatível recebe `DONE`.
- [ ] Pelo menos 6 fixtures cobrindo Java, Python, Go, cloud/dados, `REVIEW` e `BLOCKED` passam nos evals.
- [ ] O verificador independente detecta pelo menos 95% das mutações intencionais introduzidas nos fixtures de migração.
- [ ] Tarefas independentes podem executar em paralelo sem violar dependências, limites de risco ou orçamento configurados.
- [ ] A documentação do resultado permite reproduzir a decisão localmente ou no CI sem acesso de mutação a AWS/bancos reais.

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Java 11→21 | Projeto Spring/Maven com contrato REST, dependências e testes | Usuário solicita a migração | O sistema detecta contexto, gera tarefas, propõe patches em sandbox e coleta build/testes. |
| AT-002 | Python 2→3 | Projeto com sintaxe legada e dependência incompatível | A migração é planejada | O relatório lista incompatibilidades, classifica risco e não declara `DONE` sem correções e testes. |
| AT-003 | Go 1.21→1.24 | Projeto com `go.mod`, concorrência e uso de stdlib | A análise é executada | O sistema verifica toolchain, dependências, race/tests e aponta mudanças relevantes com evidências. |
| AT-004 | Toolchain indisponível | Versão-alvo não está instalada e não há adapter remoto mutável | O plano é executado | O resultado é `REVIEW` ou `BLOCKED`, com pré-condição ausente e sem inventar sucesso. |
| AT-005 | Contrato incompatível | Mudança afeta OpenAPI ou gRPC de forma breaking | O verificador revisa o diff | O resultado não pode ser `DONE`; deve exigir revisão/gate e registrar operações afetadas. |
| AT-006 | Acesso a dados | Serviço usa Redis, MongoDB, DynamoDB ou Neptune | A migração é analisada | Drivers, SDKs, serialização, pooling, TLS e retries aparecem no impacto ou são marcados como não verificáveis. |
| AT-007 | AWS/IaC read-only | Serviço possui Docker/Terraform/ECS/EKS/Lambda | A análise de plataforma é executada | O sistema inspeciona referências e produz achados sem aplicar mutações externas. |
| AT-008 | Alto risco e divergência | Dois agentes discordam sobre compatibilidade crítica | O supervisor agrega resultados | Debate/revisão independente é acionado e a decisão final inclui as posições e evidências. |
| AT-009 | Rollback | Patch de migração falha em testes | A execução é encerrada | O worktree pode retornar ao estado anterior e a evidência da falha fica registrada. |
| AT-010 | Holdout/mutation | O fixture contém um problema intencional não visto pelo planejador | O verificador roda | A mutação é detectada ou o caso falha no eval; não pode ser mascarado como sucesso. |

## Out of Scope

- Deploy automático, merge, push ou alteração em AWS, CI/CD ou bancos reais.
- Migração de dados/schema executável e alterações destrutivas em Redis, MongoDB, DynamoDB ou Neptune.
- Instalação irrestrita de runtimes, JDKs, toolchains ou plugins.
- Transformação binária, garantia formal de equivalência semântica ou tuning automático de produção.
- Cobertura total de todos os frameworks, distribuições Linux e provedores cloud no primeiro corte.
- Aprovação automática de mudanças de alto risco sem revisão humana ou gate definido.

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Safety | Execução apenas local, sandbox/worktree ou CI; adapters externos read-only | O sistema precisa degradar para `REVIEW/BLOCKED` quando não houver evidência. |
| Architecture | Um control plane agnóstico de linguagem | Regras de versão devem ficar em adapters/metadados, não no supervisor. |
| Runtime | Java 11/17/21/25; Python 2→3 e 3.8–3.14; Go 1.18–1.27 | A matriz precisa aceitar origem/alvo, saltos intermediários e versões não instaladas. |
| Agentic | Paralelismo dinâmico com limite por dependência, risco, orçamento e recursos | O scheduler não pode criar trabalho ilimitado nem executar tarefas conflitantes. |
| Governance | Debate somente em alto risco, divergência ou solicitação humana; revisão independente nos gates críticos | O decisor não pode revisar a própria decisão sem um segundo papel/verificador. |
| Evidence | `DONE` exige evidência suficiente e reprodutível | Ausências, falhas e suposições devem aparecer explicitamente no relatório. |
| Compatibility | Deve reutilizar TaskSpec, sandbox, verificação, observabilidade, Graphify e contratos existentes | Evita duplicação e mantém o comportamento consistente com o Runtime Agentic 2.0. |
| Infrastructure | Nenhuma nova infraestrutura é obrigatória no MVP | Cloud, bancos e vendors são inspecionados por adapters read-only e fixtures locais. |

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/migration/`, `src/apiforge/contracts/`, `knowledge/`, `agents/`, `tests/fixtures/migrations/`, `tests/` | Criar o domínio de migração sem duplicar runtime/sandbox; reutilizar contratos e serviços existentes. |
| **KB Domains** | `genai`, `python`, `testing`, `terraform`, `aws`, `streaming`, `data-quality`, `pydantic`; packs do projeto `knowledge/versioning`, `knowledge/observability`, `knowledge/contract-testing`, `knowledge/spring-boot` | `genai` orienta supervisor/gates; testing/evidence validam execução; aws/terraform/platform e packs existentes cobrem impacto operacional. |
| **IaC Impact** | None for MVP; future adapters only | Não provisionar recursos. Terraform, ECS, EKS, Lambda, EC2 e observabilidade entram como análise read-only e fixtures. |

## Data Contract (if applicable)

Não é uma pipeline de dados. A feature possui contexto de dependências e acesso a dados, mas não cria ou transforma datasets. Impactos em Redis, MongoDB, DynamoDB e Neptune serão tratados como dependências/integrações técnicas, com inspeção read-only e sem contrato de volume/freshness no MVP.

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | O runtime, framework e build tool podem ser identificados por arquivos, manifests ou configuração declarada. | O sistema precisará retornar `REVIEW/BLOCKED` e pedir contexto adicional. | [ ] |
| A-002 | Adapters de toolchain podem executar comandos seguros quando as ferramentas já estiverem disponíveis. | A análise continuará estática/read-only e não poderá confirmar build/testes. | [ ] |
| A-003 | A matriz Java 11/17/21/25, Python 2→3 e 3.8–3.14, e Go 1.18–1.27 é suficiente para o primeiro ciclo. | Será necessário adicionar metadados sem mudar o contrato central. | [ ] |
| A-004 | Contratos REST/gRPC e artefatos de observabilidade existentes podem ser consumidos pelos agentes. | A cobertura de compatibilidade ficará limitada e deve ser marcada como não verificada. | [ ] |
| A-005 | Fixtures sintéticas representam os riscos principais até que relatórios/diffs reais sejam fornecidos. | Evals podem apresentar viés e precisarão ser recalibrados com amostras reais. | [ ] |
| A-006 | O supervisor e o verificador são papéis independentes mesmo quando executados pelo mesmo provider físico. | Será necessário impor separação de contexto, prompts e evidências para manter independência. | [ ] |

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Dor, usuário e risco de falso sucesso estão explícitos. |
| Users | 3 | Software, plataforma/SRE, dados/backend e revisão técnica identificados. |
| Goals | 3 | Objetivos MUST/SHOULD/COULD e matriz de versões definidos. |
| Success | 3 | Critérios mensuráveis incluem cobertura, evidência, mutation detection e sandbox. |
| Scope | 3 | MVP e exclusões de mutação externa, deploy, dados e equivalência formal estão claros. |
| **Total** | **15/15** | Pronto para a fase Design. |

## Open Questions

Nenhuma pergunta bloqueadora para iniciar Design. Durante Design, validar a disponibilidade real dos comandos de cada toolchain, a separação de contexto do verificador e os limites exatos de custo/tempo do scheduler.

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-22 | define-agent | Requisitos extraídos do brainstorm aprovado; escopo, critérios, matriz de runtimes e gates definidos. |

## Next Step

**Ready for:** `/ship .claude/sdd/features/DEFINE_API_FORGE_RUNTIME_MIGRATION_CONTROL_PLANE.md`


## Shipment Record

Shipped and archived on 2026-09-22.

