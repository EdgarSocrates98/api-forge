# BRAINSTORM: API Forge Portable Distribution, Workspace and Host Activation

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_PORTABLE_DISTRIBUTION_WORKSPACE |
| **Date** | 2026-09-24 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |

---

## Initial Idea

**Raw Input:**

The user proposes changing API Forge from a repository-centered tool that is copied into projects into an installed, portable engineering platform. A user should install it once, connect it to a repository or workspace, and use its core, agents, skills, knowledge, SDD, graph, evidence and verification without copying large host mirrors into the consumer project. The platform must support independent repositories, virtual workspaces, impact-focused context, optional host activation, MCP, offline use, network-restricted environments and installations in user-selected paths without administrator privileges.

**Context Gathered:**

- The package already exposes `apiforge`, `apiforge-mcp` and `apiforge-tui` entrypoints, but the documented installation is still repository-oriented and editable.
- The repository already contains host-neutral adapters, host parity and activation plans, MCP, modular experience projections, context funneling, evidence contracts and a deterministic runtime.
- Current host assets are mirrored under `.claude/`, `.agents/`, `.devin/` and `.github/`; the new direction makes packaged API Forge assets the source of truth and treats mirrors as optional generated compatibility surfaces.
- The current repository has no first-class `init`, `workspace`, `here` or portable-install contract; these are design targets, not existing capabilities.
- The user selected the complete program as the strategic scope, all three user groups as targets, all resilience constraints as mandatory, and all major outcomes as success criteria. Delivery remains wave-based.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/application`, `src/apiforge/agentops`, `src/apiforge/mcp`, `src/apiforge/contracts`, new distribution/context/workspace modules | Add facades and versioned contracts over the deterministic core; do not make hosts the runtime authority |
| Relevant KB Domains | `genai`, `python`, `testing`, `prompt-engineering`, plus project-local API Forge context/evidence patterns | Use explicit state transitions, structured context, portable prompts, typed manifests, fixture-driven validation and guardrails |
| Existing Code Patterns | `HostAdapter`, `ActivationPlan`, parity audit, MCP server, `experience` projections, context funnel, hash-backed case artifacts | Extend existing contracts additively and preserve CLI/MCP/JSON parity |
| IaC Patterns | N/A for the first distribution slice; local paths, virtual environments and containers are the relevant deployment surfaces | Installation and discovery must be local, deterministic and permission-aware |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Qual objetivo deve guiar a primeira fatia? | **D — Programa completo**, organizado em ondas | O brainstorm precisa cobrir distribuição, workspace, graph, contexto, hosts, MCP, UX e resiliência sem transformar tudo em uma entrega única |
| 2 | Quem deve ser o usuário principal? | **D — Todos**: desenvolvedor, equipe de plataforma e maintainer de hosts | O núcleo deve ser comum e hostless, com experiências progressivas por persona |
| 3 | Qual restrição é inegociável? | **D — Todas**: não copiar conhecimento, preservar repos independentes e manter offline-first/evidence-driven | Instalação, workspace e host activation não podem exigir monorepo, rede ou privilégios administrativos |
| 4 | Como medir sucesso? | **D — Todos**: instalação/`init`, workspace/impact graph, hosts/MCP e compatibilidade expert, entregues em ondas | Cada onda precisa de gates próprios e não pode quebrar a interface expert existente |
| 5 | Quais amostras devem fundamentar o design? | **D — Todas**: código/fixtures existentes, workspaces sintéticos, exemplos de hosts/MCP e saídas esperadas | A validação deve combinar regressão do projeto, cenários multi-repo e contratos de projeção |

**Minimum Questions:** 5 (to ensure clarity before proceeding)

---

## Sample Data Inventory

> Samples are local, repository-owned or user-provided. External availability is not inferred from them.

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `prompt_evo_portable_api_forge.md`; `pyproject.toml`; `AGENTS.md`; `CLAUDE.md` | Present | Raw product vision, package metadata and operating constraints |
| Output examples | `README.md`; `docs/guides/API_FORGE_PLATFORM_USAGE.md`; `docs/guides/API_FORGE_EXPERIENCE_INTEROPERABILITY.md`; `docs/HOST_PARITY.md` | Present | Existing installation, host, context and experience documentation to preserve and revise |
| Ground truth | `src/apiforge/agentops/hosts.py`; `src/apiforge/agentops/activation.py`; `src/apiforge/agentops/parity.py`; `src/apiforge/mcp`; `src/apiforge/application`; `.apiforge/case/*` | Present | Existing contracts, capabilities, projections and evidence boundaries |
| Related code | `src/apiforge/cli.py`; `src/apiforge/dispatch/mirrors.py`; `src/apiforge/knowledge`; `src/apiforge/contracts`; `tests/agentops`; `tests/mcp`; `tests/application`; `tests/knowledge`; `tests/fixtures/tui` | Present | Reuse points for distribution, host activation, context, MCP, testing and projections |
| Synthetic scenarios | To be added in Define/Build under `tests/fixtures/portable_distribution` and `tests/fixtures/workspaces` | Planned | Independent repos, blocked network, non-admin prefix, missing host and partial graph evidence |

**How samples will be used:**

- Treat existing CLI, MCP, contract and host tests as compatibility baselines.
- Add synthetic repository trees for repo, workspace and target scopes without requiring a monorepo.
- Validate local-only operation when a host, network, optional dependency or external receipt is unavailable.
- Use expected `status`, `doctor`, `context`, graph and activation payloads as projection fixtures.
- Validate portable installation through user-selected prefixes and platform-specific executable paths.
- Keep unresolved capability states visible instead of converting missing external evidence into success.

---

## Approaches Explored

### Approach A: Plataforma instalada com camadas progressivas ⭐ Recommended

**Description:** Distribute API Forge as an installable package whose core owns agents, skills, knowledge, contracts, SDD, graph, evidence, verification and host-neutral execution. Add context/root resolution, project and workspace manifests, virtual architecture IR, scopes, cache and optional host activation as additive layers.

**Pros:**

- Directly reuses the existing CLI, MCP, `agentops`, `experience`, evidence and contract patterns.
- Supports a user-selected installation prefix and hostless operation.
- Preserves independent repositories and allows incremental migration from current mirrors.
- Gives `init`, `status`, `doctor`, `context` and later human-mode commands one canonical core.

**Cons:**

- Requires new contracts for installation, root resolution, configuration precedence, workspace graph and generated host adapters.
- Has the broadest first-wave surface and needs strict wave gates.

**Why Recommended:** The codebase already has package entrypoints, host capability models, plan-only activation, MCP, modular experience projections and evidence-backed context services. The KB patterns for explicit state machines, plan-and-execute workflows, structured context and guardrails support the same direction. Confidence: strong, based on direct codebase and KB pattern matches.

---

### Approach B: Forge externo e zero-touch por padrão

**Description:** Keep all state in a global or ephemeral API Forge directory. Consumer repositories receive no persistent files; CLI and local MCP resolve context from the current path and parent directories.

**Pros:**

- Strongest protection for locked-down and read-only repositories.
- Minimal project footprint and clean corporate adoption path.
- Natural fit for `inspect`, ephemeral workspaces and one-off analysis.

**Cons:**

- Less reproducible across machines without a persistent manifest.
- Shared context and workspace discovery become harder to explain and audit.
- CI, teams and remote hosts need an external state-sharing convention.

---

### Approach C: Compatibilidade-first com mirrors gerados

**Description:** Package the source assets inside API Forge but continue generating `.claude`, `.agents`, `.devin`, `.github` and instruction files through `init` and `host sync`; add workspace features later.

**Pros:**

- Lowest migration risk for current host integrations.
- Existing host behavior can remain operational during transition.
- Hashes and manifests can make generated output deterministic.

**Cons:**

- Keeps substantial duplication in consumer repositories.
- Preserves host-specific project files as a long-term operational burden.
- Delays the main differentiator: virtual workspace context and impact narrowing.

---

## Data Engineering Context (if applicable)

Não aplicável como pipeline de dados. O architecture graph, os índices e os caches são artefatos locais versionados ou content-addressed; nenhum banco, broker ou serviço cloud é necessário para a primeira distribuição.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A — Plataforma instalada com camadas progressivas |
| **User Confirmation** | 2026-09-24 |
| **Reasoning** | O usuário escolheu a visão completa de plataforma, confirmou a abordagem A e exigiu operação hostless, offline-capable, multi-repo e sem privilégios administrativos |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|---------------------|
| 1 | API Forge é instalado; não copiado | O pacote instalado deve ser a fonte de verdade para core, agents, skills, conhecimento e contratos | Exigir cópia de `.agents`, `.claude`, `.devin`, `.github` e skills completas |
| 2 | Host integration é opcional | A análise, contexto, SDD, graph, evidência, verificação, agents e skills precisam funcionar diretamente pelo Forge | Tornar Claude, Devin, Codex, Copilot ou MCP remoto pré-requisitos |
| 3 | Instalação aceita prefixo escolhido pelo usuário | Ambientes sem admin precisam usar venv, prefixo, volume, container ou diretório corporativo permitido | Exigir instalação global do sistema |
| 4 | Rede é capacidade opcional | O core deve funcionar com conteúdo empacotado/cache local; freshness e integrações remotas permanecem explícitas | Bloquear uso local quando rede, credencial ou provider estiver indisponível |
| 5 | Workspace virtual preserva `.git` independentes | Empresas podem correlacionar serviços, SDKs e infraestrutura sem monorepo | Forçar reorganização em um repositório único |
| 6 | Mirrors são compatibilidade gerada | Mantém hosts atuais funcionais sem tratá-los como source of truth | Continuar mantendo conhecimento duplicado manualmente em cada repo |
| 7 | MCP local via stdio é preferencial | Evita daemon, porta ou serviço de rede obrigatório | Exigir MCP remoto para integração profunda |
| 8 | Documentação completa é gate de entrega | A mudança afeta instalação, operação, manifests, hosts, segurança, roadmap e migração | Atualizar apenas README ou apenas a documentação do host |
| 9 | Commit e evidência fazem parte do ship | A mudança só está pronta quando artifacts, docs, testes, hashes e commit estiverem preservados | Considerar a implementação concluída apenas pela alteração local |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| `ask`, `improve`, `migrate` e `fix` como orquestração autônoma | Dependem de contratos de contexto, impacto, policy e execução estáveis | Yes, after the portable core ships |
| Inferência completa de relações entre todos os tipos de repositório | O primeiro graph deve usar sinais verificáveis e bounded; inferência ampla aumentaria claims não comprovados | Yes, with evidence-backed adapters |
| `apiforge here` como comando separado | A resolução de contexto já deve ser uma capacidade interna reutilizável | Yes, as a UX alias |
| Auto-update e atualização remota de Knowledge Packs | Rede, confiança de fonte, freshness e política de atualização ainda precisam de contratos próprios | Yes, read-only and receipt-backed |
| Symlink como modo de instalação | Falha ou é inconsistente em Windows, containers, WSL, Git e workspaces remotos | Yes, opt-in and capability-checked |
| Sincronização automática que sobrescreva arquivos de host | Gera risco de perda de edição e cruza uma fronteira de mutação sem approval | Yes, only as explicit diff/approval flow |
| Precedência completa até o nível de task | A hierarquia deve começar por defaults, global, workspace e projeto antes de estabilizar níveis finos | Yes, after manifests are stable |
| Debate multiagente distribuído pelo workspace | Exige budgets, leases, replay, authority e evidência distribuída | Yes, bounded and replayable |
| Promessa de paridade funcional total entre hosts | Hosts têm capabilities e limites distintos; paridade precisa continuar per-capability e evidence-backed | Yes, only where observed and proven |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Architecture concept | ✅ | De acordo | Yes — mantido como plataforma instalada com manifests, graph e host activation opcional |
| Resilience and installation | ✅ | Ok; máquinas bloqueadas, rede, segurança, sem admin e prefixo selecionável são requisitos | Yes — hostless core, `APIFORGE_HOME`, PATH, stdio MCP, cache local e `unresolved` foram tornados explícitos |
| YAGNI scope | ✅ | Perfeito; itens adiados devem permanecer no roadmap para o próximo brainstorming | Yes — backlog pós-ship foi registrado explicitamente |

**Minimum Validations:** 2 (to ensure alignment)

---

## Suggested Requirements for /define

Based on this brainstorm session, the following should be captured in the DEFINE phase:

### Problem Statement (Draft)

API Forge precisa deixar de depender de cópias de conhecimento e mirrors dentro de cada repositório e tornar-se uma plataforma instalada, portátil, hostless e evidence-driven, capaz de resolver contexto de um projeto ou workspace multi-repositório sob restrições reais de rede, segurança e privilégios.

### Target Users (Draft)

| User | Pain Point |
|------|------------|
| Desenvolvedor de API | Precisa usar descoberta, contexto, SDD, agents, skills e verificação em qualquer projeto sem copiar o Forge para dentro dele |
| Engenheiro de plataforma | Precisa administrar workspaces virtuais, impacto entre repositórios, caches, manifests, scopes e política de instalação |
| Maintainer de host | Precisa ativar Claude, Devin, Codex, Copilot ou MCP sem assumir paridade inexistente nem tornar o host obrigatório |
| Usuário em ambiente restrito | Precisa instalar em diretório permitido, operar sem admin e continuar usando o máximo possível sem rede ou provider externo |

### Success Criteria (Draft)

- [ ] API Forge pode ser instalado em modo global, user-local, virtual environment, prefixo escolhido ou diretório permitido, sem exigir admin.
- [ ] A resolução de contexto encontra projeto, repositório e workspace sem depender do diretório de instalação do Forge.
- [ ] `inspect`, `init`, `status`, `doctor` e `context` funcionam sem host externo, porta de rede ou provider remoto.
- [ ] Agents, skills, regras, SDD, graph, evidência e verificação permanecem utilizáveis em modo offline ou com capabilities opcionais ausentes.
- [ ] `.apiforge/project.yaml` e `workspace.yaml` são mínimos, versionados e compatíveis com repositórios independentes.
- [ ] Scopes repo, workspace e target limitam o contexto por impacto e preservam evidências, hashes e `unresolved`.
- [ ] O graph distingue relações observadas, declaradas e inferidas, sem converter heurística em fato.
- [ ] MCP local via stdio e host activation são opt-in, plan-only ou approval-gated conforme a operação.
- [ ] Mirrors gerados contêm apenas adapters leves, provenance, source hash e instruções de atualização segura.
- [ ] `doctor` diferencia falha de instalação, permissão, host ausente, rede bloqueada, cache ausente e capability opcional indisponível.
- [ ] README, guias, contratos, documentação de hosts, exemplos, troubleshooting, roadmap e notas de migração descrevem todas as funcionalidades e limites.
- [ ] A entrega preserva testes focados, suíte relevante, receipts, hashes, unresolved diagnostics e um commit rastreável.

### Constraints Identified

- Offline-first no core; rede, provider e freshness externa são capabilities separadas.
- Não assumir privilégios administrativos; suportar prefixos escolhidos pelo usuário e caminhos configurados por ambiente.
- Não usar `HOME`, diretórios globais ou symlink como pressuposto operacional; usar configuração explícita e paths resolvidos de forma segura.
- Não modificar host ou repositório consumidor sem comando explícito, diff, policy e approval quando aplicável.
- Não exigir monorepo; cada repositório mantém seu próprio `.git`.
- Não importar SDKs de provider/modelo no core nem transformar fixtures em prova de produção.
- Preservar compatibilidade CLI/MCP/JSON e os mirrors atuais durante a migração.
- Toda integração externa continua read-only, freshness-aware e receipt-backed até existir gate próprio.
- A documentação precisa evoluir junto com contratos, CLI, MCP, hosts, manifests, segurança e roadmap.

### Out of Scope (Confirmed)

- Orquestração autônoma de alto nível por `ask`, `improve`, `migrate` e `fix` na primeira onda.
- Inferência completa e não bounded de relações entre todos os tipos de repositório.
- Comando separado `apiforge here` antes de a resolução interna de contexto estabilizar.
- Auto-update e atualização remota de Knowledge Packs na primeira onda.
- Symlink como modo padrão ou garantido de instalação.
- Sincronização automática com sobrescrita de arquivos de host.
- Precedência completa até task antes dos manifests básicos.
- Debate multiagente distribuído pelo workspace.
- Paridade funcional total entre hosts sem evidência específica por capability.
- Web UI pesada, mutação automática em providers externos, monorepo forçado ou claims de produção sem receipt independente.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 5 perguntas, incluindo amostras |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 9 itens adiados, nenhum removido do roadmap |
| Validations Completed | 3 checkpoints |
| Duration | uma sessão |

---

## Ship Closure

The feature was implemented, verified and archived on 2026-09-24. The deferred
items listed in the roadmap remain available for a new SDD cycle.

## Next Step

**Archived:** begin the next cycle with `/brainstorm` or `/define` for a new feature.
