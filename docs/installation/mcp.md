# MCP — api-forge

Servidor MCP: `apiforge-mcp`

A instalação registra uma entrada gerenciada em `.mcp.json` (chave
`_forge_managed.api-forge`) — outras entradas suas ficam intactas.

Verificar de verdade (handshake real + tools/list + invocação segura):

```bash
apiforge doctor
```

O doctor executa `initialize` → `tools/list` → `tools/call` de leitura
quando o forge declara uma ferramenta de verificação, e reporta PASS /
BLOCKED / FAIL / UNVERIFIED com evidência de processo (exit, stderr).
Nunca infere sucesso de presença de arquivo.
