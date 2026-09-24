# DEFINE: API Forge Agentic Kernel Evolution

> Integrar o runtime agêntico determinístico, suas provas de qualidade e a experiência DX em um fluxo operacional resiliente e compatível.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_AGENTIC_KERNEL_EVOLUTION |
| **Date** | 2026-09-23 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 15/15 |

---

## Problem Statement

Desenvolvedores e equipes de governança não conseguem usar o API Forge como um fluxo único e comprovável porque o `ControlPlane`, o scheduler, o supervisor, o self-healing, as capabilities, os evals e a DX ainda não compartilham uma autoridade operacional integrada. Isso deixa retomada, idempotência, rollback concorrente, qualidade histórica dos agents e estado da execução parcialmente dependentes de caminhos separados.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Desenvolvedor/arquiteto de APIs | Usa o Forge para revisar, evoluir, corrigir ou retomar uma mudança | Precisa conhecer comandos internos demais e não tem uma entrada simples para acompanhar uma execução ou entender por que ela não terminou |
| Equipe de plataforma e governança | Mantém policies, capabilities, agents, evidências e gates | Precisa provar o que cada capability realmente suporta, qual evidência existe, quais riscos permanecem e como o runtime se comporta sob falha |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Tornar o `ControlPlane` a autoridade única para ciclo de vida, dependências, leases, retry, checkpoint, cancelamento, retomada, idempotência e replay de execuções |
| **MUST** | Impedir que self-healing sobrescreva mudanças concorrentes; conflitos devem interromper ou encaminhar a execução com evidência preservada |
| **MUST** | Fazer com que nenhuma execução seja considerada concluída sem policy, evidência, verificação independente e gaps explicitamente tratados |
| **MUST** | Preservar compatibilidade da CLI e dos artefatos existentes, usando contratos versionados e migração explícita quando uma mudança incompatível for inevitável |
| **SHOULD** | Adicionar Agent Capability Profiles, routing por capability e scorecards históricos derivados de evals, sem transformar score em autorização de mutação |
| **SHOULD** | Evoluir evals para cobrir outcome, holdout, mutation, falhas de autonomia, tool-use, segurança e colaboração |
| **SHOULD** | Entregar uma projeção DX incremental com `doctor`, `status`, `review`, `evolve` e `resume`, mantendo a superfície expert disponível |
| **SHOULD** | Aplicar debate, critic e reviewer de forma adaptativa ao risco, divergência de evidência, baixa confiança e necessidade de aprovação |
| **COULD** | Estruturar evidence levels e knowledge packs locais versionados, incluindo freshness e compatibilidade de versão sem inferir validade externa |
| **COULD** | Preparar ports/adapters e host capability negotiation para futuras integrações, sem afirmar paridade onde não houver recibo do host |

**Priority Guide:**

- **MUST** = MVP fails without this (non-negotiable for MVP)
- **SHOULD** = Important, but workaround exists
- **COULD** = Nice-to-have, cut first if needed

---

## Success Criteria

Measurable outcomes (must include numbers):

- [ ] Todas as acceptance tests declaradas para cada fatia implementada passam, incluindo cenários de dependência, lease, retry, checkpoint, cancelamento, resume, idempotência e replay.
- [ ] O rollback self-healing produz zero sobrescritas quando o hash/ownership atual diverge do estado esperado; o resultado é conflito nomeado, com os bytes externos preservados.
- [ ] Uma retomada reutiliza artifacts e etapas já comprovadamente concluídos e não repete invocações protegidas por idempotency key.
- [ ] Cenários de timeout, resposta inválida, budget esgotado, lease expirado, verificação falha, conflito e rollback falha terminam em estado explícito diferente de `DONE` quando a prova obrigatória não existe.
- [ ] Cada fatia publica evals golden, holdout e mutation; qualquer caso obrigatório sem evidência ou com outcome incorreto bloqueia o gate da fatia.
- [ ] Capability routing nunca seleciona uma capability `unsupported` ou sem prerequisites/evidence exigidos; ausência de prova permanece `unresolved`.
- [ ] Os comandos DX adicionados retornam os mesmos estados, gaps, evidências e códigos de recusa que o kernel canônico, sem regras divergentes por superfície.
- [ ] A suíte existente de testes, lint, mypy, SDD check e release gate permanece verde ou registra falhas e unresolved sem mascaramento.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | DAG com dependências | Um TaskSpec selado possui etapas independentes e uma etapa dependente | O runtime inicia a execução | Etapas independentes podem executar dentro do limite; a dependente só é liberada após os pré-requisitos concluírem |
| AT-002 | Lease expirado | Uma etapa está `running` com lease expirado | O control plane executa recuperação | A etapa volta a estado elegível, o evento é persistido e outro worker pode assumir sem duplicar resultado aceito |
| AT-003 | Resume idempotente | Uma execução possui etapas e artifacts concluídos persistidos | O usuário chama `resume` | O runtime reutiliza o que está comprovado, retoma apenas o restante e produz replay equivalente sem repetir invocações protegidas |
| AT-004 | Cancelamento | Uma execução possui etapas pendentes ou em andamento | Um ator autorizado solicita cancelamento | O estado terminal é `cancelled`, etapas não concluídas são marcadas, o ator fica registrado e não há nova execução automática |
| AT-005 | Retry e budget | Uma etapa falha de forma transitória e possui retry permitido | O scheduler tenta novamente até o limite ou budget | Cada tentativa é registrada; ao esgotar o limite, o run fica `failed`/`blocked` com erro e gaps preservados |
| AT-006 | Rollback concorrente | Um snapshot foi criado e o arquivo alvo mudou fora da execução | O self-healing precisa restaurar | Nenhum byte externo é sobrescrito; o resultado nomeia conflito, preserva snapshot e estado atual e exige reconciliação segura |
| AT-007 | Verificação independente | Um worker produz artifact, mas a prova obrigatória não existe ou falha | O reviewer/verifier avalia o run | O resultado não pode ser `DONE`; gaps, evidências ausentes e próxima ação aparecem no brief |
| AT-008 | Routing por capability | A matriz contém capabilities com estados, riscos, prerequisites e limitações diferentes | O runtime resolve uma tarefa | Apenas capabilities elegíveis são consideradas; uma capability sem prova suficiente fica `unresolved` ou é recusada |
| AT-009 | Eval adversarial | O caso simula timeout, payload inválido, divergência de agent, tool fora da allowlist ou evidence stale | A suíte executa o cenário | O runtime preserva a falha, aplica a policy correta e falha o gate quando a prova exigida não está disponível |
| AT-010 | DX canônica | Existe um run persistido com status, artifacts, gaps e replay | O usuário usa `doctor`, `status`, `review`, `evolve` ou `resume` | A superfície projeta os contratos canônicos sem alterar sua semântica e mantém os comandos expert compatíveis |
| AT-011 | Compatibilidade | Existem artifacts e runs produzidos pelo formato atual | O novo runtime carrega ou projeta esses dados | O conteúdo legado permanece legível; qualquer migração necessária é explícita, versionada e verificável |
| AT-012 | Evidência de fatia | Uma fatia possui testes, golden, holdout e mutation declarados | O gate da fatia é executado | A fatia só passa quando os casos obrigatórios e a verificação independente passam; falhas continuam visíveis |

---

## Out of Scope

Explicitly NOT included in this feature:

- Mutation direta de GitHub, AWS, bancos, brokers, CI providers ou qualquer sistema externo.
- Alteração remota de proteção da branch `main`, CODEOWNERS, merge policy ou configurações do repositório.
- Web UI e TUI completa antes de o kernel e a CLI canônica estarem comprovados.
- Criação massiva de agents sem capability, ferramentas, evals e justificativa de routing.
- Migração para microservices.
- Claims de produção, SLO, deployment safety ou paridade de host derivados apenas de fixtures locais.
- Freshness automática de knowledge packs por rede sem adapter read-only, receipt e política explícita.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Offline-first; sem SDK de modelo no core; domínio sem dependência de Typer, GitHub SDK ou AWS SDK | Adapters e ports serão mantidos fora do núcleo; execução local usa contratos e doubles permitidos |
| Safety | Read-only externo por padrão; mutation exige policy, approval, rollback, receipt e verificação independente | O runtime deve recusar ou deixar pendente ações sem requisitos; nunca transformar ausência de prova em sucesso |
| Persistence | Estado e artifacts devem ser persistidos, hashados e reprodutíveis | Resume, replay, idempotência, leases e conflitos precisam sobreviver a restart |
| Compatibility | Preservar CLI, contratos e artifacts existentes; quebra exige migração nomeada | Mudanças devem ser aditivas quando possível e cobertas por testes de compatibilidade |
| Build | Nenhum build escreve diretamente na main tree; usar sandbox, branch ou worktree governado | A implementação seguirá SDD e será promovida apenas após gates e evidências |
| Quality | Evals, holdout/mutation, testes, Ruff, mypy, SDD check e release gate não podem ser mascarados | Cada fatia terá quality gate e unresolved explícito |
| Infrastructure | Docker é opcional e somente para provas locais permitidas | Não há dependência obrigatória de infraestrutura nova nem ampliação de claims para produção |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/runtime`, `src/apiforge/contracts`, `src/apiforge/autonomy`, `src/apiforge/capabilities`, `src/apiforge/evals`, serviços de aplicação e CLI | Reutilizar o modular monolith; a CLI será somente uma projeção dos serviços |
| **KB Domains** | `genai`, `python`, `testing`, `pydantic`, `component-model` | Consultar state machines, agentic workflow, eval framework, clean architecture, contratos tipados e separação de camadas |
| **IaC Impact** | None | Docker pode apoiar probes locais, mas não são necessários novos recursos de infraestrutura |

**Why This Matters:**

- **Location** → Design phase uses correct project structure, prevents misplaced files
- **KB Domains** → Design phase pulls correct patterns from `${CLAUDE_PLUGIN_ROOT}/kb/`
- **IaC Impact** → Triggers infrastructure planning, avoids "works locally" failures

---

## Assumptions

Assumptions that if wrong could invalidate the design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | O `ControlPlane` existente pode se tornar autoridade sem invalidar os contratos atuais | Será necessário um adapter de compatibilidade e uma migração de estado antes da unificação | [ ] |
| A-002 | Os artifacts persistidos possuem informação suficiente para distinguir conclusão, tentativa e replay | Será preciso ampliar contratos e reconstruir uma trilha de eventos sem inferir estados antigos | [ ] |
| A-003 | As fixtures e testes locais representam os comportamentos críticos do kernel | Será necessário incorporar casos reais anonimizados ou novos laboratórios antes de afirmar qualidade | [ ] |
| A-004 | A fachada DX pode reutilizar serviços de aplicação existentes | Será preciso extrair serviços da CLI antes de adicionar novos comandos | [ ] |
| A-005 | Scorecards podem orientar seleção, mas não autorizar ações | Se houver acoplamento entre qualidade e autorização, policy deverá bloquear essa integração até separação formal | [ ] |
| A-006 | A concorrência relevante no primeiro ciclo está limitada a artifacts locais declarados | Se houver providers externos no escopo, cada um precisará de adapter, receipt, rollback e gate próprio | [ ] |

**Note:** Validate critical assumptions before DESIGN phase. Unvalidated assumptions become risks.

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | O problema, os componentes divergentes e o impacto operacional estão identificados |
| Users | 3 | Desenvolvedor/arquiteto e equipe de governança têm dores e responsabilidades explícitas |
| Goals | 3 | Metas MUST/SHOULD/COULD estão priorizadas e ligadas ao runtime, qualidade e DX |
| Success | 3 | Critérios são verificáveis por acceptance tests, gates, hashes, estados e compatibilidade |
| Scope | 3 | Inclusões, exclusões, constraints e fronteiras externas estão declaradas |
| **Total** | **15/15** | Pronto para Design; detalhes de arquitetura e manifest de arquivos ficam para a próxima fase |

**Scoring Guide:**

- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

Nenhuma pergunta bloqueadora para Design. A fase de Design deverá decidir, com evidência do código atual:

- Como versionar/adaptar estados e artifacts antigos sem duplicar o runtime.
- Quais campos são aditivos nos contratos existentes e quais exigem novo schema.
- Qual sequência de fatias entrega primeiro runtime seguro, depois capabilities/evals e então DX.
- Como o gate de eval será publicado sem introduzir SDK de modelo ou claims externos no core.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-23 | define-agent | Initial version derived from validated brainstorm |
| 1.1 | 2026-09-23 | ship-agent | Shipped and archived after implementation and verification |

---

## Next Step

**Archived:** feature shipped on 2026-09-23; implementation and verification evidence are preserved in the archive.
