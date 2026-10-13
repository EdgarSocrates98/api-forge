# DEFINE: API Git CI/CD Change Control Plane

> Fluxo read-only e reproduzível para governar mudanças de API iniciadas por PR, branch ou execução manual de CI/CD.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `API_GIT_CICD_CHANGE_CONTROL_PLANE` |
| **Date** | 2026-09-22 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 15/15 |

**Source:** `./BRAINSTORM_API_GIT_CICD_CHANGE_CONTROL_PLANE.md` (archived with the shipped feature).

---

## Problem Statement

Desenvolvedores, reviewers e responsáveis por CI/CD não possuem uma decisão única, reproduzível e evidence-first que relacione uma mudança de contrato de API ao diff Git, ao estado observável do pipeline e às recomendações arquiteturais dos agents; como consequência, fatos, incertezas e governança são revisados manualmente e podem divergir entre CI, CLI, MCP, IDE e UI.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Desenvolvedor | Autor de PR ou branch | Precisa saber se a mudança de API quebra consumidores, quais riscos existem e qual técnica deve ser aplicada. |
| Reviewer/maintainer | Responsável por revisar e aceitar mudanças | Precisa de impacto, evidência, limitações e próximo verificador sem reconstruir a análise manualmente. |
| Platform/CI owner | Dono de pipelines e políticas de entrega | Precisa de gates consistentes, permissões mínimas, artefatos auditáveis e métricas operacionais. |
| Integrador de IDE/MCP/UI | Autor de superfícies de engenharia | Precisa consumir o mesmo resultado canônico sem duplicar regras ou reinterpretar estados. |
| Autor de agent | Especialista que produz recomendações | Precisa provar qualidade, separar fatos de hipóteses e preservar `unresolved` quando não há evidência. |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Entregar um fluxo automático para PR/branch e um fluxo manual de diagnóstico/reprocessamento que terminem em resultado governado, sem traceback não controlado. |
| **MUST** | Implementar um adapter GitHub read-only que normalize contexto, diff, SHAs, checks e referências de artefatos com origem, hashes e limitações explícitas. |
| **MUST** | Executar a cadeia `analyze -> next-step -> graph -> evidence -> brief` para uma mudança de API e persistir todos os artefatos do case. |
| **MUST** | Avaliar recomendações dos agents com contrato estruturado, fixtures, goldens, holdouts e exemplos reais anonimizados. |
| **MUST** | Manter paridade semântica entre CLI, MCP, IDE e UI através de `CapabilityRequest/v1` e `CapabilityResult/v1`. |
| **MUST** | Impedir merge/push/deploy/auto-fix e qualquer mutação externa no primeiro corte; falhas e ausência de evidência devem ser governadas. |
| **SHOULD** | Emitir artefatos JSON, Markdown, JUnit, receipt e métricas operacionais consumíveis por CI e IDE/UI. |
| **SHOULD** | Traduzir findings técnicos para recomendações com fatos, premissas, alternativas, trade-offs, riscos, limitações, unresolved e próximo verificador. |
| **SHOULD** | Reproduzir localmente, sem rede, o resultado do CI a partir do bundle de artefatos coletado. |
| **COULD** | Adicionar comentário/status escrito no PR por adapter separado, com policy, aprovação, rollback e receipt. |
| **COULD** | Adicionar GitLab/Bitbucket e serviço persistente multi-repositório após evidência operacional suficiente. |

---

## Success Criteria

Metas normativas para o MVP, verificadas por testes e gates; não são afirmações de desempenho de produção:

- [x] **100%** dos cenários críticos de aceitação produzem `ok`, `review`, `blocked` ou `failed`, sem traceback não governado no caminho local/CLI/MCP.
- [ ] A smoke suite cobre **1** fluxo PR, **1** fluxo manual e **1** replay local do bundle, todos atravessando `analyze -> next-step -> graph -> evidence -> brief`. O PR live permanece pendente de política e receipt externa.
- [ ] Existe pelo menos **1 fixture, 1 golden e 1 holdout** para cada célula de API, Git e CI/CD; os casos reais anonimizados devem ser adicionados ao conjunto de avaliação antes do gate final.
- [x] **100%** das capabilities públicas da vertical declaram estado, documentação, limitações, evidências, pré-requisitos, risco, rollback e verificador.
- [x] O mesmo bundle de entrada reproduz os mesmos hashes de facts/findings/graph/receipt e o mesmo estado canônico em **2** execuções locais.
- [x] **0** valores de segredo, token ou conteúdo sensível de credencial aparecem nos artefatos publicados; falhas de sanitização bloqueiam a publicação.
- [x] Cada recomendação avaliada contém os **9** campos mínimos: `recommendation`, `facts`, `assumptions`, `alternatives`, `risks`, `unresolved`, `evidence_refs`, `verifier` e `confidence`.
- [x] A matriz de capabilities mantém explicitamente os estados `supported`, `heuristic`, `unresolved` e `unsupported`; nenhum estado é promovido sem adapter, evidência e verificador independentes.
- [x] As métricas registram pelo menos **8** dimensões: run id, origem, commit base, commit head, duração por etapa, status final, contagem de unresolved, falhas do adapter e referências dos artefatos.
- [x] A validação de segurança cobre **2** classes de entrada não confiável: PR de fork/token ausente e payload GitHub malformado.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | PR API change happy path | Um evento de PR contém base/head, contrato antes/depois, projeto e acesso read-only aos metadados | O workflow inicia a análise | O case é criado e os cinco estágios críticos produzem artifacts, receipt verificável, recomendação e brief; não há traceback |
| AT-002 | Manual reprocess | Um bundle exportado de PR contém diff, contratos, checks e metadados com hashes | A CLI executa o mesmo fluxo em modo local | O resultado é reproduzível sem rede e mantém estado, gaps, limitações e evidências equivalentes ao bundle original |
| AT-003 | Missing token | O contexto solicita coleta GitHub mas o token read-only não existe | O adapter é executado | A operação termina como `blocked` ou `unresolved` com `AF-*` explícito, próximo verificador e artefato diagnóstico; nenhum segredo é inventado |
| AT-004 | Read-only mutation boundary | Uma request declara `action=apply` ou tenta merge, push, deploy ou alteração de workflow | O gateway recebe a request | A operação é recusada pela policy com status `blocked`/`unsupported`, rollback requerido e sem chamada mutável |
| AT-005 | Malformed provider payload | O payload do PR, diff, check ou artifact é inválido, incompleto ou aponta para caminho inseguro | O adapter normaliza a entrada | O processo retorna erro tipado e persistido, sem traceback, sem escrever fora do case e sem promover conclusão |
| AT-006 | Breaking API change | O contrato antes/depois contém uma operação incompatível com o código ou contrato baseline | `analyze` e o judge determinístico são executados | O finding confirmado referencia facts, regra e localização; `next-step` seleciona o route correto ou nomeia `AF-ROUTING-NO-ROUTE` como gap explícito |
| AT-007 | Inconclusive CI execution | A configuração do pipeline existe, mas não há check concluído ou artefato verificável para o SHA | `cicd.inspect` avalia o contexto | O resultado permanece `heuristic`/`unresolved`, com limitação de que configuração não prova execução |
| AT-008 | Complete evidence chain | O case contém artifacts válidos de análise e findings | Graph, receipt e brief são executados | O graph referencia o case, o receipt revalida hashes, e o brief termina em estado governado com gaps e ação humana quando necessário |
| AT-009 | Recommendation contract | Um agent produz recomendação para a mudança | O supervisor valida o output | Os nove campos mínimos são aceitos somente quando válidos; fatos e evidence refs são distintos de assumptions e unresolved |
| AT-010 | Recommendation golden/holdout | Existe um golden representativo e um holdout com evidência ausente ou ambígua | O evaluator processa ambos | O golden atende a expectativa revisada e o holdout não permite recomendação otimista sem evidência; resultado e motivo são persistidos |
| AT-011 | Surface parity | A mesma `CapabilityRequest/v1` é enviada por CLI, MCP, IDE e UI | Cada surface projeta o resultado | `capability_id`, state, status, payload, evidence, gaps, limitations e error code mantêm semântica equivalente |
| AT-012 | External evidence provenance | O adapter recebe diff, check e artifact de uma origem externa | O case é materializado | Cada fonte registra origem, referência, timestamp, hash e limitação; o receipt prova correspondência e não autoria |
| AT-013 | Secret safety | Um input de CI contém token, URL assinada ou variável sensível | Sanitização e publicação são executadas | Os valores não aparecem em facts, logs, JUnit, Markdown, JSON ou receipt; a falha de sanitização bloqueia a saída |
| AT-014 | Operational metrics | O fluxo termina em `ok`, `review`, `blocked` ou erro controlado | O publisher gera métricas | O registro contém as dimensões mínimas definidas e pode ser correlacionado ao run, case e artifacts sem depender de serviço persistente |
| AT-015 | Unsupported provider | A entrada identifica provedor que não possui adapter | O ingress tenta selecionar o adapter | A execução termina com `AF-INTEGRATION-UNSUPPORTED`, capability `unsupported` e instrução de como adicionar adapter, sem fallback silencioso |

---

## Out of Scope

Explicitly NOT included in this feature:

- Merge, push, deploy, auto-fix, commit gerado, alteração de workflow ou publicação de comentário/status via API do GitHub.
- Serviço persistente, webhook externo, fila, banco de casos, dashboard multi-repositório ou retenção centralizada.
- GitLab, Bitbucket e outros provedores além do primeiro adapter GitHub.
- Execução de código não confiável do PR, testes com credenciais, acesso live a banco/cloud/broker ou inferência de runtime a partir de configuração.
- Promoção de `git.plan` ou `cicd.inspect` para `supported` sem prova independente específica.
- Substituição do supervisor determinístico por LLM, SDK de modelo ou julgamento sem facts e evidências.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | O core continua offline-first, determinístico e sem SDKs de modelo, cloud, banco ou broker. | Adapters e coletores devem separar fronteira externa da aplicação e permitir replay por arquivos. |
| Technical | O contrato canônico é `CapabilityRequest/v1`/`CapabilityResult/v1`. | CLI, MCP, IDE e UI não podem criar semântica paralela. |
| Technical | A cadeia crítica precisa preservar todos os diagnostics, findings, hashes e unresolved. | `review`, `blocked` e `unresolved` são estados válidos, não falhas a ocultar. |
| Security | GitHub é read-only; PRs de fork e tokens ausentes não podem executar ações mutáveis ou revelar segredos. | O workflow deve usar policy de menor privilégio e coleta separada de execução do código do PR. |
| Security | Conteúdo externo é input potencialmente hostil. | Validar schema, caminhos, tamanho, hashes, sanitização e limites antes de persistir. |
| Integration | O primeiro provider é GitHub e a saída primária é artefato do CI. | O adapter não escreve no provedor; publicação externa futura exige feature separada. |
| Testing | Há fixtures atuais, goldens/holdouts por vertical e devem ser incluídos exemplos reais anonimizados. | O evaluator deve ser determinístico no núcleo e rastrear a origem de cada sample. |
| Operational | Não há serviço persistente ou backend de métricas obrigatório no MVP. | Métricas devem ser emitidas em artifacts locais/CI e ser replayáveis. |
| Resource | O projeto deve usar os diretórios e contratos existentes, sem reestruturar todo o core. | Mudanças ficam concentradas em integrações, aplicação, CLI/workflow, testes, evals e documentação. |
| Timeline | Não foi definido prazo externo. | A entrega deve ser dividida em gates verificáveis, sem assumir deadline. |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/contracts/`, `src/apiforge/integrations/`, `src/apiforge/application/`, `src/apiforge/cli.py`, `.github/workflows/`, `tests/`, `evals/`, `docs/` | Estender contratos e use cases existentes; manter o provider atrás de adapter e os artefatos no case. |
| **KB Domains** | `python`, `pydantic`, `testing`, `genai` | Clean architecture e error handling; schemas e validação; integração/fixtures/holdouts; workflow e avaliação de agents. |
| **IaC Impact** | None for MVP; workflow changes only | Não criar recursos cloud, serviço persistente ou banco; a workflow do GitHub é configuração versionada, não infraestrutura runtime. |

**Relevant Existing Evidence:**

- `src/apiforge/contracts/platform.py` define os contratos canônicos de capability e surface.
- `src/apiforge/integrations/gateway.py` já bloqueia mutação sem policy, aprovação e rollback.
- `src/apiforge/integrations/git.py` e `cicd.py` são boundaries estáticas que precisam ganhar adapter read-only real sem contaminar o core.
- `src/apiforge/rules/capability_matrix.yaml` registra estados, evidências, limitações e verifiers.
- `tests/e2e/test_platform_completion.py`, `tests/e2e/test_next_step.py` e `tests/labs/test_platform_verticals.py` são pontos de verificação existentes.
- `.apiforge/case/` é a fonte de evidência persistida para análise corrente; o caso atual ainda possui unresolved e uma rota ausente para `discover`/`CONTRACT`.
- `.claude/CLAUDE.md` não existe; as instruções de projeto estão em `CLAUDE.md`, além de `AGENTS.md` e `AGENT_PROTOCOL.md`.

---

## Data Contract (if applicable)

Não aplicável como pipeline de dados de negócio. O feature possui um contrato de evidência de engenharia que deverá ser especificado no DESIGN:

| Artifact | Required content | Integrity |
|----------|------------------|-----------|
| Provider context | provider, repository, run, event/manual origin, base/head refs | schema validation and source hash |
| API change input | before/after contract or declared baseline, project path and diff reference | input hashes and safe paths |
| CI evidence | check name, conclusion, SHA, run/artifact reference, observed timestamp | source reference and receipt binding |
| Recommendation | nine output fields from `AGENT_OUTPUT_CONTRACT.md` | contract validation and evaluator result |
| Metrics | run/case identity, stage timings, final status, unresolved/errors and artifact references | append-only artifact with receipt |

---

## Assumptions

Assumptions that if wrong could invalidate the design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | O GitHub Actions disponibiliza contexto suficiente para correlacionar PR, base SHA, head SHA, checks e artefatos em modo read-only. | Será necessário um exportador externo ou o escopo deverá voltar para artifact-first. | [ ] |
| A-002 | Um bundle sanitizado pode representar o contexto externo sem executar o código do PR. | O replay local não provará correspondência e a coleta precisará de contrato mais restrito. | [ ] |
| A-003 | Os contratos `CapabilityRequest/v1` e `CapabilityResult/v1` suportam a nova capability sem quebrar surfaces existentes. | Exigirá versionamento aditivo ou nova versão de contrato. | [ ] |
| A-004 | É possível obter e aprovar pelo menos dois exemplos reais anonimizados de PR/CI sem PII, tokens ou URLs sensíveis. | A avaliação inicial ficará limitada às fixtures sintéticas e terá menor validade externa. | [ ] |
| A-005 | Os artefatos do CI são suficientes para a publicação primária sem comentário/status via API. | Será necessário um publisher separado e uma policy de escrita. | [ ] |
| A-006 | A execução do fluxo no CI pode ser separada da execução do código não confiável do PR. | Forks exigirão workflow/artifact boundary diferente e a coleta poderá ficar `unresolved`. | [ ] |
| A-007 | Métricas em JSON/JUnit/artifacts são suficientes para a primeira prova operacional. | Será necessário escolher e provisionar uma integração de observabilidade antes do MVP. | [ ] |
| A-008 | O route catalog pode ser ampliado para eliminar o gap `AF-ROUTING-NO-ROUTE` sem alterar a semântica de findings. | O caso de contrato continuará exigindo fallback explícito ou supervisionado. | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Problema e impacto para autor, reviewer e CI owner estão definidos em uma frase acionável. |
| Users | 3 | Cinco personas foram identificadas com papéis e dores concretas. |
| Goals | 3 | Goals têm prioridades MUST/SHOULD/COULD e fronteira read-only explícita. |
| Success | 3 | Critérios mensuráveis incluem cobertura, replay, segurança, schema e ausência de traceback. |
| Scope | 3 | Out of scope exclui mutação, serviço persistente, multi-provider e execução insegura. |
| **Total** | **15/15** | Gate de 12/15 atendido; pronto para Design. |

---

## Open Questions

Perguntas não bloqueantes para a fase DESIGN:

1. Qual formato exato será o bundle canônico do adapter GitHub: JSON próprio, payloads sanitizados ou ambos?
2. Quais checks têm poder de bloquear e quais apenas produzem `review`?
3. Qual policy de token e fluxo de forks será adotado para separar coleta read-only de execução do PR?
4. Onde os exemplos reais anonimizados serão versionados, aprovados e removidos quando expirarem?
5. A primeira integração IDE/UI consumirá MCP, arquivos de artifact ou uma ponte local?
6. Qual formato inicial de métricas será obrigatório: JSONL, JUnit, OpenTelemetry ou combinação mínima?
7. Como o route catalog tratará a ausência de rota para `discover`/`CONTRACT` identificada no caso atual?

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-22 | define-agent | Requisitos derivados do brainstorm aprovado; clareza 15/15; status pronto para Design. |
| 1.1 | 2026-09-22 | ship-agent | Feature shipped; archived with external-proof gaps preserved as unresolved. |

---

## Next Step

**Shipped by:** `/ship .claude/sdd/features/DEFINE_API_GIT_CICD_CHANGE_CONTROL_PLANE.md`
