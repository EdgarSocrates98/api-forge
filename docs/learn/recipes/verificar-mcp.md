# Receita — provar que o MCP server funciona de verdade

**O quê:** `apiforge install verify` executa o handshake JSON-RPC real —
initialize + tools/list + invoke de `portable_status` contra
`apiforge-mcp` por stdio.
**Por que:** um `.mcp.json` presente não prova nada — só o handshake
mostra que o server sobe e responde.
**Quando:** depois de `install`, quando o host não vê o server, antes de
culpar a configuração.
**Quando não:** para medir o custo da superfície — aí é
`apiforge mcp surface` (bytes por superfície).

## Problema

"O `.mcp.json` está lá mas o host não lista as tools — o server
funciona?"

## Pré-requisitos

`apiforge` instalado com o extra `mcp` (`apiforge-mcp` resolvível no
PATH); `.mcp.json` com a chave gerenciada `mcpServers.apiforge`.

## Passo a passo

```bash
apiforge install verify        # handshake real: initialize → tools/list → invoke
cat .mcp.json                  # a chave gerenciada declarada
apiforge ai <host>             # o host enxerga a integração? (state READY)
```

## Saída esperada / interpretação

`PASS` com a lista de tools (153 na superfície completa) e o invoke de
`portable_status`. `BLOCKED` quando `apiforge-mcp` não resolve ou o
extra falta; `FAIL` quando o processo sobe mas não responde o
initialize.

## Verificação

O recibo traz `tools` reais — se o número difere do esperado, o server
que subiu não é o que a `.mcp.json` aponta (versão/venv errada).

## Limitações

O handshake prova o server, não a aprovação do host: Claude pede
aprovação de `.mcp.json` de projeto por sessão; Codex lê só
`~/.codex/config.toml` (instale `--scope user --host codex`).

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| `BLOCKED` | `apiforge-mcp` fora do PATH | ative a venv ou reinstale com o extra |
| server sobe e falha | versão antiga do pacote | `apiforge install update` |

## Uso por agentes

Saída JSON com `status`/`tools`/`invoke` — o host lê sem parsear texto.
