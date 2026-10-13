# Receita — medir e abrir a sessão do host de IA

**O quê:** `apiforge ai` mede o estado real de cada host (binário,
versão, login, integração com a install) e `apiforge ai <host> --launch`
abre a sessão no repositório.
**Por que:** antes de gastar uma sessão, um recibo diz se o host existe,
está logado e enxerga o API Forge instalado — sem inventar suporte.
**Quando:** depois de `install`, na dúvida sobre qual host usar, ou
quando a sessão do host não vê MCP/skills.
**Quando não:** configurar o host — `ai` só observa; quem instala é
`apiforge install`, quem conserta é `install repair`.

## Problema

"Tenho Devin, Claude e Codex — em qual abro a sessão e está tudo pronto?"

## Pré-requisitos

`apiforge install` aplicado no projeto; o host CLI instalado (o `ai`
declara `NOT_DETECTED` honestamente, nunca chuta).

## Passo a passo

```bash
apiforge ai                  # mede os quatro hosts
apiforge ai devin            # um host: state, versão, logged_in, integração
apiforge ai devin --launch   # abre o binário aqui (só TTY, um host)
```

## Saída esperada / interpretação

Estados: `NOT_DETECTED` → `DETECTED` → `SUPPORTED` → `READY`
(integração healthy) / `NEEDS_LOGIN` / `INTEGRATION_DEGRADED|BROKEN` /
`refused`. Com `--launch` negado, `launch_refused` diz por quê
(`host_missing`, `login_required`, `no_tty`, seletor `all`).

## Verificação

`READY` exige `integration.state == healthy` — se vier `SUPPORTED` com
login ok, a install não está saudável: `install status` mostra o drift.

## Limitações

Autenticação vira só booleano — a saída bruta do host (que pode listar
caminhos de credencial) nunca entra no recibo. Copilot não tem
subcomando de status documentado → `logged_in: null` declarado.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| `NEEDS_LOGIN` | sessão expirada | rode o `login_hint` do recibo |
| `INTEGRATION_DEGRADED` | asset gerenciado alterado | `apiforge install repair` |
| `all` + `--launch` recusado | lançar é escolha humana | escolha um host |

## Uso por agentes

Saída 100% estruturada — `state` por host + `launched`/`launch_refused`.
O `--launch` é fronteira humana: nunca por automação.
