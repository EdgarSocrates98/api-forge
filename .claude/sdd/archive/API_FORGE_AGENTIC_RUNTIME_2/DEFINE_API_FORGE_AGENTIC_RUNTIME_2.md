# DEFINE: API Forge Agentic Runtime 2.0

> Orquestrar a evolução de uma API existente por agentes especializados, com evidência, revisão, debate seletivo e verificação independente.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_AGENTIC_RUNTIME_2 |
| **Date** | 2026-09-22 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 15/15 |

---

## Problem Statement

O API Forge já possui especialistas, TaskSpec, dispatch, debate, sandbox e verificação, mas esses mecanismos ainda não formam um runtime agentico coordenado. Um time de engenharia precisa transformar uma intenção de evolução de API existente em uma trajetória persistida, revisada, segura e verificável, sem depender de um provider de modelo específico ou executar mutações externas.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Time de engenharia | Dono coletivo da evolução da API | Precisa coordenar especialistas, compartilhar contexto e auditar decisões. |
| Engenheiro responsável | Autor da mudança | Precisa receber plano, execução em sandbox, evidências e resultado claro. |
| Revisor técnico | Avaliador independente | Precisa revisar TaskSpec, riscos, provas, holdouts e rollback sem confiar apenas no texto dos agentes. |
| Pipeline CI | Executor não interativo | Precisa de comportamento determinístico, sem rede obrigatória e com estados claros. |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Implementar um supervisor determinístico que coordene intenção, TaskSpec Reviewer, planner, especialistas, critic, debate, referee, sandbox, verifier e brief final. |
| **MUST** | Persistir a trajetória completa — invocações, handoffs, artefatos, decisões, evidências, custos, falhas e estados — com contratos versionados. |
| **MUST** | Executar o primeiro vertical slice com adapter fake determinístico, local/CI, sem mutações externas e com verifier independente, holdout e mutation check. |
| **MUST** | Aplicar gates de risco: crítico adversarial para mudanças de alto risco e aprovação humana para decisões críticas, baixa confiança ou debate não resolvido. |
| **SHOULD** | Suportar fan-out dinâmico de agentes independentes, limitado por orçamento, dependências, timeout, concorrência e política de segurança. |
| **SHOULD** | Suportar provider real opcional por adapter compatível, sem import de SDK de modelo no core. |
| **SHOULD** | Permitir debates automáticos por gatilho e abertura explícita de sala de debate por um membro do time. |
| **COULD** | Preparar adapters futuros para Datadog, Dynatrace, gRPC, AWS, bancos, LangGraph e múltiplos providers. |

---

## Success Criteria

Measurable outcomes:

- [ ] Uma intenção de evolução usando `tests/fixtures/orders_agentic/` produz, em uma execução, um `RunRecord`, TaskSpec, plano, pelo menos uma invocação de agente, artefatos estruturados, decisão e `VerificationRecord`.
- [ ] O fluxo fake executa sem rede e produz resultado semanticamente equivalente em 3 execuções com os mesmos inputs, ignorando timestamps e identificadores de execução.
- [ ] O supervisor consegue despachar pelo menos 3 especialistas independentes em paralelo quando a política permitir e nunca excede o limite de concorrência declarado.
- [ ] 100% das invocações registram agente, capability, modelo/adapter, inputs referenciados, output schema, duração, uso de tokens quando disponível e resultado.
- [ ] Todo artefato aceito contém proveniência, evidências, premissas, riscos e próximo passo; artefato inválido é recusado antes da decisão.
- [ ] O sistema abre debate automaticamente em pelo menos um caso de divergência/alto risco e aceita uma sala aberta explicitamente pelo usuário.
- [ ] Mudanças de alto risco executam o crítico adversarial antes do referee; mudanças de baixo risco não executam crítico sem gatilho.
- [ ] Gates críticos pausam o fluxo com `REVIEW` ou `BLOCKED` até haver aprovação humana registrada; o runtime não promove nem muta recurso externo.
- [ ] Todos os holdouts declarados e todas as mutações do fixture são detectados; qualquer falha impede `DONE`.
- [ ] Falhas de timeout, adapter, schema, ferramenta, orçamento e debate não resolvido produzem estado e código de erro estruturados, sem retry infinito.
- [ ] A execução termina em `DONE`, `REVIEW` ou `BLOCKED` e o brief contém prova, gaps, ação humana e próximo passo.
- [ ] O caminho fake passa no CI sem credenciais, rede, AWS, bancos, Datadog, Dynatrace ou provider de modelo real.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Evolução feliz | Existe uma API fixture, contrato e TaskSpec válido | O usuário inicia o runtime com o adapter fake | O runtime persiste a trajetória completa e termina com brief verificável. |
| AT-002 | TaskSpec inválido | A intenção não possui proof, rollback, escopo ou input existente | O TaskSpec Reviewer analisa a intenção | A execução não começa; o resultado é `REVIEW`/`BLOCKED` com findings acionáveis. |
| AT-003 | Fan-out governado | Há 3 ou mais capabilities independentes e uma política de concorrência | O supervisor planeja a execução | Os agentes independentes executam em paralelo dentro do limite; dependências continuam ordenadas. |
| AT-004 | Output inválido | Um adapter retorna JSON incompleto ou incompatível com o schema | O runtime recebe a resposta | A invocação é registrada como falha e não entra no merge como evidência confiável. |
| AT-005 | Debate automático | Dois especialistas produzem posições conflitantes com facts distintos | O supervisor avalia risco/divergência | Uma Decision Room é criada; posições citam evidências; o referee resolve ou registra `unresolved`. |
| AT-006 | Sala humana | O usuário solicita debate sobre uma decisão | O runtime abre a sala com lados e pergunta | Especialistas podem submeter posições; fechamento exige quorum, evidências e referee. |
| AT-007 | Alto risco | A mudança envolve segurança, dados, contrato breaking, performance ou infraestrutura | O plano chega ao gate de decisão | O crítico adversarial executa antes do referee; ausência de crítica impede decisão final. |
| AT-008 | Gate crítico | Existe promoção, mutação externa, baixa confiança ou debate não resolvido | O runtime chega ao ponto de ação | A execução pausa em `REVIEW`/`AWAITING_SUPERVISION` e exige aprovação registrada. |
| AT-009 | Verificação independente | Executor produz uma mudança aparentemente correta | Verifier, holdout e mutation checks executam | Qualquer discrepância ou mutação não detectada impede `DONE`. |
| AT-010 | Reprodutibilidade | O mesmo caso, policy e adapter fake são executados 3 vezes | O runtime finaliza as execuções | Resultados normalizados são equivalentes e cada trajetória mantém seu próprio receipt. |
| AT-011 | Falha operacional | Agente excede timeout, budget ou retorna erro transitório | O supervisor tenta continuar | O retry é limitado; o estado final e o motivo ficam persistidos como `REVIEW` ou `BLOCKED`. |
| AT-012 | Segurança de ferramentas | Uma ferramenta pede caminho fora do sandbox ou ação externa | O adapter tenta executar a chamada | A policy recusa com código `AF-*`, registra a tentativa e não altera o ambiente. |
| AT-013 | Provider opcional | Um provider real está configurado fora do CI | O adapter real executa uma tarefa permitida | A saída é normalizada para o mesmo contrato do fake, com modelo, custo, latência e falhas registrados. |
| AT-014 | Brief final | A trajetória possui evidências, gaps e estado terminal | O runtime sintetiza o resultado | O brief informa somente `DONE`, `REVIEW` ou `BLOCKED`, com prova e ação humana quando aplicável. |

---

## Out of Scope

Explicitly NOT included in this feature:

- Integração nativa com Datadog ou Dynatrace; o contrato deverá permitir adapters futuros.
- Implementação completa de gRPC, ProtoIR de produção, codegen, streaming e transcoding.
- Execução mutável em AWS, bancos, produção, CI compartilhado ou ambientes externos.
- LangGraph ou outro framework agentico como dependência obrigatória do core.
- Swarm/mesh com delegação irrestrita ou loops autônomos.
- Obrigatoriedade de múltiplos providers reais no CI.
- Deploy, rollout, rollback ou remediação automática em produção.
- UI web; CLI, MCP e artefatos persistidos são suficientes.
- Repositório real anonimizado como requisito de aceite inicial.
- Evals cross-model obrigatórios; o slice terá evals fake/estruturais e deixará o contrato preparado.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | O core não pode importar SDK de modelo. | Adapters devem isolar Claude, GPT e futuros providers. |
| Technical | Estados e transições devem ser explícitos e persistidos. | O supervisor não pode controlar o fluxo somente por texto livre. |
| Technical | Todo output agentico deve validar schema. | Respostas incompletas ou não estruturadas não entram como evidência. |
| Security | Execução local/CI sem mutações externas. | Ferramentas usam allowlist, sandbox, caminhos permitidos e gates. |
| Security | Dados de repositório e telemetria podem conter secrets/PII. | Contexto, logs e artefatos precisam de redaction e minimização. |
| Reliability | Fan-out é dinâmico, mas nunca ilimitado. | Policy deve aplicar budget, timeout, concorrência e cancelamento. |
| Reliability | Falha não pode virar falso sucesso. | `DONE` exige verifier, holdout, mutation e aceitação conforme contrato. |
| Compatibility | Deve funcionar para Claude, GPT, Devin e Copilot. | Interface de adapter e skills não pode exigir um host específico. |
| Resource | CI não deve exigir rede, credenciais ou tokens pagos. | Adapter fake é caminho obrigatório e determinístico. |
| Scope | AWS, bancos, vendors e gRPC ficam para extensões. | Primeiro slice prova o runtime e os contratos de integração. |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/runtime/`, `src/apiforge/contracts/`, `src/apiforge/agents/`, `src/apiforge/evals/`, `agents/`, `.agents/skills/`, `.claude/skills/` | Integrar com `taskspec`, `debate`, `dispatch`, `verification`, `mcp` e `brief` existentes; não duplicar a fonte de verdade. |
| **KB Domains** | `genai`, `testing`, `pydantic`, `python`, `terraform` | Consultar Supervisor/Multi-Agent, State Machines, Tool Calling, Guardrails, Evaluation Framework, schemas e execução segura. |
| **IaC Impact** | None | O primeiro slice é local + CI; AWS e IaC permanecem adapters/read-only futuros. |

**Why This Matters:**

- **Location** → mantém o runtime separado do core determinístico e permite integração explícita por contratos.
- **KB Domains** → orienta o Design para orquestração controlada, outputs estruturados e evals reproduzíveis.
- **IaC Impact** → confirma que não há mutações ou recursos de infraestrutura nesta fase.

---

## Assumptions

Assumptions that if wrong could invalidate the design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | `TaskSpec`, debate, dispatch, sandbox e verification podem ser integrados sem quebrar seus contratos atuais. | Será necessário um layer de compatibilidade ou migração de contratos. | [ ] |
| A-002 | Um adapter fake consegue representar planner, especialistas, crítico e referee com saídas estruturadas determinísticas. | O CI precisará de fixtures de respostas e um executor fake por role. | [ ] |
| A-003 | As fixtures locais cobrem uma evolução representativa de API existente. | Será necessário aumentar fixtures antes do build vertical. | [ ] |
| A-004 | O orçamento de tokens e latência pode ser obtido do adapter real sem depender de um provider específico. | O contrato deverá aceitar `unknown`/`not_observed` e separar medido de estimado. | [ ] |
| A-005 | Os perfis existentes de agents e skills possuem capabilities suficientes para o primeiro fan-out. | Será necessário criar novos perfis antes do runtime. | [x] — catálogo existente confirmado; suficiência ainda será verificada no Design. |
| A-006 | O primeiro slice pode ser validado sem um repositório real anonimizado. | A aceitação precisará esperar a amostra real, reduzindo generalização. | [x] — usuário confirmou fixtures locais como ground truth inicial. |
| A-007 | A policy engine atual pode expressar gates críticos, recusa de mutação e aprovação. | Será necessário estender a policy engine e os contratos de aprovação. | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Problema, usuários afetados e necessidade de coordenação verificável estão explícitos. |
| Users | 3 | Time de engenharia, engenheiro responsável, revisor e CI estão identificados. |
| Goals | 3 | Goals foram priorizados em MUST/SHOULD/COULD. |
| Success | 3 | Critérios têm artefatos, limites, estados e cenários verificáveis. |
| Scope | 3 | Escopo local/CI e itens deferidos estão explicitamente delimitados. |
| **Total** | **15/15** | Pronto para Design. |

**Scoring Guide:**
- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

- Nenhuma pergunta bloqueante para iniciar Design.
- O Design deverá decidir os nomes finais dos contratos de runtime, a política de normalização de timestamps/IDs para replay e a estratégia de integração com os estados atuais do TaskSpec.
- O Design deverá confirmar se os adapters ficam em `src/apiforge/runtime/adapters/` ou em um pacote separado de integração.
- A suficiência dos 20 perfis de agentes para o primeiro fan-out deve ser validada pelo catálogo e pelos evals de routing.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-22 | define-agent | Requirements captured from approved brainstorm; clarity 15/15. |
| 1.1 | 2026-09-22 | ship-agent | Shipped and archived. |

---

## Next Step

**Archived:** `.claude/sdd/archive/API_FORGE_AGENTIC_RUNTIME_2/`
