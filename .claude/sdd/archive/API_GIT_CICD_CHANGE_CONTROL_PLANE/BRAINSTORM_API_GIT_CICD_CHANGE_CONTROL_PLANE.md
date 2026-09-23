# BRAINSTORM: API Git CI/CD Change Control Plane

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `API_GIT_CICD_CHANGE_CONTROL_PLANE` |
| **Date** | 2026-09-22 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |

---

## Initial Idea

**Raw Input:** Entregar o próximo salto da API Forge como uma vertical principal de API + Git + CI/CD, com adapter read-only real, evidência externa reproduzível, avaliação das recomendações dos agents, fluxo completo para o usuário, integração real com IDE/UI, métricas operacionais e segurança.

**Context Gathered:**

- O fluxo crítico local já existe como `analyze -> next-step -> graph -> evidence -> brief` e possui teste e2e em `tests/e2e/test_platform_completion.py`.
- A plataforma já usa `CapabilityRequest/v1`, `CapabilityResult/v1`, `IntegrationGateway`, matriz pública de capabilities e contratos de evidência.
- O adapter Git local ainda é estático e mantém `git.plan` como `unresolved`; o adapter CI/CD mantém `cicd.inspect` como `heuristic`.
- A workflow `.github/workflows/ci.yml` já valida o repositório, mas ainda não representa uma mudança de API em PR nem coleta contexto de um provedor Git.
- O caso persistido em `.apiforge/case/` possui 8 findings, dos quais 3 estão `unresolved`. `next-step` roteia a fase `verify` para `api-governance-reviewer`; a fase `discover` ainda produz `AF-ROUTING-NO-ROUTE` para a área dominante `CONTRACT`.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/integrations/`, `src/apiforge/application/`, `src/apiforge/contracts/`, `.github/workflows/`, `tests/e2e/`, `tests/evals/` | Adicionar adapter e orquestração sem quebrar o core determinístico |
| Relevant KB Domains | `python`, `pydantic`, `testing`, `genai` | Contratos tipados, adaptadores, holdouts, avaliação de agents e validação reprodutível |
| IaC Patterns | N/A para o primeiro corte | Não criar serviço persistente ou infraestrutura de controle antes de provar a vertical |
| Existing Boundary | GitHub read-only + artefatos gerados no CI | Token, diff, checks e artefatos entram como evidência; nenhuma mutação externa é autorizada |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Qual resultado principal deve orientar a nova vertical? | Fluxo completo de mudança de API + governança de CI/CD. | O produto deve fechar o ciclo de mudança, não adicionar capabilities isoladas. |
| 2 | Quem inicia o fluxo? | Ambos: PR/branch executa automaticamente; execução manual serve para diagnóstico e reprocessamento. | O contrato precisa aceitar contexto de evento e contexto explícito, com comportamento idempotente. |
| 3 | Qual fronteira de integração externa? | GitHub read-only, lendo PR, diff, checks e artefatos; a saída é produzida pelo CI. | O adapter não faz merge, push, deploy, alteração de workflow ou comentário via API. |
| 4 | Quais dados de amostra estarão disponíveis? | Fixtures atuais + exemplos reais anonimizados de PRs, contratos e execuções de CI. | Goldens devem cobrir exemplos revisados; holdouts devem preservar incerteza e ausência de evidência. |

**Minimum Questions:** 4

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `tests/fixtures/platform/api/` | 1 célula | OpenAPI, aplicação e caso de API; base para mudança antes/depois. |
| CI input | `tests/fixtures/platform/cicd/` | 1 célula | `pipeline.yaml`, golden e holdout; representa configuração sem prova de execução. |
| Cross-vertical fixtures | `tests/fixtures/platform/{api,database,messaging,cicd,cloud,frontend}/` | 6 células | Cada vertical possui fixture, golden e holdout. |
| Current evidence | `.apiforge/case/` | 5 artefatos | `case.json`, `api-ir.json`, `facts.json`, `findings.json` e `receipt.json`. |
| Output examples | `tests/fixtures/platform/*/golden.json` | 6 goldens | Expectativas revisadas e determinísticas. |
| Uncertainty examples | `tests/fixtures/platform/*/holdout.yaml` | 6 holdouts | Caminhos `unresolved`, `unsupported` ou `inconclusive`. |
| Real anonymized data | A ser curado em `evals/datasets/api-git-cicd/` | Pendente | PRs, diffs OpenAPI, checks e relatórios de CI sem segredos ou identificadores sensíveis. |
| Related code | `src/apiforge/contracts/platform.py`, `src/apiforge/integrations/gateway.py`, `src/apiforge/integrations/git.py`, `src/apiforge/integrations/cicd.py` | 4 áreas | Contratos e adapters existentes a estender, sem duplicar semântica por superfície. |

**How samples will be used:**

- Reproduzir localmente o mesmo input coletado no PR, sem dependência de rede.
- Validar schema, hashes, timestamps, source references e estado de evidência.
- Comparar recomendações dos agents contra goldens e holdouts, incluindo ausência de conclusão quando faltar prova.
- Exercitar a paridade entre CLI, MCP, IDE e UI através do mesmo resultado canônico.

---

## Approaches Explored

### Approach A: PR-native read-only control plane ⭐ Recommended

**Description:** Um workflow do GitHub Actions coleta o contexto do PR ou da execução manual. Um adapter GitHub somente leitura normaliza diff, SHAs, metadados, checks e artefatos; o núcleo cria um case, executa a cadeia completa, avalia a recomendação do agent e publica JSON, Markdown, JUnit e receipt como artefatos do CI. O modo local reprocessa os mesmos artefatos sem rede.

**Pros:**

- Fecha o fluxo real de mudança de API e governança no PR sem permitir mutações externas.
- Reutiliza os contratos, a matriz de capabilities, a cadeia de evidência e as superfícies existentes.
- Produz prova reproduzível e uma base estável para IDE/UI e métricas futuras.
- Permite least privilege e bloqueio explícito para forks, tokens ausentes e checks inconclusivos.

**Cons:**

- Exige política de token, tratamento de rate limit e normalização de formatos do GitHub.
- O adapter só prova o que o provedor expõe; execução, permissões e qualidade do pipeline continuam condicionadas à evidência coletada.

**Why Recommended:** É a menor mudança que entrega o resultado escolhido, mantém o core offline-first e pode promover `git.plan`/`cicd.inspect` somente quando houver evidência e verificador independentes.

**Confidence:** 0.95 — forte correspondência com os contratos e gates já presentes; a implementação live do adapter ainda precisa ser provada.

---

### Approach B: Artifact-first local pipeline

**Description:** O workflow fornece apenas arquivos exportados — diff, contratos, metadados, JUnit e relatórios — e o API Forge não acessa a API do GitHub.

**Pros:**

- Escopo menor, execução offline e superfície de segurança mais simples.
- Excelente reprodutibilidade e compatibilidade com outros provedores.

**Cons:**

- Não prova a leitura real do PR, checks ou artefatos no provedor.
- Exige uma etapa externa para exportar e manter o contexto coerente.
- Entrega uma integração mais fraca com IDE/UI e governança de PR.

**Confidence:** 0.98 para execução local; 0.70 para satisfazer a ambição de integração externa real.

---

### Approach C: External persistent control service

**Description:** Webhook, API persistente, armazenamento de casos, dashboard, fila de execução e integração centralizada com GitHub.

**Pros:**

- Melhor experiência centralizada, métricas históricas e possibilidade de múltiplos repositórios.
- Abre caminho para políticas organizacionais e comparação entre equipes.

**Cons:**

- Introduz autenticação, tenancy, disponibilidade, retenção, custos, operação e novas superfícies de ataque.
- Aumenta o sistema antes de validar o fluxo fundamental e o avaliador de recomendações.
- Pode deslocar o núcleo determinístico para uma dependência de serviço.

**Confidence:** 0.65 — arquitetura plausível, mas sem evidência de necessidade operacional nesta fase.

---

## Data Engineering Context

Não aplicável ao primeiro corte. O fluxo trata evidência de engenharia e mudanças de contratos, não uma pipeline de dados de negócio.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A — PR-native read-only control plane |
| **User Confirmation** | Confirmado em 2026-09-22 após validação da arquitetura e dos componentes |
| **Reasoning** | Entrega fluxo completo de API + Git + CI/CD, mantém o modo local reproduzível e preserva o bloqueio de mutações externas. |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|---------------------|
| 1 | PR/branch e execução manual são entradas equivalentes, com reprocessamento determinístico. | Atende automação e diagnóstico sem criar dois contratos. | Fluxos separados por superfície. |
| 2 | GitHub será o primeiro provider e o adapter será read-only. | Há uma workflow GitHub existente e o risco fica limitado a coleta de evidência. | Suportar múltiplos provedores no primeiro corte. |
| 3 | Artefatos do CI são a publicação primária. | Mantém a integração auditável e evita escrita via API externa. | Comentários/status automáticos no PR. |
| 4 | O core executa a cadeia completa e preserva `unresolved`. | Um parser ou check ausente não pode virar aprovação implícita. | Resolver lacunas por inferência do agent. |
| 5 | Goldens, holdouts e exemplos reais anonimizados avaliam recomendações. | Mede qualidade e segurança das sugestões, não apenas schema do payload. | Aceitar recomendações apenas por validade sintática. |
| 6 | CLI, MCP, IDE e UI projetam o mesmo resultado canônico. | Evita divergência de status, evidência e limites entre superfícies. | Lógica específica por host. |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Merge, push, deploy ou alteração de workflow | São mutações externas e não são necessárias para provar análise e governança. | Yes, with explicit adapters, approval, rollback and receipt. |
| Auto-fix ou commit gerado a partir da recomendação | Mistura sugestão com execução e aumenta risco em PR não confiável. | Yes, through sandbox and a separate mutation feature. |
| Comentário/status escrito pela API do GitHub | A integração selecionada é read-only; artefatos do CI já são prova suficiente no primeiro corte. | Yes, with a separate write adapter and permission policy. |
| Serviço persistente, webhook, fila e dashboard multi-repositório | Não há evidência de necessidade antes de validar a vertical no CI. | Yes, after operational metrics demonstrate the need. |
| GitLab, Bitbucket e provedores adicionais | Evita abstração prematura e mantém um verificador concreto. | Yes, behind the same adapter contract. |
| Execução de código do PR, testes com credenciais ou acesso a banco/cloud | Viola o modelo offline-first e amplia a ameaça de código não confiável. | Yes, only as explicit sandboxed evidence providers. |
| Modelo SDK dentro do core | Preserva determinismo, reprodutibilidade e a separação entre agent e supervisor. | Yes, in an external agent host, never as an implicit core dependency. |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Architecture concept and approach comparison | ✅ | Confirmou a Abordagem A: PR-native read-only, com modo artifact-first local. | Yes — C foi adiada e B permaneceu como modo de reprodução. |
| Component breakdown and evidence flow | ✅ | Confirmou a decomposição em ingress, adapter, control plane, evaluator e publisher. | Yes — publicação primária ficou limitada a artefatos do CI; mutações foram removidas do primeiro corte. |
| Discovery scope | ✅ | Escolheu fluxo de mudança de API + governança de CI/CD, com PR/branch e execução manual. | Yes — contrato único de entrada e reprocessamento determinístico. |

**Minimum Validations:** 2 — completed

---

## Suggested Requirements for /define

### Problem Statement (Draft)

Uma mudança de API em PR precisa de uma decisão reproduzível e evidence-first que relacione diff, contrato, código, checks de CI/CD e recomendações arquiteturais, sem afirmar execução ou segurança que não tenham prova.

### Target Users (Draft)

| User | Pain Point |
|------|------------|
| Desenvolvedor | Não sabe rapidamente se a alteração de contrato quebra consumidores ou qual é o próximo passo técnico. |
| Reviewer/maintainer | Precisa revisar impacto e governança sem reconstruir manualmente facts, checks e evidências. |
| Platform/CI owner | Precisa de gates consistentes, least privilege, artefatos auditáveis e métricas de falha. |
| Integrador de IDE/MCP/UI | Precisa consumir o mesmo resultado canônico sem duplicar regra ou reinterpretar estado. |
| Autor de agent | Precisa medir qualidade das recomendações e preservar incerteza em casos holdout. |

### Success Criteria (Draft)

- [ ] Um PR ou execução manual válida termina com resultado governado, sem traceback, mesmo quando o adapter falhar, o token faltar ou o check estiver inconclusivo.
- [ ] O adapter GitHub read-only coleta e hasheia diff, SHAs, metadados, checks e referências de artefatos, sem expor segredos.
- [ ] O fluxo produz case, facts/findings, `next-step`, graph, receipt verificável, recommendation artifact e Outcome Brief.
- [ ] O modo local reproduz o resultado do CI usando os artefatos exportados, sem acesso à rede.
- [ ] API breaking change, CI policy e ausência de evidência terminam em estados explícitos (`confirmed`, `unresolved`, `review` ou `blocked`), nunca em aprovação implícita.
- [ ] Cada recomendação contém fatos, premissas, alternativas, riscos, unresolved, referências de evidência, verificador e confiança limitada.
- [ ] A avaliação possui fixtures, goldens, holdouts e casos reais anonimizados; falsos positivos, falsos negativos e falhas de schema são mensurados.
- [ ] CLI, MCP, IDE e UI preservam o mesmo `CapabilityResult`, incluindo estado, gaps, evidências, limitações e error codes.
- [ ] Métricas operacionais cobrem duração por etapa, status final, falhas de adapter, idade/hash de evidência, unresolved count, artefatos e avaliação de recomendações.
- [ ] O CI usa permissões mínimas, não executa código não confiável durante a coleta e não grava credenciais nos artefatos.

### Constraints Identified

- Core determinístico, offline-first e sem model/cloud/database/broker SDKs.
- GitHub como primeiro provedor, com adapter read-only e modo artifact-first.
- PRs de forks e tokens ausentes devem degradar para resultado governado, não exceção não tratada.
- Nenhum número, status de execução ou garantia operacional pode ser inventado sem `fact_id` e fonte.
- Toda capability pública precisa de documentação, limitações, evidências e verificador.
- A workflow atual `.github/workflows/ci.yml` é uma base local ainda não equivalente ao fluxo de mudança de API.

### Out of Scope (Confirmed)

- Merge, push, deploy, auto-fix, alteração de workflow ou escrita direta no GitHub.
- Serviço persistente, dashboard multi-repositório e governança multi-provider.
- Execução de código do PR fora de um sandbox explicitamente governado.
- Prova de runtime, performance, permissões, segurança ou entrega de CI quando o provedor não fornecer evidência observável.

### Open Questions for /define

- Qual formato de exportação do GitHub será o contrato canônico do adapter: JSON próprio, payloads brutos sanitizados ou ambos?
- Quais checks bloqueiam a decisão e quais apenas geram `review`?
- Qual política de token e comportamento para forks será adotado no workflow?
- Onde os exemplos reais anonimizados serão versionados e como serão aprovados?
- A primeira integração de IDE/UI consumirá MCP, arquivos de artefato ou uma ponte local?
- Qual formato inicial de métricas será obrigatório: JSONL local, JUnit, OpenTelemetry ou combinação mínima?

### Known Unresolved Gaps

- Ainda não existe adapter GitHub live comprovado; os adapters atuais são contratos estáticos.
- A execução real do provider e a correlação entre checks e commits precisam de evidência externa reproduzível.
- O conjunto de PRs reais anonimizados ainda precisa ser coletado, sanitizado e revisado.
- A fase `discover` não possui rota para a área `CONTRACT` no caso atual (`AF-ROUTING-NO-ROUTE`); isso deve ser tratado como gap de roteamento, não suprimido.
- A integração IDE/UI concreta e o backend de métricas ainda não foram escolhidos.
- O CI local tem alterações não commitadas em `README.md` e `.github/workflows/ci.yml`; elas não fazem parte deste brainstorm até serem deliberadamente incluídas no build.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 4 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 7 |
| Validations Completed | 3 |
| Duration | One interactive session on 2026-09-22 |

---

## Next Step

**Archived by:** `/ship .claude/sdd/features/DEFINE_API_GIT_CICD_CHANGE_CONTROL_PLANE.md`

**Shipment note:** Exploratory decisions and unresolved external-proof gaps were
preserved as part of the shipped feature archive.
