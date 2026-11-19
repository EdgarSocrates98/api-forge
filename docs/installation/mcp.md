# MCP — api-forge

Servidor MCP: `apiforge` (lançado pelo entry point `apiforge-mcp`)

A instalação registra uma entrada gerenciada em `.mcp.json` (chave
`_forge_managed.api-forge`) — outras entradas suas ficam intactas. O
`command` gravado é sempre um **argv absoluto**: o caminho do entry
point `apiforge-mcp` no env registrado/atual, ou
`python -m apiforge.mcp.main` como fallback module-pinned — um host
nunca resolve o servidor por busca em PATH.

Verificar de verdade (handshake real + tools/list + invocação segura):

```bash
apiforge install verify    # sonda dedicada: initialize → tools/list → tools/call
apiforge install doctor    # ledger + drift + mcp config + o mesmo handshake
```

O verify/doctor executa `initialize` → `tools/list` → `tools/call` de
leitura (`portable_status`), e reporta PASS / BLOCKED / FAIL / UNVERIFIED
com evidência de processo (exit, stderr). Nunca infere sucesso de
presença de arquivo — extra `mcp` ausente vira `UNVERIFIED`/`BLOCKED`
nomeado, nunca PASS.
