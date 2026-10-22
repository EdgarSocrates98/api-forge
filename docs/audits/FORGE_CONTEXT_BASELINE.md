# FORGE_CONTEXT_BASELINE — api-forge

Auditoria do Ciclo 1 (spec `lf-0034`, prompt-fonte `prompt_evo_install2.0.md` §0–§3).
Escopo: somente evidência — todo achado cita o comando que o produziu ou o
arquivo/linha que o sustenta. Nada foi preenchido por suposição.

## Metadados

| Campo | Valor | Evidência |
|---|---|---|
| Repo | `/home/edgar/Documentos/projetos/forjas/api-forge` | — |
| HEAD | `5b3a195601443ae9cd1dd17840dc44b7af331535` | `git log -1` |
| Versão | `0.1.6` | `pyproject.toml` (`name = "apiforge-af"`) |
| Python | `>=3.12` | `pyproject.toml` |
| Build | hatchling, wheel `src/` layout | `pyproject.toml` `[build-system]` |
| CLI | `apiforge`, `apiforge-mcp`, `apiforge-tui` | `[project.scripts]` |
| Wheel publicado | `apiforge_af-0.1.6-py3-none-any.whl` (2.248.045 B) | PyPI JSON API |
| Wheel local | **sha256 idêntico ao publicado** (`ad12e3c9…`) | `sha256sum` comparado |
| sdist publicado | 3.996.353 B | PyPI JSON API |
| sdist local | **148.189.555 B** — contém `.tokensave/` (~711 MB descomprimido) | `tar -tzvf` |

---

## 1. Inspeção de arquitetura (§3.1)

### 1.1 Mapa de módulos

Pacote `src/apiforge/` (~90 entradas de primeiro nível). Relevantes ao contexto:

| Área | Módulo | Papel |
|---|---|---|
| Install lifecycle | `install/service.py` (310 linhas), `install/render.py` (151) | ForgeSpec + render de assets por host |
| Motor de install | `_installkit.py` (1732) | **vendored, byte-idêntico** ao canônico `the-forge/scripts/installkit/forge_installkit.py` e às cópias em `platform-forge` e `data-sentinel-forge` (mesmo md5 `a31bd4f0…`, `_SOURCE_SHA256 = "bc189dd2ae0028ce"`) |
| CLI install | `cli_install.py` (278) + `cli_install_pretty.py` (166) | sub-app typer `install` |
| Assets empacotados | `host_assets/` (`loader.py`, `manifest.yaml`, `templates/`) + `host_assets/{agents,skills}` via force-include | templates de host + árvores canônicas dentro do wheel |
| Distribuição | `distribution/{assets,config,doctor,paths}.py` | `package_root()`, inventário com sha256, diagnóstico |
| Workspace | `workspace/{manifests,service,discovery,graph}.py` | `.apiforge/project.yaml` / `workspace.yaml` próprios |
| Knowledge | `knowledge/{selector,loader,retrieval,levels,freshness,drift,impact,semantic,watch,rewrite}.py` | `default_root()` cai para `apiforge/_data/knowledge` |
| Rules | `rules/` (subpacote, 55 arquivos — `capability_matrix.yaml`, `agent_aliases.yaml`, `routing`…) | catálogo dentro do pacote |
| Evals | `evals/` (módulo) + `evals/paths.py` | resolve `evals/` do cwd ou `apiforge/_data/evals` |
| Agents | `dispatch/mirrors.py`, `cli_agents.py` | `agents sync/check/lint/audit` |
| MCP | `mcp/{server,tools,gateway,surface,main}.py` | SDK `mcp` real (extra); superfícies `full` (154 tools) e `compact` (6) |
| Forge Protocol | `forge/{protocol,doctor,store}.py`, `cli_forge.py` | capabilities/submit/attach/inspect/result/evidence/handoff/health + doctor (delegação forge-doctor-api) |
| Capabilities | `capabilities/{registry,verify,scorecard}.py` | matriz pública (`apiforge capabilities list/verify`) |
| Portal | `portal_adapter.py`, `_forge_portal.py`, `_portal_telemetry.py` | vendored do forge-portal |
| Bootstrap | `scripts/forge_bootstrap.py`, `scripts/forge_installkit.py` | vendored, byte-idênticos (verificado com `cmp -s`) |

### 1.2 CLI — superfície instalável

`apiforge install` existe (sub-app typer, `cli_install.py`). Subcomandos:

```text
apiforge install            # apply (wizard interativo em TTY; plano→confirma)
apiforge install status     # ledger + drift + health
apiforge install doctor     # ledger, drift, .mcp.json, handshake MCP
apiforge install repair     # re-escreve managed drifted/missing
apiforge install update     # upgrade do runtime bootstrap (venv registrada)
apiforge install uninstall  # remove só o que o ledger declara
apiforge install verify     # handshake JSON-RPC real no apiforge-mcp
```

Verbos de descoberta relevantes ao contexto (todos executados na venv limpa,
fora do checkout — ver §4):

| Verbo | Resultado observado |
|---|---|
| `apiforge knowledge list` | 40 packs (`apiforge/_data/knowledge`) |
| `apiforge rules list` | 127 regras em 13 áreas (`apiforge/rules/*.yaml`) |
| `apiforge evals list` | 4 casos de `evals/cases/platform.yaml` via `_data/evals` |
| `apiforge evals validate` | `{'cases': 4, 'ok': True}` |
| `apiforge capabilities list` | 21 capacidades (`rules/capability_matrix.yaml`) |
| `apiforge capabilities verify` | verificação doc/matriz |
| `apiforge forge capabilities` | 21 descritores `forge-protocol/v1` |
| `apiforge forge health` | `state: ok`, 21 capabilities |
| `apiforge forge doctor discover/scan/compare/list/show` | pista de delegação p/ `forge-doctor-api` (GET-only, argv-only) |
| `apiforge distribution inspect` | inventário `host_assets/` + sha256 por arquivo |
| `apiforge next-step --findings …` | roteamento determinístico |
| `apiforge ai` | observa hosts (binary/version/auth/integração) |
| `apiforge agentops hosts` | matriz declarada de hosts (instruction_file, skill_directory, suporte MCP/subagents) |
| `apiforge devin payload|probe|capabilities` | integração Devin |
| `apiforge init` | cria `.apiforge/project.yaml` (manifesto mínimo) |
| `apiforge workspace discover|init|add|status|graph` | workspace multi-repo |
| `apiforge sdd …` | ciclo SDD interno |
| `apiforge agents sync/check/lint/audit` | gerador oficial dos espelhos de agents |

### 1.3 Installkit — canônico vs derivado

| Item | Status | Gerador oficial |
|---|---|---|
| `_installkit.py` | derivado (vendored, byte-idêntico) | `the-forge/scripts/installkit/forge_installkit.py` |
| `scripts/forge_bootstrap.py` | derivado (vendored, byte-idêntico) | `the-forge/scripts/installkit/` |
| `install/service.py`, `install/render.py`, `cli_install.py` | **canônicos desta forja** | edição manual |
| `agents/*.md` (26 coordenadores) + `agents/executors/` (5) | **canônico** | edição manual; lint via `apiforge agents lint` |
| `.claude/agents/*.md`, `.agents/agents/*.md`, `.codex/agents/*.toml`, `.devin/agents/` | derivado | `apiforge agents sync` (`dispatch/mirrors.py`) |
| `.agents/skills/` (15 skills `api-forge-*`) | **canônico** | edição manual; validação `scripts/validate_skills.py` |
| `.claude/skills/`, `.github/skills/`, `.devin/skills/` | derivado | `scripts/sync_skills.py` (copia `.agents/skills`) |
| `forge.json`, `forge.agentic.json` | **canônico** | edição manual (contrato the-forge bootstrap/delegação) |
| `vendor/MANIFEST.sha256` | derivado | `scripts/vendor_caveman.py` (cobre `vendor/caveman`, `vendor/cavekit` — **não** assets de install) |
| `.devin/config.json`, `.devin/hooks.v1.json` | **canônico** | edição manual (camada Devin nativa) |
| `AGENTS.md`, `CLAUDE.md`, `AGENT_PROTOCOL.md` (raiz) | **canônico** | edição manual |
| `knowledge/` (40 packs, 1,8 MB) | **canônico** | edição manual + gates de proveniência |
| `evals/` (349 arquivos) | **canônico** | edição manual |
| `docs/installation/*.md` (15 docs) | **canônico** | edição manual |

**Ausências de integridade no estilo installkit maduro:** data-sentinel-forge
mantém `src/data_sentinel/installation/assets/MANIFEST.sha256` — manifesto de
hashes da árvore de assets empacotada. api-forge não tem equivalente estático;
em vez disso (a) `distribution inspect` emite inventário com sha256 em runtime
e (b) o ledger `.apiforge/install/install-ledger.json` registra sha256 por
arquivo managed no alvo. O `.apiforge/install/` contém `components.json`,
`install-ledger.json`, `receipts/` — verificado em `/tmp/af-target`.

### 1.4 Host integration e MCP adapters

- `install/render.py`: `HOSTS = ("claude","devin","codex","copilot")`.
  Mapeamento de diretórios: claude→`.claude/{agents,skills}`,
  devin→`.devin/{agents,skills}` + superfície `.agents/`,
  codex→`.agents/{agents,skills}` (+`.codex` declarado em `_host_dirs`),
  copilot→`.github/{agents,skills}` + `.agents/`.
  Agentes copilot são emitidos como `<name>.agent.md`.
- `.mcp.json`: chave gerenciada `mcpServers.apiforge` + bloco
  `_forge_managed.api-forge` — merge preserva servidores estranhos
  (`_installkit.py` `mcp_set`/`mcp_unset`, linhas 459–488).
- MCP server: `apiforge-mcp` (SDK `mcp`, extra opcional). Superfícies:
  `full` = 154 tools, `compact` = 6 gateway tools
  (`apiforge_discover|call|context|expand|analyze|evidence`) — medido via
  `python -c` na venv limpa.
- Doctor reporta `mcp-handshake UNVERIFIED` quando o extra `mcp` não está
  instalado — recusa honesta, não falso PASS.

---

## 2. Matriz de recursos (§3.2)

Colunas preenchidas **só com evidência executada** (venv `/tmp/af-venv`,
alvo `/tmp/af-target`, `HOME=/tmp/af-home2` isolada). "Descoberto pelo host"
= arquivo/material que um host consegue encontrar por convenção ou por
ponteiro instalado — não há teste com host real nesta auditoria; células sem
prova direta estão marcadas `não verificado`.

| Recurso | Existe na fonte | Está no wheel | Instalado no alvo | Descoberto pelo host | Utilizável | Verificado |
|---|---|---|---|---|---|---|
| Skills | SIM — `.agents/skills/` (15) | SIM — `apiforge/host_assets/skills/` (force-include) | SIM — `.claude/skills`, `.devin/skills`, `.github/skills`, `.agents/skills` (25 arquivos/dir) | convenção de diretório dos hosts (`.claude`, `.devin`, `.agents`, `.github`) | SIM — SKILL.md íntegro | SIM — `install --yes` escreveu; `doctor` PASS |
| Agents | SIM — `agents/*.md` (26) + `agents/executors/` (5) | SIM — `host_assets/agents/` (inclui `executors/`) | PARCIAL — 26 por host dir; **`executors/` não é renderizado** (render.py itera só `glob("*.md")` no topo) | convenção de diretório | SIM (coordenadores); executores rodam inline por design (subagent não dispara subagent) | SIM — contados 26/dir |
| MCP | SIM — `apiforge-mcp` + `mcp/{server,tools,gateway}` | SIM — entry point + código | SIM — `.mcp.json` chave gerenciada `mcpServers.apiforge` | SIM — `.mcp.json` na raiz do projeto | condicional — exige extra `mcp` instalado | PARCIAL — handshake `UNVERIFIED` sem extra; `install verify` existe |
| Knowledge | SIM — `knowledge/` (40 packs) | SIM — `apiforge/_data/knowledge` (411 arquivos) | **NÃO copiado** — acessado via pacote | **NÃO** — nada no alvo aponta para `knowledge list` | SIM — `knowledge list` → 40 packs | SIM — comando executado |
| Rules | SIM — `apiforge/rules/*.yaml` (55) | SIM — dentro do pacote | **NÃO copiado** | **NÃO** — idem | SIM — `rules list` → 127 regras/13 áreas | SIM |
| Evals | SIM — `evals/` (349 arq.) | SIM — `apiforge/_data/evals` | **NÃO copiado** | **NÃO** | SIM — `evals list/validate` | SIM |
| Protocols | SIM — `AGENT_PROTOCOL.md` (raiz, 113 linhas) + `forge.protocol` | SIM — `host_assets/AGENT_PROTOCOL.md` | **NÃO copiado** — fica dentro do site-packages | **NÃO** — skills mandam ler `AGENT_PROTOCOL.md` mas o arquivo não existe no workspace | SIM via pacote; **quebrado via path relativo** | SIM — `find /tmp/af-target` confirma ausência |
| Verificadores | SIM — `install doctor`, `capabilities verify`, `agents check`, `validate_skills.py`, `evals *` | SIM (código no pacote) | n/a — roda no runtime nativo | **NÃO** — sem ponteiro instalado | SIM | SIM — doctor executado |
| Políticas | SIM — AGENTS.md/AGENT_PROTOCOL.md (raiz), `rules/`, `.devin/hooks.v1.json` | PARCIAL — AGENT_PROTOCOL no wheel; AGENTS.md/CLAUDE.md da raiz **não** são assets de consumidor | **NÃO** — só marcador de 6 linhas em AGENTS.md | PARCIAL — marcador existe mas não roteia para protocolo/regras | PARCIAL | SIM |
| Manifesto de capacidades | `forge.json` + `forge.agentic.json` (raiz) + `capabilities list`/`forge capabilities` | **NÃO** — `forge.json`/`.agentic.json` não entram no wheel (`unzip -l` confirma ausência) | **NÃO** — nenhum manifesto é escrito no alvo | **NÃO** — só via `~/.forge/installations/api-forge.json` (global, não no workspace) | SIM via CLI | SIM |
| Registry de contexto (`.forge/context/`) | **NÃO existe** | n/a | **NÃO** | **NÃO** | **NÃO** | SIM — ausência confirmada |

### 2.1 Evidência bruta principal

```text
$ HOME=/tmp/af-home2 /tmp/af-venv/bin/apiforge install --yes     # em /tmp/af-target
status: completed · files: 204 · markers: [AGENTS.md api-forge]
mcp: [{'action':'created','file':'.mcp.json','key':'managed:api-forge','server':'apiforge'}]
checks: files-written PASS (204 writes) · mcp-scope:codex NOT_APPLICABLE
verification: PASS

$ find /tmp/af-target -type f | wc -l      # 210 (204 managed + AGENTS.md + .mcp.json + estado)
$ ls .apiforge/install/                    # components.json install-ledger.json receipts/

$ /tmp/af-venv/bin/apiforge install doctor # em /tmp/af-target
status: healthy — ledger PASS · mcp-config PASS · mcp-handshake UNVERIFIED · forge-portal NOT_APPLICABLE

$ /tmp/af-venv/bin/apiforge install uninstall --purge
removed: 206 kept: 0 status: completed
# mas /tmp/af-home/.forge/installations/api-forge.json PERMANECE (stale)
```

---

## 3. Análise do instalador (§3.3)

Arquitetura: `cli_install.py` → `install/service.py` (ForgeSpec) →
`_installkit.py` (motor compartilhado: `resolve_scope`, `Ledger`, lock,
journal com rollback, marker blocks, `.mcp.json` managed, receipts,
`~/.forge` registry) → `install/render.py` (assets por host).

| Aspecto | Implementação observada |
|---|---|
| Resolução do alvo | `resolve_scope` (`_installkit.py:547`): `--root` explícito → senão `.git` mais próximo → senão ancestral com `.apiforge/install` (state root) → senão recusa `FORGE-INSTALL-NOT-A-REPO` |
| `scope=project` | raiz VCS/estado; escreve `<root>/.apiforge/install/` |
| `scope=workspace` | ancestral com `forge.workspace.{yaml,json}`, `.forge-workspace` ou `pyproject.toml` com `tool.forge.workspace`/`tool.uv.workspace`; fallback = resolução de projeto (`_installkit.py:507–524`) |
| `scope=user` | `$HOME`; state em `~/.apiforge` (`user_state_dir`) |
| Assets copiados | skills (byte-a-byte) e agents (render por host) → `.claude`, `.devin`, `.github`, `.agents` (+marker AGENTS.md/CLAUDE.md, `.mcp.json`) |
| Assets referenciados | knowledge/rules/evals — **nunca copiados**; resolvidos em runtime via `apiforge/_data/` (wheel) ou checkout |
| Assets ignorados | `agents/executors/` (não renderizado), `AGENT_PROTOCOL.md` (não copiado), `forge.json`/`forge.agentic.json`, `docs/`, `tests/`, `vendor/`, `factory/` |
| Merge | marker blocks `<!-- api-forge:managed:begin/end -->` em AGENTS.md/CLAUDE.md; `.mcp.json` chave gerenciada preservando servidores alheios |
| Ownership | ledger sha256 por arquivo; arquivo pré-existente idêntico = "adopted" (não vira managed); diferente = pulado "user-owned"; conflito nunca sobrescrito |
| Uninstall | remove só `owned_paths()` do ledger; excisa marker blocks mantendo conteúdo do usuário; `mcp_unset` remove só a chave gerenciada; `--purge` rmtree do state dir |
| Repair | re-escreve managed missing/drifted; entradas sem fonte canônica → `skipped` |
| Update | `pip install --upgrade <checkout registrado>` na venv do bootstrap — exige `~/.forge/installations/api-forge.json` com `source.path`+`venv`; `latest` recusado |
| Host selection | `--host all|none|csv` validado contra `render.HOSTS`; `none` nunca vira `all` |
| Perfis | `minimal` = config+mcp+marker+state; `recommended`/`full` = +skill+agent; `--components skills,agents,mcp,tui,graph-studio` restringe/seleciona; `--gateway-profile economy|balanced|deep` gravado em `components.json` |
| Registry | `~/.forge/installations/api-forge.json` (`forge/InstallationManifest/v1`) escrito no apply |
| Lock | `.install.lock` no state dir (`acquire_lock`) |
| Rollback | journal: snapshot pré-escrita em `state/backups/` + remoção de criados em falha |

### 3.1 Desvios frente à referência madura (data-sentinel-forge)

A mesma `_installkit.py` é compartilhada, mas o `service.py` de data-sentinel
corrige problemas que o de api-forge **não** corrige:

| # | data-sentinel | api-forge |
|---|---|---|
| 1 | `_check_python()` recusa abaixo do piso | **ausente** — depende só do `requires-python` do pip |
| 2 | `marker_files=()` no escopo user (M12) | **`~/AGENTS.md` é escrito** — observado: `/tmp/af-home/AGENTS.md` criado |
| 3 | `user_state_dir="~/.data-sentinel/install"` aninhado (H1) | `user_state_dir="~/.apiforge"` — `uninstall --scope user --purge` apagaria `~/.apiforge` inteiro |
| 4 | `kit.deregister_installation()` no uninstall (M3) | **ausente** — `api-forge.json` fica stale após uninstall (observado) |
| 5 | `install_root = ctx.root` real (M3) | `install_root = ~/.forge/installs/api-forge` — **caminho fantasma** (observado no manifesto) |
| 6 | `distribution="data-sentinel"` = nome real do dist | registry grava `distribution: "apiforge"` — o dist real é `apiforge-af` (M1) |
| 7 | `_detect_source()` repo/copied-tree/installed no recibo | ausente — recibo não registra a origem |
| 8 | `environment` verb (§11.1) | ausente |

---

## 4. Diagnóstico PyPI (§3.4)

Procedimento executado (sem `pip install -e .` em nenhum passo):

```bash
.venv/bin/python -m build --outdir /tmp/af-dist .   # wheel + sdist
python3 -m zipfile -l /tmp/af-dist/apiforge_af-0.1.6-py3-none-any.whl
tar -tzvf /tmp/af-dist/apiforge_af-0.1.6.tar.gz
python3 -m venv /tmp/af-venv && /tmp/af-venv/bin/pip install /tmp/af-dist/*.whl
mkdir /tmp/af-target && cd /tmp/af-target && git init .
HOME=/tmp/af-home2 /tmp/af-venv/bin/apiforge install --yes
```

### 4.1 Conteúdo real do wheel (`unzip -l`, resumo)

| Árvore | Arquivos | Origem |
|---|---|---|
| `apiforge/` código | ~1671 | `src/apiforge` |
| `apiforge/host_assets/agents/` | 31 (26 + `executors/` 5) | force-include `agents/` |
| `apiforge/host_assets/skills/` | ~25 | force-include `.agents/skills/` |
| `apiforge/host_assets/AGENT_PROTOCOL.md` | 1 | force-include |
| `apiforge/_data/knowledge/` | 411 | force-include `knowledge/` |
| `apiforge/_data/evals/` | 349 | force-include `evals/` |
| `apiforge/_data/tests/fixtures/` | 163 | force-include `tests/fixtures/` |
| `apiforge/portal_assets/` | 46 | force-include `portal/assets/` |
| `apiforge/rules/` | 55 | subpacote normal |
| `forge.json` / `forge.agentic.json` | **0 — ausentes do wheel** | só na raiz/sdist |

### 4.2 Prova funcional fora do checkout

- `apiforge --version` → `apiforge 0.1.6` ✔
- `apiforge install --yes` → 204 arquivos, marker, `.mcp.json` ✔
- `knowledge list` 40 packs · `rules list` 127 regras · `evals validate` ok
  · `capabilities list`/`forge capabilities` 21 · `forge health` ok ✔
- `install doctor` → `healthy` (`mcp-handshake UNVERIFIED` — extra `mcp`
  não instalada na venv limpa; recusa honesta) ✔
- `install status/doctor/uninstall/repair` ciclo completo ✔
- `distribution inspect` → inventário com sha256 ✔

### 4.3 Comparativo com o publicado (0.1.6)

| Artefato | Local | PyPI | Nota |
|---|---|---|---|
| wheel sha256 | `ad12e3c9…` | `ad12e3c9…` | **byte-idêntico — build reproduzível** |
| sdist | 148 MB | 4,0 MB | ver abaixo |

### 4.4 sdist local vs publicado — vazamento de `.tokensave/`

`tar -tzvf` do sdist local mostra:

```text
437878784  apiforge_af-0.1.6/.tokensave/tokensave.db
273247760  apiforge_af-0.1.6/.tokensave/tokensave.db-wal
   294912  apiforge_af-0.1.6/.tokensave/tokensave.db-shm
```

Causa-raiz: `.tokensave/` está excluído apenas em `.git/info/exclude` (linha 7
— exclusão **local**, não commitada). O `.gitignore` do repo não o lista;
hatchling inclui qualquer arquivo não ignorado no sdist. O pipeline
`publish-pypi.yml` constrói em CI limpo — por isso o sdist publicado tem 4 MB
e está limpo. O risco materializa em **publicação manual a partir de checkout
sujo**: ~711 MB de estado de desenvolvedor (cache TokenSave) iria para o PyPI.

O sdist também carrega o repo inteiro: `docs/` (1384 itens), `tests/`,
`vendor/`, `.claude/`, `.agents/`, `.devin/`, `.codex/`, `portal/`, `factory/`
(1 item — `runs/2026-10-15.cyc9-06.md` do loop-factory), `graphify-out/`…

---

## 5. Gaps, causa-raiz, riscos, decisões, migração (§3.5)

### P0 — quebra a promessa central do install 2.0

**P0-1 · `AGENT_PROTOCOL.md` não chega ao consumidor; skills instaladas
referenciam arquivo inexistente.**
- Evidência: `/tmp/af-target/.agents/skills/api-forge-core/SKILL.md:33` —
  `Leia AGENT_PROTOCOL.md`; `find` no alvo: ausente. Está no wheel
  (`host_assets/AGENT_PROTOCOL.md`) mas `install` não o copia e o marcador
  em AGENTS.md não o menciona.
- Causa-raiz: `install/render.py` só renderiza agents+skills; o contrato
  operacional ficou empacotado mas sem rota de entrega/descoberta.
- Risco: o host instala, vê skills, segue a instrução e bate em arquivo
  inexistente → protocolo (case-first, next-step, AF-* codes) não aplicado.
- Decisão proposta: instalar `AGENT_PROTOCOL.md` na raiz do alvo (ou bloco
  gerenciado apontando para `apiforge/host_assets/AGENT_PROTOCOL.md` via
  caminho resolvido por verbo, ex.: `apiforge protocol print`).

**P0-2 · Nenhum registry/manifesto de contexto no workspace.**
- Evidência: após install, `/tmp/af-target` não tem `.forge/context/`,
  `forge.json` nem manifesto de capacidades — só `.apiforge/install/` +
  `~/.forge/installations/api-forge.json` (global, fora do workspace).
- Causa-raiz: o contrato `forge-context/v1` (§4 do prompt) ainda não existe;
  o registry atual é o `forge/InstallationManifest/v1` global do installkit.
- Decisão proposta: emitir `.forge/context/registry.json` +
  `capabilities/api-forge.json` + `ROUTING.md` no apply — o receipt já tem
  `forge_id`, hosts, profile, paths; o material está todo disponível.

**P0-3 · Knowledge/Rules/Evals/Verificadores não têm ponteiro de descoberta
no workspace.**
- Evidência: recursos respondem via CLI (`knowledge list` → 40), mas nada no
  alvo diz ao host que existem — o marcador fala só de MCP+skills+agents.
- Causa-raiz: o marcador/markers do installkit é o único canal de instrução
  instalado; falta o "entry point" que o §5 do prompt pede (AGENTS.md
  consumidor + AGENT_PROTOCOL.md + referência ao registry).
- Decisão proposta: ampliar `marker_body` (ou AGENTS.md consumidor gerado)
  para citar: `apiforge knowledge list|select`, `rules list|lookup`,
  `capabilities list`, `forge capabilities`, `install doctor`, local do
  `AGENT_PROTOCOL.md`.

### P1 — regressões/divergências vs referência madura e contratos

**P1-1 · Registry `~/.forge/installations/api-forge.json` fica stale após
uninstall** — `service.uninstall` não chama `kit.deregister_installation()`
(data-sentinel M3). Evidência: arquivo persistiu após `uninstall --purge`.

**P1-2 · `install_root` fantasma + `distribution` errado no registry** —
grava `~/.forge/installs/api-forge` (inexistente) e `distribution:
"apiforge"` (real: `apiforge-af`). Corrigir como data-sentinel M3/M1.

**P1-3 · Escopo user escreve `~/AGENTS.md` e coloca estado em `~/.apiforge`
sem aninhar** — nenhum host lê `~/AGENTS.md` (data-sentinel M12) e
`uninstall --scope user --purge` apagaria `~/.apiforge` inteiro, onde podem
viver outros estados (H1). Evidência: `/tmp/af-home/AGENTS.md` criado.

**P1-4 · sdist local vaza `.tokensave/` (~711 MB)** — exclusão só em
`.git/info/exclude`. Decisão: adicionar `.tokensave/` ao `.gitignore`
commitado e/ou `tool.hatch.build.targets.sdist` excludes; gate de conteúdo
de sdist no CI (hoje só wheel é inspecionado).

**P1-5 · Assets de agents: `executors/` empacotado mas não renderizado** —
o wheel carrega `host_assets/agents/executors/` (5 arquivos), o render
ignora subdirs. Coerente com a fronteira "subagent não dispara subagent"
(mesmo desenho do spark-forge-aws), mas é empacotamento sem consumo —
decidir: remover do wheel ou documentar como deliberado.

**P1-6 · Sem verificador de integridade da árvore instalada no nível de
pacote** — data-sentinel tem `installation/assets/MANIFEST.sha256`; aqui o
ledger cobre drift no alvo e `distribution inspect` cobre o pacote em
runtime. Aceitável, mas falta um manifesto declarativo assinável/auditável
dos assets canônicos (skills/agents/AGENT_PROTOCOL) — decisão: avaliar
`MANIFEST.sha256` gerado no build (já existe `test_artifact_contents.py`
como gate de presença).

**P1-7 · `install` sem `_check_python()` e sem `detect_source` no recibo** —
recusa honesta de piso de Python depende do pip; cópia de árvore (copied-tree)
não é detectada/registrada (data-sentinel §8.1/§8.4).

### P2 — assimetrias e economia de contexto

- **P2-1** — codex no install recebe só `.agents/` (`.codex/agents/*.toml`
  existe como espelho de repo via `agents sync`, não no install). Avaliar
  emitir `.codex/agents/*.toml` — hoje `_host_dirs` declara `.codex` mas o
  render não produz.
- **P2-2** — verb `environment` (§11.1 do contrato) ausente; `apiforge ai`
  cobre hosts, mas o relatório de ambiente (tools/env/registry) não existe.
- **P2-3** — `install update` depende do registro do bootstrap; sem
  `source.path`+`venv` devolve `BLOCKED` — correto, mas sem auto-reparo.
- **P2-4** — marker_body tem 6 linhas e não cita `next-step`/`case` —
  o mínimo de roteamento (carregar/criar `.apiforge/case`, `next-step`
  antes de escolher coordenador) só existe dentro das skills.
- **P2-5** — `forge.json`/`forge.agentic.json` não entram no wheel — o
  manifesto de delegação fica indisponível p/ consumidores wheel; avaliar
  incluir como package data.
- **P2-6** — sdist carrega `docs/`, `tests/`, `vendor/`, `factory/` —
  sdist é "repo tarball"; aceitável, mas combinar com P1-4 para endurecer
  excludes.

### Plano de migração proposto (ordem sugerida)

1. Criar contrato `forge-context/v1`: `.forge/context/registry.json` +
   `capabilities/api-forge.json` + `ROUTING.md` escritos pelo installkit
   (P0-2) — adaptável sobre `forge/InstallationManifest/v1` existente.
2. Entregar `AGENT_PROTOCOL.md` ao consumidor + ampliar marcador com o
   mapa de descoberta (P0-1, P0-3, P2-4).
3. Alinhar `service.py` às correções M1/M3/M12/H1 da referência
   (P1-1…P1-3) — mudança pequena e isolada, com testes e2e existentes.
4. Endurecer sdist: `.gitignore` + excludes + gate de conteúdo (P1-4, P2-6).
5. Resolver `executors/` (remover do bundle ou instalar) e `.codex/agents`
   toml no install (P1-5, P2-1).
6. Adicionar `environment` verb + `protocol print` (P2-2, P0-1).

### Compatibilidades observadas

- Wheel byte-idêntico ao publicado → build reproduzível/determinístico.
- `install` funciona do wheel sem checkout (força do desenho force-include).
- Recusas honestas: `mcp-handshake UNVERIFIED` sem extra; `E_NOTAPPROVED`
  sem `--yes`; `E_NOTREPO` fora de repo; rollback em falha.
- Ledger + marker + `.mcp.json` managed: merge não destrutivo, uninstall
  só toca no próprio (verificado com uninstall completo: `removed: 206`).
- e2e `tests/e2e/test_install_lifecycle.py` + `tests/test_artifact_contents.py`
  + `tests/distribution/` cobrem lifecycle e conteúdo de wheel.
- CI: `ci.yml` (agents check, skills mirrors, capabilities verify, ruff,
  testes) + `publish-pypi.yml` (version gate, twine, checksums, trusted
  publishing OIDC, verify pós-publicação).

## Apêndice — comandos executados

```text
git log -1 --format='%H %s'                                   # 5b3a195…
md5sum src/apiforge/_installkit.py                            # a31bd4f0… == siblings
cmp -s scripts/forge_installkit.py src/apiforge/_installkit.py  # IDÊNTICO
.venv/bin/python -m build --outdir /tmp/af-dist .
python3 -m zipfile -l /tmp/af-dist/apiforge_af-0.1.6-py3-none-any.whl
tar -tzvf /tmp/af-dist/apiforge_af-0.1.6.tar.gz | sort -k3 -rn | head
sha256sum /tmp/af-dist/*.whl                                  # == PyPI
python3 -m venv /tmp/af-venv; /tmp/af-venv/bin/pip install …whl
cd /tmp/af-target && git init
HOME=/tmp/af-home2 /tmp/af-venv/bin/apiforge install --yes
/tmp/af-venv/bin/apiforge install status|doctor|repair|uninstall|verify
/tmp/af-venv/bin/apiforge knowledge list|rules list|evals list|evals validate
/tmp/af-venv/bin/apiforge capabilities list|forge capabilities|forge health
/tmp/af-venv/bin/apiforge distribution inspect|agentops hosts|devin capabilities
/tmp/af-venv/bin/apiforge install --scope user --yes           # ~/AGENTS.md escrito
```
