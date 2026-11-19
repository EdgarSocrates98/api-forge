# api-forge + Claude Code

```bash
cd ~/meu-projeto
apiforge install
```

Assets vão para `.claude/skills/` e `.claude/agents/`; `AGENTS.md` e
`CLAUDE.md` recebem o bloco `forge:ecosystem` gerenciado (criados com
preâmbulo mínimo quando ausentes — conteúdo seu fora do bloco nunca é
tocado). Abra o Claude Code no diretório — as skills aparecem
automaticamente.

MCP: `claude` lê `.mcp.json` da raiz — a entrada `apiforge` é registrada
na instalação com argv absoluto (o caminho do entry point `apiforge-mcp`
ou `python -m apiforge.mcp.main`), nunca um nome dependente de PATH.
