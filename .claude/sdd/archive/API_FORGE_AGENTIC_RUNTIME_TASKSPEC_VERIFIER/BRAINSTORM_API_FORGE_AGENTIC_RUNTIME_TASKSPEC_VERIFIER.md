# BRAINSTORM: API Forge Agentic Runtime — TaskSpec e Verifier

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_AGENTIC_RUNTIME_TASKSPEC_VERIFIER |
| **Date** | 2026-09-21 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |

---

## Initial Idea

**Raw Input:** `prompt_evo_2026-09-21-api-forge-agentic-engineering-consolidated.md`, com foco confirmado em Runtime agentico + TaskSpec/Verifier: transformar intenção em tarefas verificáveis, com execução segura, evidências, holdout e aprovação.

**Context Gathered:**
- O API Forge já possui `TaskSpec`, revisão, selo Ed25519, receitas, budgets, máquina de estados, sandbox, receipts, aceitação por identidade distinta e brief terminal.
- O fluxo e2e existente cobre descoberta → API-IR → finding → task → sandbox → evidence → brief, mas ainda não fecha a compilação de intenção em plano nem uma verificação independente com holdout/mutation.
- `AGENT_PROTOCOL.md` estabelece deterministic-core, facts sem julgamento, findings com evidência, `unresolved` explícito, sandbox-first, roteamento por dados e registro de verbos/executores.
- O primeiro incremento ficará restrito a local + CI, sem mutações externas; AWS, bancos e Redis serão representados por adaptadores read-only simulados ou fixtures.
- O caso de validação será novo e mais representativo: uma Commerce Orders API multi-tenant com idempotência, paginação por cursor, autorização, banco/cache read-only e falhas deliberadas.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/contracts/`, `src/apiforge/taskspec/`, `src/apiforge/sandbox/`, `src/apiforge/evidence/`, `src/apiforge/verification/` ou extensão equivalente | Evoluir contratos e serviços existentes; não criar runtime paralelo |
| Relevant KB Domains | `genai`, `testing`, `python`, `terraform` | Plan-and-execute/state machine/tool rails; fixtures/mutation; contratos tipados; IaC somente como extensão futura |
| IaC Patterns | Leitores/modelos Terraform, SAM e AWS já existem; mutação externa está fora do slice | Nenhum provisionamento no primeiro incremento; preservar interfaces para futura execução efêmera aprovada |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Qual o objetivo prioritário do primeiro incremento? | Runtime agentico + TaskSpec/Verifier | O recorte é execução verificável, não a plataforma inteira |
| 2 | Qual o limite operacional inicial? | Local + CI, sem mutações externas; AWS/bancos somente read-only | Sandbox e adaptadores determinísticos são obrigatórios; cloud mutation fica fora |
| 3 | Qual o critério de pronto? | Vertical slice: intenção → TaskSpec selado → plano → sandbox → evidências → verificador independente → holdout/mutation → brief | O sucesso é demonstrado por artefatos e estados observáveis, não por narrativa |
| 4 | Quais samples devem ser usados? | Incluir um caso novo e representativo | Criar fixture Commerce Orders API, além dos fixtures existentes |
| 5 | A arquitetura proposta foi validada? | Sim | Planner, executor, verifier, holdout/mutation e acceptance/brief formam o slice |
| 6 | A decomposição em seis componentes foi validada? | Sim | Intent Compiler, Task Planner, Sandbox Executor, Independent Verifier, Holdout/Mutation Gate e Acceptance/Brief entram no design |
| 7 | Qual abordagem arquitetural foi escolhida? | Abordagem A: evoluir contratos existentes | Preservar compatibilidade com CLI, MCP, sandbox, receipts e estados atuais |
| 8 | Os cortes YAGNI foram confirmados? | Sim | Sem cloud mutation, deploy, stress distribuído real, multi-linguagem completa, event-sourcing ou self-healing no slice |

**Minimum Questions:** 3 (satisfied: 8 recorded decisions)

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `tests/fixtures/orders_agentic/` (proposto) | 1 caso, 4 operações | OpenAPI + implementação FastAPI + config de dependências read-only; deve ser criado no Define/Build |
| Output examples | `.apiforge/tasks/<id>/`, `.apiforge/case/`, sandbox manifests, verification record e outcome brief | A definir por execução | Shapes devem reutilizar contratos versionados e receipts existentes |
| Ground truth | Matriz de requisitos do caso Orders + falhas deliberadas | 1 matriz | Verdade conhecida: auth ausente, Problem Details incorreto, cursor sem validação, idempotência removida por mutação |
| Related code | `src/apiforge/contracts/task.py`, `src/apiforge/taskspec/`, `src/apiforge/sandbox/`, `src/apiforge/evidence/`, `tests/taskspec/`, `tests/e2e/test_agentic_slice.py` | 6+ áreas | Reutilizar contratos, persistência, gates, receipts e padrão vertical slice |

**Proposed sample — Commerce Orders API:**

- `POST /v1/orders`: cria pedido, exige `Idempotency-Key`, valida cliente, itens e moeda.
- `GET /v1/orders/{order_id}`: leitura por identificador.
- `GET /v1/orders`: cursor pagination, filtro de status e `tenant_id`.
- `POST /v1/orders/{order_id}/cancel`: transição idempotente de estado.
- OpenAPI + FastAPI inicial; variantes Spring/Go permanecem futuras.
- Adaptadores read-only simulados para PostgreSQL/Mongo e Redis; nenhuma conexão externa real.
- Requisitos futuros de TPS/latência serão declarados como dados do cenário, mas não medidos em ambiente externo neste slice.

**How samples will be used:**

- Compilar a intenção em TaskSpec e verificar se o escopo não foi ampliado.
- Exercitar divergências contrato/código/testes e gerar findings com evidência.
- Verificar autenticação, RFC 9457/Problem Details, idempotência, paginação e tenant boundary.
- Rodar provas do executor e reexecutá-las de forma independente no verifier.
- Aplicar mutações conhecidas e exigir que o holdout seja detectado.
- Produzir fixtures determinísticas para testes unitários, integração, e2e e regressão.

---

## Approaches Explored

### Approach A: Evoluir os contratos e serviços existentes ⭐ Recommended

**Description:** Estender `TaskSpec`, `TaskPlan`, registros de execução e evidências; adicionar Intent Compiler, planner, verifier independente, holdout/mutation e coordenador do vertical slice sobre o fluxo atual.

**Pros:**
- Preserva compatibilidade com CLI, MCP, sandbox, receipts, budgets e estados atuais.
- Reduz duplicação de persistência, autorização e evidência.
- Permite entregar um slice testável antes de habilitar cloud mutation ou múltiplas linguagens.
- Mantém a direção futura para event log/replay sem pagar a complexidade agora.

**Cons:**
- Alguns contratos do MVP precisarão de extensão compatível e migração versionada.
- O verifier precisa de uma fronteira clara para não reutilizar inadvertidamente o resumo do executor.

**Why Recommended:** O codebase já contém os primitives e um e2e parcial; o padrão de `AGENT_PROTOCOL.md` favorece determinismo, evidência e roteamento por dados. A recomendação tem confiança alta, baseada em evidência direta do repositório e nos padrões dos domínios `genai` e `testing`.

---

### Approach B: Criar um Agent Runtime paralelo

**Description:** Construir um kernel novo com eventos, tarefas, estados, evidências e aprovação próprios, mantendo `TaskSpec` atual como legado/adaptador.

**Pros:**
- Modelo conceitual novo e potencialmente mais limpo.
- Liberdade para mudar sem restrições do MVP.

**Cons:**
- Duplica persistência, estados, autorização e evidências.
- Cria risco de dois runtimes divergentes e aumenta a migração.
- Contraria o objetivo de evolução incremental do vertical slice.

---

### Approach C: Event-sourcing desde o início

**Description:** Tratar intenção, plano, passo, evidência, verificação e decisão como eventos imutáveis; derivar estados e briefs por projeções.

**Pros:**
- Auditoria, replay e diagnóstico fortes.
- Boa base futura para execução distribuída e aprendizado operacional.

**Cons:**
- Complexidade desnecessária para provar o primeiro slice local/CI.
- Exige definir versionamento de eventos e projeções antes de validar o contrato funcional.
- Pode ser adicionado posteriormente sobre o histórico append-only existente.

---

## Data Engineering Context (if applicable)

### Source Systems

| Source | Type | Volume Estimate | Current Freshness |
|--------|------|-----------------|-------------------|
| Commerce Orders fixture | OpenAPI + FastAPI local | Pequeno, sintético | Estático/versionado |
| PostgreSQL/Mongo adapter | Read-only test double | Pequeno, controlado | Por execução |
| Redis adapter | Read-only cache test double | Pequeno, controlado | Por execução |
| AWS/API metadata adapters | Fixture ou dump local | N/A no slice | Sem acesso externo |

### Data Flow Sketch

```text
[Intenção + contrato + código]
          → [Intent Compiler]
          → [TaskSpec selado]
          → [Task Planner]
          → [Sandbox Executor]
          → [facts / findings / test records / receipts]
          → [Independent Verifier + Holdout]
          → [Acceptance]
          → [Outcome Brief]
```

### Key Data Questions Explored

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | O runtime pode acessar bancos reais? | Não no primeiro slice | Adaptadores devem ser read-only e determinísticos |
| 2 | O requisito de TPS será medido agora? | Não; apenas declarado como cenário | Stress testing real fica fora do escopo, sem inventar benchmark |
| 3 | O dado deve ser persistido para replay? | Evidências e histórico atuais sim; event-sourcing completo não | Reutilizar store/receipts e preservar futura evolução |

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A — evoluir contratos e serviços existentes |
| **User Confirmation** | 2026-09-21 |
| **Reasoning** | Menor risco e maior aderência aos primitives já entregues: TaskSpec, sandbox, evidence, acceptance e brief. Mantém o core determinístico e permite adiar event-sourcing e mutações externas. |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | O primeiro incremento é um vertical slice local/CI de execução verificável | Prova a fundação do runtime com risco operacional baixo | Plataforma inteira em um único incremento |
| 2 | Evoluir `TaskSpec`/serviços existentes | Evita runtime paralelo e preserva compatibilidade | Agent Runtime novo |
| 3 | Separar executor e verifier por contrato e identidade | Evita que resumo de execução vire prova de correção | Verificação feita pelo mesmo agente |
| 4 | Holdout/mutation é gate de qualidade | Prova que os testes detectam regressões conhecidas | Apenas testes “verdes” do caminho correto |
| 5 | Adaptadores de dados são read-only | Mantém o limite local/CI e prepara bancos futuros | Conexões reais a Redis/Mongo/AWS |
| 6 | CLI e application core são a primeira superfície; MCP preserva paridade | Reutiliza o desenho existente sem lógica duplicada | Runtime específico por interface |
| 7 | TPS, AWS, Java e Go ficam como contratos/extensões futuras | Evita scope explosion sem fechar portas arquiteturais | Implementar todas as especializações agora |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|---------------|----------------|
| Mutações reais em AWS/bancos/Redis/Mongo/DynamoDB/Neptune | Fora do limite local/CI e exige identidade, policy, rollback e aprovação externa | Yes |
| Terraform/ECS/EKS/Lambda/MSK/API Gateway deploy | Não é necessário para provar o runtime verificável | Yes |
| Stress testing distribuído e garantia de TPS | Sem ambiente externo e baseline real, seria uma afirmação não comprovada | Yes |
| Implementações completas Java, Go e Python | O slice precisa de um caso mínimo; contratos serão extensíveis | Yes |
| Event-sourcing completo | Complexidade maior que o benefício do primeiro slice | Yes |
| Self-healing e loops autônomos de reparo | A execução deve primeiro ser verificável e aprovável | Yes |
| Autoaceitação pelo agente | Viola separação entre execução e aprovação | No, salvo política futura explícita |
| Catálogo completo de skills e modelos | Não é pré-requisito para o runtime determinístico | Yes |
| Dependência obrigatória de TokenSave/Graphify | O runtime deve funcionar sem acoplamento de integração | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Architecture concept | ✅ | Confirmado: runtime determinístico com TaskSpec, planner, executor, verifier, holdout e acceptance | No |
| Component breakdown | ✅ | Confirmado: seis componentes do vertical slice | No |
| Sample case | ✅ | Confirmado: incluir caso novo e mais representativo | Sim — Commerce Orders API adicionada com falhas deliberadas |
| Approach comparison | ✅ | Abordagem A confirmada | Sim — event-sourcing e runtime paralelo ficaram futuros |
| YAGNI scope | ✅ | Cortes confirmados; foco local/CI | No |

**Minimum Validations:** 2 (satisfied: 5 checkpoints)

---

## Suggested Requirements for /define

Based on this brainstorm session, the following should be captured in the DEFINE phase:

### Problem Statement (Draft)

O API Forge precisa transformar intenções de evolução de APIs em unidades de trabalho fechadas, executáveis em sandbox e verificáveis independentemente, para que nenhum resultado seja marcado como concluído apenas por narrativa ou pelo resumo do agente executor.

### Target Users (Draft)

| User | Pain Point |
|------|------------|
| Desenvolvedor de APIs | Precisa converter uma intenção ampla em plano seguro, testes e evidência reproduzível |
| Engenheiro de plataforma/CI | Precisa executar tarefas agenticas sem mutação externa e com gates determinísticos |
| Revisor técnico | Precisa distinguir execução, prova, incerteza e aprovação |
| Futuro agente especialista | Precisa consumir e produzir contratos estáveis sem conhecer a implementação interna do runtime |

### Success Criteria (Draft)

- [ ] Uma intenção sobre o caso Commerce Orders gera um `TaskSpec` versionado, validado, revisado e selado.
- [ ] O planner produz um `TaskPlan` fechado, com verbos registrados, inputs, paths, budgets e artefatos esperados.
- [ ] O executor roda somente em sandbox/local, sem tocar a árvore principal nem recursos externos.
- [ ] Cada passo produz status e artefatos persistidos, com facts/findings e receipts rastreáveis.
- [ ] O verifier reexecuta provas sem confiar no resumo do executor e produz um `VerificationRecord` com resultado, evidências, limitações e gaps.
- [ ] O holdout/mutation que remove auth ou idempotência é detectado; caso contrário o terminal é `REVIEW` ou `BLOCKED`, nunca `DONE`.
- [ ] A aceitação exige identidade distinta do executor e evidências nomeadas.
- [ ] O brief final deriva corretamente `DONE`, `REVIEW` ou `BLOCKED` sem permitir conclusão com gaps obrigatórios.
- [ ] CLI e MCP expõem os mesmos casos de uso e controles de detalhe, sem duplicar lógica de negócio.
- [ ] O caso é determinístico e reproduzível em CI sem AWS, banco ou Redis reais.

### Constraints Identified

- Não executar mutações externas no primeiro incremento.
- Não importar SDK de modelo no core determinístico.
- Não inferir fatos ausentes; registrar `unresolved` e recusas nomeadas.
- Não permitir expansão de escopo depois do seal.
- Não aceitar `DONE` por teste verde isolado, resumo do executor ou aprovação do próprio executor.
- Não afirmar TPS, economia de tokens ou performance sem baseline e evidência correspondente.
- Preservar compatibilidade com os contratos e artefatos existentes.

### Out of Scope (Confirmed)

- AWS mutation/deploy, Terraform apply e provisionamento efêmero.
- Stress testing distribuído real, validação de TPS em ambiente externo e tuning de produção.
- Implementações completas de Java/Go e conectores reais para Redis, Mongo, DynamoDB e Neptune.
- Event-sourcing completo, self-healing, loops autônomos de reparo e autoaceitação.
- Catálogo final de todas as skills, modelos e integrações TokenSave/Graphify.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 8 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 9 |
| Validations Completed | 5 |
| Duration | Interactive session across 2026-09-21 |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_API_FORGE_AGENTIC_RUNTIME_TASKSPEC_VERIFIER.md`
