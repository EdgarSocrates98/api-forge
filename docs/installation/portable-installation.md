# Instalação portátil — api-forge

Instala em qualquer diretório/repositório — sem estrutura prévia exigida.

```bash
cd <qualquer-projeto>
apiforge install                    # escopo projeto (padrão)
apiforge install --dry-run          # planeja sem escrever
apiforge install --profile minimal  # só config+MCP+docs, sem mirrors
apiforge install --profile full     # mesmo conjunto de assets do recommended
apiforge install --gateway-profile economy  # MCP com --surface compact
```

O que acontece: assets gerenciados vão para `.agents/`, `.claude/`,
`.devin/`, `.codex/` conforme os hosts pedidos; `.mcp.json` ganha uma
entrada gerenciada; `AGENTS.md`/`CLAUDE.md`/`AGENT_PROTOCOL.md` recebem o
bloco `forge:api-forge` — conteúdo seu nunca é sobrescrito.

## Perfis (`--profile`)

`--profile` seleciona **conjuntos de componentes** — e nada mais. Não há
diferença de conteúdo dentro de um componente nem de "profundidade":

| Perfil | Componentes instalados |
|---|---|
| `minimal` | config + entrada MCP + docs (`AGENTS.md` bloco) — sem mirrors de skills/agents/knowledge |
| `recommended` (padrão) | minimal + skills + agents + ponteiros de knowledge/rules/evals |
| `full` | **idêntico ao `recommended` hoje** — slot reservado para componentes opcionais (`tui`, `graph-studio`) quando entrarem no pacote |

Seleção fina por componente: `--components skills,agents,knowledge` (csv;
válidos: `skills`, `agents`, `mcp`, `knowledge`, `rules`, `evals`, `tui`,
`graph-studio`). Cada nome habilita só o seu conjunto.

## Perfil do Context Gateway (`--gateway-profile`)

Dimensão ortogonal ao `--profile`: decide só o **argv do servidor MCP**
gravado em `.mcp.json`, não mexe em nenhum asset:

| `--gateway-profile` | argv do MCP | Tools expostas |
|---|---|---|
| `economy` / `balanced` (padrão) | `apiforge-mcp --surface compact` | 6 gateways (`apiforge_discover`, `apiforge_call`, …) |
| `deep` | `apiforge-mcp --surface full` | 154 tools completas |

A escolha fica persistida em `.apiforge/install/components.json`
(`execution_profile`): `status`, `doctor` e `repair` reproduzem o mesmo
argv gravado — `repair` nunca regrava `.mcp.json` com um modo diferente
do instalado. Instalações anteriores à flag (argv sem `--surface`,
superfície full implícita) seguem reproduzidas como estão.

## Raiz do alvo (`--root`) e projetos sem `.git`

- `--root <dir>` é autoritativo: sempre vence, inclusive em diretório sem
  `.git` (gitless) e inclusive no escopo `workspace` — um marcador de
  workspace num ancestral nunca desvia o alvo para cima do `--root`.
- Sem `--root`, o escopo `project` procura a raiz VCS (`.git`) subindo do
  cwd; se não houver, procura um estado `.apiforge/install/` já existente;
  sem os dois, recusa com `FORGE-INSTALL-NOT-A-REPO` — passe `--root`.
- Escopo `workspace`: `--root` é autoritativo; sem ele, procura marcador
  de workspace, depois `.git`, e por fim o cwd.
- Precedência entre escopos: `project > workspace > user` — a instalação
  mais específica vence; conflitos são reportados, nunca sobrescritos.

## Ponteiros de knowledge

As referências `knowledge/<rel>` citadas por skills/agents resolvem em
ponteiros gerados em `knowledge/api-forge/<rel>` (mais um `README.md`
índice no mesmo subdir) — o subdir com o nome do forge evita colisão na
raiz `knowledge/` compartilhada entre forges: duas forjas na mesma árvore
não podem ser donas do mesmo `<rel>`. O ponteiro ensina o caminho de
retrieval real:

```bash
apiforge knowledge get <rel>
apiforge knowledge search "<termo>" --domain <dominio>
apiforge knowledge list
```

Ao migrar de versões que gravavam na raiz genérica: stubs antigos
gerenciados e intactos são removidos do disco e do ledger; arquivo
editado por você fica intacto no disco (posse liberada, recusa nomeada
no recibo); arquivo de outra forge nunca é tocado.

## Superfície declarada (install-2.1)

`forge.json` declara, e o install copia verbatim para o manifesto
registrado (`forge/InstallationManifest/v1` em
`~/.forge/installations/api-forge.json`):

- `installation_kind: "content"` — o plano consolidado do workspace usa
  na ordenação estável entre forges.
- `install` — capability surface honesta: `operations`
  (`plan`/`apply`/`status`/`doctor`/`repair`/`update`/`uninstall`/
  `mcp-verify`), `flags` (`--scope` `--root` `--host` `--profile`
  `--components` `--gateway-profile` `--yes` `--dry-run` `--purge`
  `--to` `--repo`), `hosts`, `scopes`, `profiles`, `approval: "--yes"`.
  O orquestrador só envia flag declarada; pedido fora da lista vira
  `unsupported-capability`.
- `depends_on: []` — declarado mesmo vazio: a presença da chave diz
  "este forge não depende de ninguém".
- `mcp.verify_tool: "portable_status"` — tool no-arg read-only usada por
  `install verify` e `doctor` para aferição do handshake.

## Flags do ciclo de vida

```text
apiforge install [--scope S] [--root DIR] [--host H] [--profile P]
                 [--components CSV] [--gateway-profile G]
                 [--dry-run | --yes]
apiforge install status|doctor|repair [--scope S] [--root DIR] [--dry-run]
apiforge install update [--to VERSAO] [--repo CHECKOUT] [--dry-run]
apiforge install uninstall [--scope S] [--root DIR] [--purge] [--dry-run]
apiforge install verify                       # handshake MCP real
```

Sem `--yes` nem `--dry-run` a escrita é recusada — o plano é o contrato.
`--to latest` nunca é instalável (versão sempre pinned).
