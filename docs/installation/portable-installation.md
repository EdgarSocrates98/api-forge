# Instalação portátil — api-forge

Instala em qualquer diretório/repositório — sem estrutura prévia exigida.

```bash
cd <qualquer-projeto>
apiforge install                    # escopo projeto (padrão)
apiforge install --dry-run          # planeja sem escrever
apiforge install --profile minimal  # só CLI+MCP+marker
apiforge install --profile full     # skills + agents + todos os hosts
apiforge install --gateway-profile economy  # menor custo de execução
```

O que acontece: assets gerenciados vão para `.agents/`, `.claude/`,
`.devin/`, `.codex/` conforme os hosts detectados; `.mcp.json` ganha uma
entrada gerenciada; `AGENTS.md` recebe um bloco delimitado
`<!-- api-forge:managed -->` — conteúdo seu nunca é sobrescrito.

Perfis: `minimal` (essencial) · `recommended` (workflow completo, padrão)
· `full` (teto de disclosure — não é autorização extra).

Perfil de execução: `economy` reduz custo e contexto mantendo roteamento
seguro; `balanced` é padrão; `deep` amplia capacidade para tarefas difíceis.
Escolha permanece no recibo e no roteamento delegado, inclusive quando o
The Forge encaminha instalação para api-forge.
