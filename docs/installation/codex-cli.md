# api-forge + Codex CLI

```bash
cd ~/meu-projeto
apiforge install
```

Assets vão para `.agents/skills/` e `.agents/agents/` — a superfície
compartilhada que o Codex consome; nenhuma cópia duplicada em `.codex/`
é escrita. Abra `codex` no diretório.

MCP: `.mcp.json` gerenciado registra o servidor `apiforge` com argv
absoluto (entry point `apiforge-mcp` ou `python -m apiforge.mcp.main`).
