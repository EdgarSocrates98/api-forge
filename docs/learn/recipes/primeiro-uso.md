# Receita — primeira utilização do API Forge

**O quê:** instala o API Forge num projeto, confirma a integração com o
host e roda a primeira análise determinística.
**Por que:** a jornada inteira (install → host → analyze → next-step) tem
que fechar antes de qualquer trabalho substantivo.
**Quando:** primeiro clone, onboarding de projeto, após upgrade de versão.
**Quando não:** diagnóstico de instalação quebrada — vai para
`apiforge install doctor` e `docs/installation/troubleshooting.md`.

## Problema

"Instalei o pacote — como sei que o host está vendo o API Forge?"

## Pré-requisitos

`apiforge` instalado (`pip install apiforge` ou `setup.ps1`/`setup.sh` do
repo) e um projeto com `git init`.

## Passo a passo

```bash
apiforge install --profile full --yes   # assets + skills + agents + .mcp.json
apiforge install status                 # ledger + drift — esperado: healthy
apiforge ai devin                        # host detectado? logado? READY?
apiforge install verify                  # handshake MCP real (precisa do extra mcp)
```

Abra a sessão do host (`apiforge ai <host> --launch`, ou o
`launch_command` do recibo) e peça uma tarefa em linguagem natural —
o host já vê skills, agents e o MCP server `apiforge`.

## Saída esperada / interpretação

`install status` → `"status": "healthy"`, `drift.ok` = nº de assets.
`ai <host>` → `READY` quando binário + login + integração estão OK.
`install verify` → `PASS` com a lista de tools do handshake.

## Verificação

Se `ai` mostrar `SUPPORTED` em vez de `READY`: integração não está
`healthy` — rode `install status` e `install repair` se houver drift.
Se `NEEDS_LOGIN`: o recibo traz `login_hint` com o comando oficial.

## Limitações

`install verify` exige o extra `mcp` e `apiforge-mcp` no PATH; sem eles
o check sai `BLOCKED` — é declaração honesta, não falha do install.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| `ai` → `NOT_DETECTED` | host CLI fora do PATH | instale o host ou aceite o estado |
| `BLOCKED` no handshake | extra `mcp` ausente | `pip install apiforge[mcp]` / extra no venv |
| `degraded` no status | asset gerenciado editado/removido | `apiforge install repair` |

## Uso por agentes

Todas as saídas são JSON estruturado com estados nomeados — o host lê
`state` e `integration.state` sem parsear texto.
