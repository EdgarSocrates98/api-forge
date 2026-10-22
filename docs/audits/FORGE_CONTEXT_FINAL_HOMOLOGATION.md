# FORGE_CONTEXT_FINAL_HOMOLOGATION — api-forge

Relatório final do programa Install 2.0 (spec-fonte
`prompt_evo_install2.0.md` §12.6), cobrindo os ciclos 2–7 executados sobre a
baseline `docs/audits/FORGE_CONTEXT_BASELINE.md` (ciclo 1, lf-0034).
Documento de evidência: cada afirmação cita commit/PR, arquivo:linha ou
comando executado. O que não foi executado está marcado **NÃO EXECUTADO**
(§16 — nenhum teste não executado é reportado como sucesso).

## Metadados

| Campo | Valor | Evidência |
|---|---|---|
| Repo | `/home/edgar/Documentos/projetos/forjas/api-forge` | — |
| SHA antes | `5b3a195601443ae9cd1dd17840dc44b7af331535` | tag `v0.1.6` (2026-10-21), mesma HEAD do baseline |
| SHA depois | `98755ad7461fe095831738931ef7aeb0c28267f9` | `git log -1` em `main` |
| Versão | `apiforge-af` 0.1.6 → **0.2.0** | `pyproject.toml` (bump em worktree, **pendente de publicação** — §10) |
| Python | `>=3.12` | `pyproject.toml` |
| CLI | `apiforge`, `apiforge-mcp`, `apiforge-tui` | `[project.scripts]` |
| Data | 2026-10-22 | — |

---

## 1. SHAs antes/depois

| | SHA | Descrição |
|---|---|---|
| Tag base / baseline | `5b3a195601443ae9cd1dd17840dc44b7af331535` | `release: 0.1.6 — forge doctor governed delegation to forge-doctor-api` |
| HEAD final | `98755ad7461fe095831738931ef7aeb0c28267f9` | `fix(install): installkit 1.0.1 — stale-lock created_at + backport bootstrap fixes (#107)` |

Range medido: `git log v0.1.6..HEAD` → **19 commits**, `git diff --stat` →
**34 arquivos, +9.488/−2.169 linhas**.

## 2. PRs

Todos os PRs mergeados em `EdgarSocrates98/api-forge`, verdes no CI no
momento do merge.

| PR | Merge / squash | Conteúdo |
|---|---|---|
| #97 | `ea75984` (merge), `dcef59d` | docs(audit): FORGE_CONTEXT_BASELINE (lf-0034) |
| #98 | `fbe3be4` (merge), `e054460` | feat(context): `forge/context/v1` — vendored registry + install wiring (ciclo 2) |
| #99 | `262a297` (merge), `e2927c1` | fix(build): `.gitignore` `.tokensave` + local mcp config — **sdist leak** (P1-4 do baseline) |
| #100 | `e00c720` (merge), `5523f8b` | feat(context): consumer-docs layer — blocos `forge:*` + AGENT_PROTOCOL.md consolidado (ciclo 3, lf-0036) |
| #101 | `c343c74` (merge), `613756e` `99e0014` `eb358b0` `78386e4` | feat(install): wheel distribution parity + wheel isolation test (lf-0039 §8); discovery lf-0037 (verbs §6.2 + knowledge pointers); fix §8.2 `_data` manifests + `default_root` ignora stubs sem `pack.yaml`; `uv.lock` sync |
| #102 | `b5d5f52` (squash) | fix(lint): PLW1510/RUF100/ISC004 no wheel isolation test |
| #103 | `b41030d` (squash) | fix(installkit): `_forgecontext` v1.2.1 — `timezone.utc` p/ Python 3.10 |
| #104 | `fd7e853` (squash) | feat(evals): lf-0038 §7 — evals classification + verification |
| #105 | `6bd01b2` (squash) | fix(tests): **windows parity** + ruff format — `discovery.knowledge_get` com `is_relative_to()` (separador hardcoded quebrava refs no Windows), `_run` com encoding/errors |
| #106 | `d7d2683` (squash) | feat(install): transactional context registry — vendored `_forgecontext` v1.3.0 (lf-0040, ciclo 7) |
| #107 | `98755ad` (squash) | fix(install): installkit 1.0.1 — stale-lock `created_at` + backports do bootstrap |

## 3. Commits

19 commits no range (`git log v0.1.6..HEAD --format='%h %s'`, ordem cronológica):

```text
dcef59d docs(audit): FORGE_CONTEXT_BASELINE — install-context baseline (lf-0034 cycle 1)
ea75984 Merge pull request #97 (audit/install-context)
e054460 feat(context): forge/context/v1 — vendored registry + install wiring (ciclo 2)
fbe3be4 Merge pull request #98 (cycle/install-context)
e2927c1 fix(build): gitignore .tokensave + local mcp config — sdist leak
262a297 Merge pull request #99 (fix/sdist-tokensave-leak)
5523f8b feat(context): consumer-docs layer — blocos forge:* + AGENT_PROTOCOL.md consolidado (lf-0036)
e00c720 Merge pull request #100 (cycle/install-context-docs)
613756e feat(install): wheel distribution parity — forge manifests packaged + wheel isolation test (lf-0039 §8)
99e0014 discovery: lf-0037 install-time §6.2 retrieval verbs + knowledge pointers
eb358b0 chore(deps): uv.lock sync — apiforge-af 0.1.3 -> 0.1.6
78386e4 fix(install+knowledge): _data manifests + default_root ignora stubs sem pack.yaml (lf-0039 §8.2)
c343c74 Merge pull request #101 (cycle/install-context)
b5d5f52 fix(lint): PLW1510/RUF100/ISC004 no wheel isolation test (#102)
b41030d fix(installkit): _forgecontext v1.2.1 — timezone.utc p/ Python 3.10 (#103)
fd7e853 feat(evals): lf-0038 install-2.0 §7 — evals classification + verification (#104)
6bd01b2 fix(tests): windows parity + ruff format (#105)
d7d2683 feat(install): transactional context registry — vendored _forgecontext v1.3.0 (lf-0040) (#106)
98755ad fix(install): installkit 1.0.1 — stale-lock created_at + backport bootstrap fixes (userinfo regex, argv trim, smoke vazio) (#107)
```

## 4. Arquivos modificados

`git diff --name-only v0.1.6..HEAD` → 34 arquivos. Agrupados:

| Grupo | Arquivos |
|---|---|
| Vendored | `src/apiforge/_forgecontext.py` (novo, v1.3.1, `_SOURCE_SHA256 = "e72e93eab21ade74"`), `src/apiforge/_installkit.py` (v1.0.1, `4c446922f5e77a0c`), `scripts/forge_installkit.py`, `scripts/forge_bootstrap.py` (v1.1.1) |
| Wiring de produção | `src/apiforge/install/service.py` (`install_transaction`/`uninstall_transaction` em `:605`/`:635`, `_context_manifest`, `_LEGACY_DOC_TAGS`, `repair_docs` em `:205`), `src/apiforge/install/render.py` (knowledge pointer stubs, lf-0037), `src/apiforge/discovery_ops.py` (novo — fonte única §6.2+§7.2), `src/apiforge/discovery.py`, `src/apiforge/cli.py` (verbos `capabilities`, `context`, `evals`), `src/apiforge/evals/catalog.py`, `src/apiforge/knowledge/selector.py` |
| Empacotamento | `pyproject.toml` (force-include `forge.json`/`forge.agentic.json` → `apiforge/_data/`), `.gitignore` (`.tokensave/` commitado — fix do leak) |
| Docs | `docs/audits/FORGE_CONTEXT_BASELINE.md`, `docs/install/DISTRIBUTION_PARITY.md`, `docs/evals-taxonomy.md`, `docs/catalog-contract.md`, `docs/INDEX.md`, `docs/knowledge-program/*` (6 artefatos), `docs/reference/*` |
| Testes | `tests/e2e/test_install_lifecycle.py` (28 testes), `tests/test_wheel_isolation.py`, `tests/test_evals_cycle5.py` (10), `tests/test_discovery_ops.py` (6), `tests/test_artifact_contents.py` |
| Deps | `uv.lock` (sync 0.1.3→0.1.6) |

## 5. Gaps corrigidos

Mapeamento gap do baseline (§5) → correção entregue:

| Gap baseline | Status | Evidência |
|---|---|---|
| **P0-1** — `AGENT_PROTOCOL.md` não chega ao consumidor (skills citam arquivo inexistente) | **CORRIGIDO** | consumer-docs do `_forgecontext.py` grava `AGENT_PROTOCOL.md` consolidado na raiz do alvo (`_CONSUMER_DOCS`, `service.py:377`); commit `5523f8b` |
| **P0-2** — nenhum registry/manifesto de contexto no workspace | **CORRIGIDO** | `.forge/context/registry.json` + `capabilities/api-forge.json` + `ROUTING.md`; commits `e054460`, `d7d2683` |
| **P0-3** — Knowledge/Rules/Evals/Verificadores sem ponteiro de descoberta | **CORRIGIDO** | manifesto `forge/context/v1` declara `discovery.commands`/`ops` (§6.2), `eval_suites`, `resources`, `mutating_verbs`; verbos `capabilities`, `knowledge`, `rules`, `evals`, `context` na CLI; commits `99e0014`, `fd7e853` |
| **P1-4** — sdist local vaza `.tokensave/` (~711 MB) | **CORRIGIDO** | `.tokensave/` commitado no `.gitignore` (linha 28); commit `e2927c1` (PR #99) |
| — `forge.json`/`forge.agentic.json` fora do wheel (P2-5) | **CORRIGIDO** | force-include → `apiforge/_data/` (`pyproject.toml:102-103`); leitor `_PKG_DIR`-aware (`service.py:371-373`); commits `613756e`, `78386e4` |
| — refs `knowledge/*` mortas nos mirrors instalados (mesma classe do AWS P0-2) | **CORRIGIDO** | `install/render.py:148-188` emite pointer stub por ref (`knowledge/<rel>` → verbos nativos); commit `99e0014` |
| — install/uninstall multi-forge transacional (ciclo 7) | **CORRIGIDO** | `fctx.install_transaction`/`uninstall_transaction` wired (`service.py:605`,`:635`); `_forgecontext` v1.3.1; commit `d7d2683` |
| — evals sem classificação §7 | **CORRIGIDO** | `evals/catalog.py` + `evals list|describe|run|result` + `eval_suites[].kind`; commit `fd7e853` |
| — `_forgecontext` incompatível com py3.10 | **CORRIGIDO** | v1.2.1 `timezone.utc`; commit `b41030d` |
| — `knowledge_get` com separador hardcoded quebrava refs no Windows | **CORRIGIDO** | `Path.is_relative_to()`; commit `6bd01b2` |
| — installkit 1.0.0 / bootstrap 1.1.0 | **CORRIGIDO** | `_installkit.py` v1.0.1 + `forge_bootstrap.py` v1.1.1 byte-idênticos ao canônico; commit `98755ad` |

## 6. Gaps restantes

- **E2E real de hosts (§10.2) — NÃO EXECUTADO** (ciclo 8 pendente; ver §9).
- **Economia/observabilidade (ciclo 9, §11) — pendente.**
- **Publicação PyPI — pendente** (§10).
- **P1-1** — registry `~/.forge/installations/api-forge.json` continua
  stale após uninstall: `service.py` não chama
  `kit.deregister_installation()` (verificado: `grep deregister
  src/apiforge/install/service.py` → vazio; a função existe só no
  installkit).
- **P1-2** — registry global ainda grava `distribution: "apiforge"`
  (`service.py:332`, real: `apiforge-af`) e `install_root` fantasma
  (`service.py:343` setdefault de `installs_root()/api-forge`).
- **P1-3** — scope user: consumer-docs escrevem na raiz do alvo; com
  `root=$HOME` isso é `~/AGENTS.md` (a camada nova mantém a semântica;
  decisão pendente).
- **P1-5** — `host_assets/agents/executors/` empacotado mas não
  renderizado — decisão em aberto (remover do wheel ou instalar).
- **P1-6** — sem `MANIFEST.sha256` declarativo assinável dos assets
  canônicos (o contrato suporta `integrity.files`; `test_artifact_contents.py`
  segue como gate de presença).
- **P1-7** — `install` sem `_check_python()`/`detect_source` no recibo —
  não tocado.
- **P2-1…P2-6** — `.codex/agents/*.toml` no install, verb `environment`,
  auto-reparo do `update`, marker mínimo de roteamento (agora coberto
  pelos blocos `forge:*` + AGENT_PROTOCOL consolidado — parcial),
  sdist "repo tarball" — não tocados.
- **`DISTRIBUTION_PARITY.md`** descreve a lacuna do leitor pré-§8.2 como
  "tracked" — o §8.2 (`78386e4`) corrigiu; o doc registra o histórico.
- **`mcp-handshake` BLOCKED sem o extra `mcp`** — estado de dependência
  honesto (não corrupção), documentado; segue o comportamento.

## 7. Testes executados

| Suíte | Arquivo | Contagem | Resultado |
|---|---|---|---|
| install lifecycle + context txn | `tests/e2e/test_install_lifecycle.py` | 28 | verde |
| wheel isolation (lf-0039) | `tests/test_wheel_isolation.py` | 1 (e2e) | verde |
| evals §7 | `tests/test_evals_cycle5.py` | 10 | verde |
| discovery ops §6.2 | `tests/test_discovery_ops.py` | 6 | verde |
| artifact contents | `tests/test_artifact_contents.py` | — | verde |

Cross-forge (rodado em the-forge, cobrindo esta wheel): **120/120**
permutações de ordem de instalação (`test_multi_forge_e2e.py`, marker
`slow`) e `vendor.py --check` **CLEAN**.

## 8. Resultados

- `src/apiforge/_forgecontext.py` **byte-idêntico** ao canônico e às 4
  outras forjas (sha256 `390f5e0e61ab80dc…`, `_SOURCE_SHA256 =
  "e72e93eab21ade74"`, v1.3.1).
- `install` escreve `.forge/context/{registry.json,
  capabilities/api-forge.json, ROUTING.md}` + consumer-docs
  (`forge:api-forge` blocks + `AGENT_PROTOCOL.md` consolidado) + `.mcp.json`
  managed key sob um único lock transacional; `install uninstall` idem.
  Markers legados `api-forge:managed` são removidos na convergência
  (`_LEGACY_DOC_TAGS`).
- `discovery_ops.py` é fonte única do mapa §6.2 + ops §7.2 → verbos reais;
  `domains` publicados: `api-design, api-contract, api-testing,
  api-performance, api-observability, api-migration, data-access,
  messaging`.
- Evals classificados (`evals/catalog.py`) persistidos no manifesto
  (`eval_suites` + `discovery.ops`); ~30 verbos `apiforge evals <suite>`
  nativos + `task holdout`/`task verify`/`verify plan|escalate`.
- `install verify` = handshake JSON-RPC real; sem extra `mcp` → BLOCKED
  honesto, nunca traceback.
- `forge.json`/`forge.agentic.json` empacotados em `apiforge/_data/`;
  `default_root` de knowledge ignora stubs sem `pack.yaml` (§8.2).

## 9. Evidências Devin/Claude/Codex

**NÃO EXECUTADO.** A prova E2E real por host (§10.2 — Devin CLI, Claude
Code, Codex CLI, Copilot) pertence ao ciclo 8, pendente. Os artefatos
instalados foram verificados por testes e2e e wheel isolation — não por
telemetria de host real.

## 10. Matriz PyPI

| Componente | Estado |
|---|---|
| Wheel local (HEAD) | construída e testada em venv limpa fora do checkout (`tests/test_wheel_isolation.py`); usada na matriz 5! do the-forge |
| `forge.json`/`forge.agentic.json` no wheel | presentes em `apiforge/_data/` (force-include `pyproject.toml:102-103`) |
| `_data/{knowledge,evals}` + `host_assets/{skills,agents,templates}` | empacotados (ver `docs/install/DISTRIBUTION_PARITY.md`) |
| Publicação no índice | **PENDENTE DE PUBLICAÇÃO** — worktree marca `0.2.0`; PyPI ainda serve `0.1.6` |
| sdist | `.tokensave/` excluído via `.gitignore` (#99); wheel/sdist locais continuam "repo tarball" por padrão (P2-6) |
| PyPI 0.1.6 publicado | bit-idêntico ao wheel 0.1.6 local (baseline) |

## 11. Compatibilidade

- Contratos `forge/*` v1 estáveis; `forge/context/v1` +
  `forge/context-registry/v1` adicionados sem quebrar
  `forge/InstallationManifest/v1`.
- Engine vendored compatível com py3.10 (v1.2.1) — a forja exige `>=3.12`,
  mas a engine é compartilhada com forjas de piso 3.10.
- Rollback: uninstall transacional só remove o próprio manifesto/entry/
  blocks; `FORGE-CONTEXT-OWNERSHIP` impede deleção cruzada; markers
  legados `api-forge:managed` são excisados na convergência, nunca
  conteúdo de usuário.

## 12. Segurança

Herdada do motor vendored + wiring local:

- `_txn_restore` com validação de path (`..`, absoluto, `\`, drive;
  blob `^\d{1,8}$`) — `_forgecontext.py:2495-2531`.
- KeyboardInterrupt/SystemExit propagam bare após rollback (`:2670+`).
- `forge_bootstrap.py` 1.1.1: `_URL_USERINFO_RE` `[^/\s]+@` (userinfo com
  `@` interno não vaza), argv trim, smoke vazio≠PASS.
- installkit 1.0.1: stale-lock `created_at` fallback para PID indecidível
  (Windows/PermissionError).
- `discovery.knowledge_get` valida com `Path.is_relative_to()` — resolve
  containment do ref sem depender de separador (Windows, #105).
- `.tokensave/` não vaza mais no sdist (#99).
- Ownership `FORGE-CONTEXT-OWNERSHIP`; markers ambíguos →
  `FORGE-CONTEXT-CONFLICT`; conteúdo de usuário byte-preservado.

## 13. Performance

- Reinstall inalterado = zero writes (registry determinístico — prova na
  matriz 5!).
- `discovery_ops` é tabela em memória (fonte única).
- Sem claims quantitativos — ciclo 9 (§11) não executado.

## 14. Recomendações

1. Ciclo 8 (§10.2) — prova real Devin/Claude/Codex com esta wheel
   instalada num consumidor de APIs; sem ela o aceite §16 sobre hosts
   fica aberto.
2. Publicar `0.2.0` (`apiforge-af`, §12.5) ou marcar release bloqueada —
   nunca simular.
3. Alinhar `service.py` às correções M1/M3/M12 da referência: deregister
   no uninstall (P1-1), `distribution`/`install_root` corretos no
   registry global (P1-2), política de consumer-docs em scope=user (P1-3).
4. Decidir `executors/` (P1-5) e `MANIFEST.sha256` do bundle (P1-6).
5. Resíduos P2: `.codex/agents` no install, verb `environment`,
   auto-reparo do `update`, sdist enxuto.

## 15. Status por Forge

| Forge | `forge/context/v1` | `_forgecontext` | `_installkit` | `forge_bootstrap` | Status |
|---|---|---|---|---|---|
| the-forge | registry + docs + txn | v1.3.1 | v1.0.1 | v1.1.1 | **merged, pendente de release** (0.6.0) |
| spark-forge-aws | registry + docs + txn | v1.3.1 | v1.0.1 | v1.1.1 | **merged, pendente de release** (0.6.0) |
| spark-forge-azure | registry + docs + txn | v1.3.1 | v1.0.1 | v1.1.1 | **merged, pendente de release** (0.2.0) |
| **api-forge** | registry + docs + txn | v1.3.1 | v1.0.1 | v1.1.1 | **merged, pendente de release** (0.2.0) |
| platform-forge | registry + docs + txn | v1.3.1 | v1.0.1 | v1.1.1 | **merged, pendente de release** (0.2.0) |
| forge-doctor-api | — | ausente | v1.0.1 | v1.1.1 | **installkit only (boundary)** |
| forge-doctor-data | — | ausente | v1.0.1 | v1.1.1 | **installkit only (boundary)**; certifi PYSEC-2026-4320 |
| data-sentinel-forge | — | ausente | v1.0.0 | ausente | **deferred by owner** |

---

## Apêndice — comandos executados para este relatório

```text
git log v0.1.6..HEAD --format='%h %H %s'        → 19 commits
git diff --stat v0.1.6..HEAD                    → 34 files, +9488/−2169
sha256sum src/apiforge/_forgecontext.py         → 390f5e0e61ab80dc…
sha256sum src/apiforge/_installkit.py           → 1484135ae71c396e…
sha256sum scripts/forge_bootstrap.py            → 978862ebedb9ecfb…
grep _FORGECONTEXT_VERSION src/apiforge/_forgecontext.py → "1.3.1"
grep deregister src/apiforge/install/service.py → (vazio — P1-1 aberto)
grep -c 'def test_' tests/e2e/test_install_lifecycle.py \
  tests/test_{wheel_isolation,evals_cycle5,discovery_ops}.py → 28/1/10/6
```

## Pós-release — evidência de publicação (2026-10-23 UTC)

| Item | Estado | Evidência |
|---|---|---|
| Tag | CRIADA | `v0.2.0` no merge commit da release PR |
| GitHub Release | CRIADO | `gh release view v0.2.0` |
| PyPI | PUBLICADO | `pypi.org/pypi/apiforge-af/json` → `0.2.0` |
| Wheel smoke (venv limpo) | PASS | `pip install apiforge-af==0.2.0` + `apiforge --version` → `0.2.0` |

Notas: installkit canônico 1.0.2 (`_SOURCE_SHA256 a15ca78bb34a0109`), bootstrap 1.1.1 — propagados aos 7 carriers; `vendor.py --check` CLEAN ×7. `data-sentinel-forge`: **deferido pelo dono** (outro CLI evoluindo).
