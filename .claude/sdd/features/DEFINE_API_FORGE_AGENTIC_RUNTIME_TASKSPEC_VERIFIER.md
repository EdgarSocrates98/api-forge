# DEFINE: API Forge Agentic Runtime — TaskSpec e Verifier

> Transformar uma intenção de API em uma tarefa selada, executável em sandbox e verificável independentemente, com evidências, holdout/mutation e aprovação explícita.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_AGENTIC_RUNTIME_TASKSPEC_VERIFIER |
| **Date** | 2026-09-22 |
| **Author** | define-agent |
| **Status** | Ready for Design |
| **Clarity Score** | 15/15 |

---

## Problem Statement

O API Forge já possui contratos de tarefa, sandbox, evidências e aprovação, mas ainda não fecha de forma integrada o ciclo intenção → plano → execução → verificação independente → holdout/mutation → brief. Sem esse ciclo, um agente pode produzir um resultado plausível ou um resumo “verde” sem demonstrar que o escopo foi respeitado, que as provas realmente cobrem o risco ou que uma regressão deliberada seria detectada.

O problema afeta desenvolvedores de APIs, operadores de CI e revisores técnicos que precisam de resultados reproduzíveis, auditáveis e seguros sem permitir mutações externas.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Desenvolvedor de APIs | Define e evolui contratos e implementações | Precisa converter uma intenção ampla em plano, testes e provas reproduzíveis |
| Engenheiro de plataforma/CI | Opera automação local e pipelines | Precisa executar tarefas agenticas sem tocar recursos externos ou a árvore principal |
| Revisor técnico | Aceita ou rejeita resultados | Precisa distinguir fatos, execução, evidência, incerteza e aprovação |
| Agente especialista | Produz ou consome etapas do trabalho | Precisa de contratos estáveis para handoff sem conhecer a implementação interna do runtime |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Compilar uma intenção do caso Commerce Orders em `TaskSpec` validado, revisado e selado, sem ampliar o escopo após o seal |
| **MUST** | Gerar `TaskPlan` fechado com passos registrados, inputs, paths, budgets e artefatos esperados |
| **MUST** | Executar somente em sandbox/local/CI, produzindo histórico, status, stdout/stderr sanitizados e artefatos rastreáveis |
| **MUST** | Verificar independentemente contrato, código, testes, claims e evidências, sem confiar no resumo do executor |
| **MUST** | Aplicar holdout/mutation conhecido e bloquear `DONE` quando a regressão não for detectada |
| **MUST** | Exigir aceitação por identidade distinta do executor e produzir brief terminal `DONE`, `REVIEW` ou `BLOCKED` |
| **SHOULD** | Expor o mesmo application core por CLI e MCP, com controle de `detail_level` e sem lógica duplicada |
| **SHOULD** | Manter adaptadores read-only simulados para PostgreSQL/Mongo/Redis e contratos preparados para AWS/DynamoDB/Neptune futuros |
| **COULD** | Registrar interfaces de integração para TokenSave/Graphify sem torná-las dependências do runtime |

---

## Success Criteria

Measurable outcomes:

- [ ] 1 intenção do caso Commerce Orders produz 1 `TaskSpec` versionado, validado, revisado e selado.
- [ ] O plano contém 100% dos passos com verbo registrado, input explícito, path permitido, budget e artefato esperado.
- [ ] 100% das escritas do executor permanecem no sandbox ou diretório de evidências; a árvore principal permanece byte-a-byte inalterada.
- [ ] 100% dos passos executados produzem status persistido e pelo menos uma referência de artefato ou razão nomeada para ausência.
- [ ] O verifier reexecuta pelo menos 4 dimensões do caso: contrato, segurança/autorização, idempotência e paginação/validação.
- [ ] 100% das mutações de holdout definidas para o slice são detectadas; qualquer mutação não detectada resulta em `REVIEW` ou `BLOCKED`.
- [ ] `DONE` só é produzido após aceitação por ator distinto, evidência não vazia e zero gaps obrigatórios.
- [ ] O fluxo passa integralmente em CI sem rede, AWS, banco ou Redis reais.
- [ ] CLI e MCP retornam resultados equivalentes para os casos de uso cobertos pelo slice.
- [ ] `pytest`, `ruff`, `mypy` e o release gate existente permanecem verdes.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Compile intent | A intenção e os artefatos Commerce Orders estão disponíveis | O Intent Compiler é executado | Um `TaskSpec` válido contém outcome, inputs, preconditions, tests, expected proofs, risk e budgets |
| AT-002 | Seal scope | Um `TaskSpec` revisado é alterado após o seal | A alteração é solicitada | Uma nova revisão não selada é criada; a revisão anterior não é reutilizada como selada |
| AT-003 | Plan closure | Um `TaskSpec` selado define escopo fechado | O planner gera o plano | Cada passo possui verbo registrado, input, path permitido, budget e artefato esperado; nenhum passo fora do spec aparece |
| AT-004 | Sandbox boundary | Um plano contém uma operação de escrita local | O executor roda o plano | A escrita ocorre apenas no sandbox; a árvore principal e recursos externos não são tocados |
| AT-005 | Read-only data adapter | O caso declara PostgreSQL/Mongo/Redis | O executor resolve dependências | Apenas doubles/fixtures read-only são usados; tentativa de mutação é recusada com código e unlock nomeados |
| AT-006 | Independent verification | O executor produz um resumo positivo com uma prova incompleta | O verifier recebe spec, plano e artefatos | O verifier reexecuta as provas, ignora o resumo como autoridade e retorna `REVIEW`/`BLOCKED` com gap explícito |
| AT-007 | Contract/security finding | A operação de criação não declara autenticação | O verifier analisa contrato e implementação | O finding cita evidência, rule/capability e não é convertido em `DONE` |
| AT-008 | Idempotency holdout | A proteção de `Idempotency-Key` é removida por mutação | O holdout é executado | Pelo menos uma prova falha e o resultado identifica a mutação não tolerada |
| AT-009 | Pagination holdout | A validação de cursor é removida | O holdout roda contra `GET /v1/orders` | A regressão é detectada ou o resultado é explicitamente `REVIEW`; nunca passa silenciosamente |
| AT-010 | Acceptance separation | O executor conclui com evidências | O mesmo executor tenta aceitar | A aceitação é recusada; outro ator, com evidências nomeadas, pode aceitar |
| AT-011 | Terminal brief | Há execução, verificação e aceitação válida | O brief é renderizado | O status é `DONE`, sem gaps, open items ou human action pendentes |
| AT-012 | Inconclusive result | Uma prova não pode ser reexecutada ou falta evidência | O verifier finaliza | O resultado é `REVIEW` ou `BLOCKED`, com limitação e próximo passo; não há inferência de sucesso |
| AT-013 | CLI/MCP parity | O mesmo TaskSpec é submetido pelas duas superfícies | Os casos de uso são executados | Os contratos, estados e evidências equivalentes são produzidos sem lógica divergente |
| AT-014 | Offline CI | Não há credenciais nem acesso de rede | O vertical slice roda em CI | O caso termina de forma determinística usando apenas fixtures locais |

---

## Out of Scope

Explicitly NOT included in this feature:

- Mutações reais em AWS, Redis, MongoDB, DynamoDB, Neptune ou qualquer banco externo.
- Provisionamento/deploy com Terraform, ECS, EKS, Lambda, MSK, API Gateway ou ambientes efêmeros.
- Stress testing distribuído real, garantia de TPS, benchmark de produção ou tuning operacional.
- Implementações completas de Java e Go; o primeiro caso usa FastAPI, com contratos extensíveis.
- Event-sourcing completo, replay distribuído, self-healing e loops autônomos de reparo.
- Autoaceitação pelo agente executor.
- Catálogo final de todas as skills, modelos, TokenSave e Graphify.
- Conectores de modelo no core determinístico.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Evoluir `TaskSpec`, `TaskPlan`, stores, sandbox, evidence e brief existentes | O design deve preservar compatibilidade e versionar alterações de contrato |
| Technical | Core determinístico não importa SDKs de modelos ou executa código arbitrário do alvo | Intent Compiler e planner devem produzir dados validados; execução usa verbos/allowlist |
| Technical | Escritas são sandbox-scoped e o escopo é fechado no seal | O executor deve recusar path, verbo ou input fora do spec |
| Technical | Fatos ausentes permanecem `unresolved`; claims exigem evidência | O verifier deve distinguir pass, fail, inconclusive e limitação |
| Security | AWS e bancos são somente read-only ou doubles locais | Não há credenciais, mutações ou efeitos externos no slice |
| Process | Aceitação deve ser distinta do executor | O brief `DONE` depende de aprovação e evidências nomeadas |
| Quality | Holdout/mutation precisa falhar quando a prova não cobre a regressão | Testes verdes no caminho feliz não são suficientes |
| Compatibility | CLI e MCP usam o mesmo application core | Nenhuma lógica de negócio pode ser implementada somente em uma superfície |
| CI | Execução deve ser offline e determinística | Fixtures, hashes e resultados precisam ser reproduzíveis |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/contracts/`, `src/apiforge/taskspec/`, `src/apiforge/sandbox/`, `src/apiforge/evidence/`, `src/apiforge/verification/` ou extensão equivalente; `tests/fixtures/orders_agentic/`; `tests/agentic_runtime/` | Estender módulos existentes; criar novo módulo apenas se a fronteira do verifier não couber nos atuais |
| **KB Domains** | `genai`, `testing`, `python`, `terraform` | `genai`: plan-and-execute, state machine, tool rails; `testing`: fixtures, integração e mutation; `python`: contratos e arquitetura; `terraform`: referência futura, sem IaC neste slice |
| **IaC Impact** | None | Não há provisionamento ou alteração de infraestrutura; adaptadores externos são interfaces/doubles read-only |

**Why This Matters:**

- **Location** → preserva a separação entre contratos, execução, evidência e testes.
- **KB Domains** → orienta Design para state machine, tool rails, testes falsificáveis e contratos tipados.
- **IaC Impact** → confirma que cloud mutation e deploy não são pré-requisitos do slice.

---

## Data Contract (if applicable)

> O caso inclui fontes de dados e adaptadores, mas não executa pipeline nem acessa sistemas externos.

### Source Inventory

| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| Commerce Orders fixture | OpenAPI + FastAPI local | Pequeno/sintético | Versionado por commit | API Forge test suite |
| PostgreSQL/Mongo test double | Fonte read-only simulada | Pequeno/controlado | Por execução | Test harness |
| Redis test double | Cache read-only simulado | Pequeno/controlado | Por execução | Test harness |
| AWS/API metadata fixture | JSON local opcional | N/A | Versionado por commit | API Forge test suite |

### Schema Contract

| Field | Type | Constraints | PII? |
|-------|------|-------------|------|
| `tenant_id` | string | Obrigatório; delimita escopo de leitura | Não no fixture |
| `order_id` | string | Obrigatório; identificador estável | Não |
| `status` | enum | `pending`, `confirmed`, `cancelled` | Não |
| `currency` | string | ISO 4217 declarada no contrato | Não |
| `items` | array | Não vazio; quantidade e preço válidos | Não |
| `idempotency_key` | string/header | Obrigatório em criação; replays devem ser deduplicados | Não |
| `cursor` | string | Validado e rejeitado quando malformado | Não |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Fixtures | Mesmo conteúdo durante a execução | Hash do fixture antes/depois |
| Test doubles | Estado isolado por execução | Snapshot/histórico do harness |
| Evidências | Emitidas ao final de cada passo | Timestamp e hash do artefato |

### Completeness Metrics

- 100% dos inputs declarados no TaskSpec resolvem para fixture, artefato ou recusa nomeada.
- 100% dos campos obrigatórios do cenário possuem evidência de contrato ou são marcados `unresolved`.
- 0 conexões externas permitidas no CI do slice.

### Lineage Requirements

- Cada finding deve apontar para artefato/fact/evidence identificável.
- Cada VerificationRecord deve apontar para a revisão do TaskSpec, plano e resultados consumidos.
- Cada brief terminal deve listar as evidências que sustentam o estado.

---

## Assumptions

Assumptions that if wrong could invalidate the design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Os contratos atuais de TaskSpec, revisão, selo e aceitação podem receber campos/versionamento compatíveis | Será necessário um migration layer antes do planner/verifier | [ ] |
| A-002 | O dispatch/sandbox atual consegue registrar artefatos suficientes para verificação independente | Será necessário um evidence adapter adicional | [ ] |
| A-003 | O caso Commerce Orders pode representar banco e Redis com doubles sem perder os riscos de contrato | O sample precisará de um harness mais rico, ainda local | [ ] |
| A-004 | Quatro dimensões — contrato, auth, idempotência e paginação — são suficientes para provar o primeiro verifier | O slice exigirá mais provas ou será explicitamente limitado | [ ] |
| A-005 | A aceitação distinta e o brief atual podem consumir um VerificationRecord sem quebrar estados | Será necessário adaptar a máquina de estados e os consumers | [ ] |
| A-006 | A superfície MCP disponível pode expor o mesmo application core sem dependência externa no CI | MCP ficará como adapter opcional, com paridade testada quando disponível | [ ] |
| A-007 | O holdout pode ser aplicado de forma determinística no sandbox | Mutation testing será isolado em fixture/lab próprio | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Gap e impacto do ciclo não verificável estão explicitamente definidos |
| Users | 3 | Desenvolvedor, plataforma/CI, revisor e agente especialista foram identificados com dores distintas |
| Goals | 3 | Metas priorizadas em MUST/SHOULD/COULD e ancoradas nos contratos existentes |
| Success | 3 | Critérios possuem quantidades, estados, limites e condições testáveis |
| Scope | 3 | Local/CI, read-only, sample, YAGNI e exclusões externas estão definidos |
| **Total** | **15/15** | **PASS — mínimo para prosseguir: 12/15** |

---

## Open Questions

None blocking — ready for Design.

O Design deve resolver, sem ampliar o escopo:

- se o `VerificationRecord` será um novo contrato ou uma extensão de `CapabilityProof`/`AcceptanceRecord`;
- qual executor de mutation será usado no fixture e como seus hashes entram nas evidências;
- como a paridade MCP será testada quando o extra MCP não estiver instalado;
- quais campos de `TaskSpec` exigem bump de versão e compatibilidade de leitura.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-22 | define-agent | Requisitos extraídos e validados de `BRAINSTORM_API_FORGE_AGENTIC_RUNTIME_TASKSPEC_VERIFIER.md`; clarity 15/15 |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_API_FORGE_AGENTIC_RUNTIME_TASKSPEC_VERIFIER.md`
