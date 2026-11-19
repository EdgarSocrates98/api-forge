# api-forge + Devin CLI

```bash
cd ~/meu-projeto
apiforge install
```

Assets vão para `.agents/skills/` e `.agents/agents/` — Devin lê
`.agents/` nativamente, então nenhuma segunda cópia é escrita em
`.devin/` (reservado a assets host-specific). Abra `devin` no diretório
do projeto.

MCP: a entrada `apiforge` em `.mcp.json` — argv absoluto, sem dependência
de PATH — é consumida pelo host.
