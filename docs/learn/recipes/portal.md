# Receita — portal web local do API Forge

**O quê:** abre uma UI web local (`127.0.0.1` + token de sessão) que
exibe e opera os **mesmos** serviços do CLI — instalação, hosts, MCP,
skills, agents, tarefas (inclui análise real de API), grafo e docs.
**Por que:** a jornada inteira (install → host → verify → primeira
análise) fecha numa tela só, com os mesmos recibos e as mesmas recusas
nomeadas do CLI — sem decorar flags.
**Quando:** primeiro onboarding, configurar Claude/Devin/Codex, auditar
estado sem ler JSON, ou apresentar a forja para alguém.
**Quando não:** automação, CI ou fluxo MCP — o portal é fronteira humana
e nunca roda dentro do MCP; para scripts use `apiforge install`,
`apiforge analyze` e os verbos diretamente.

## Problema

"Quero instalar a forja, ver o que o host está vendo e rodar a primeira
análise — sem aprender os verbos antes."

## Pré-requisitos

`apiforge` instalado e um projeto com `git init`. Nenhum serviço externo:
o servidor é stdlib Python, os assets vão embutidos no pacote.

## Passo a passo

```bash
apiforge portal                    # abre o browser numa URL com token de sessão
apiforge portal --no-browser       # só imprime a URL (SSH/headless)
apiforge portal --port 8420        # porta fixa em vez de livre
apiforge portal --root /caminho    # inspeciona outro workspace
```

Na UI: **Install** mostra o estado real (NOT_INSTALLED → planejar →
confirmar → INSTALLED/VERIFIED); **Hosts** detecta Claude/Devin/Codex/
Copilot e devolve o `launch_command` para copiar (o portal não abre
binário — sem TTY); **Tasks** executa verbos seguros com plano → token
→ confirmação, inclusive *analisar a api* com `contract`/`project` do
workspace — roda `analyze_project` de verdade e persiste o case em
`.apiforge/portal-cases/<ts>/`.

## Saída esperada / interpretação

- Health: `NOT_INSTALLED` (ledger vazio) → `INSTALLED`/`ACTIVE`/
  `VERIFIED` — nunca `VERIFIED` sem handshake MCP provado.
- Mutações exigem plano + `plan_token` + confirmação explícita; o recibo
  é o mesmo `forge/…` do CLI.
- Intenções ambíguas voltam `AF-PORTAL-AMBIGUOUS` com `safe_verbs` —
  recusa nomeada, não chute.

## Verificação

Sem token de sessão, toda rota `/api/v1/*` responde 403. `GET /health`
repete o estado do `install status`. Uma task `analisar a api` cria
`case.json` com `case_id` e artefatos hashados no workspace.

## Limitações

- Só `127.0.0.1`, sem TLS — é ferramenta local de um usuário, não um
  serviço. O token de sessão na URL é a fronteira.
- `analisar a api` aceita apenas caminhos **dentro** do workspace
  (escape vira `AF-PORTAL-INPUT`); cases ficam em `.apiforge/portal-cases/`.
- Catálogo de skills/agents vem do pacote/clone da forja, não do
  workspace do usuário.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| `AF-PORTAL-NO-ASSETS` | clone sem `portal/assets/` | rode `python scripts/vendor.py` no forge-portal (pip install já embute) |
| health `DEGRADED` | drift em asset gerenciado | `apiforge install repair` |
| `PORTAL-PLAN-STALE` | plano mudou ou token expirou | regenere o plano na página |
| `AF-PORTAL-AMBIGUOUS` | intenção fora dos verbos seguros | use um verbo de `safe_verbs` |
| `PORTAL-HOST` 403 | Host não-loopback (rede/túnel/DNS rebinding) | acesse por 127.0.0.1/localhost |
| `PORTAL-ORIGIN` 403 | POST com Origin fora do loopback | só a UI do portal muta |
| `PORTAL-RATE-LIMITED` 429 | >10 mutações/min | aguarde a janela; envelope sinaliza retry |

## Nota

O portal é opcional: CLI (`apiforge`), TUI (`apiforge tui`) e MCP
(`apiforge-mcp`) cobrem tudo que ele faz. Ele existe para a jornada de
descoberta — o motor é sempre o mesmo.
