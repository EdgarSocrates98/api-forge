# Paridade entre hosts

O API Forge tem um core Python compartilhado e entradas específicas por host.
Execute:

```text
apiforge agentops parity
```

A auditoria verifica o layout do repositório; ela não declara que um host
suporta funções que ele não expõe.

| Host | Entradas no repositório | Limite atual |
|---|---|---|
| Claude Code | `CLAUDE.md`, `.claude/skills`, `.claude/agents` | hooks/MCP dependem da instalação do Claude |
| GPT/Codex | `AGENTS.md`, `.agents/skills`, `.agents/agents` | hooks `.codex` são gerenciados pelo host |
| Devin | `AGENTS.md`, `.devin/` | payloads são locais; Desktop/CLI/Cloud/subagents/hooks dependem do runtime Devin |
| Copilot | `AGENTS.md`, `.github/skills` | não há garantia de paridade para MCP/subagents |

Todos os hosts podem usar o core CLI depois da instalação em um ambiente do
usuário. “Core compartilhado” significa comportamento local do pacote; não
significa UI, hooks, ciclo de vida MCP ou orquestração de subagents idênticos.
Nenhum host é pré-requisito para `inspect`, `init`, `status`, `doctor` ou
resolução de contexto.

## Negociação e planos de ativação

```text
apiforge agentops hosts
apiforge agentops negotiate --capability mcp
apiforge agentops activation-plan --host claude
apiforge agentops activation-plan --host gpt-codex
apiforge agentops activation-plan --host devin
apiforge agentops activation-plan --host copilot
```

Declarações mantidas pelo host podem ficar em `.apiforge/hosts/*.json`. Sem
declarações, o resolver usa o layout estático conservador e preserva as
limitações conhecidas. O resultado publica apenas interseções comprovadas; ele
nunca transforma ausência de evidência em equivalência entre hosts.

## Assets, conflitos e segurança

Os templates pertencem ao pacote instalado. Adapters gerados são pequenos,
identificados por hash e destinados a preview/plano. Um conflito é reportado
como `AF-HOST-CONFLICT`; sincronização automática, sobrescrita e symlink não
estão habilitados.

Para o Devin:

```text
apiforge devin payload "Review the current API evolution slice" --surface cli --task-kind review
apiforge devin probe
apiforge devin capabilities
```

O adapter mantém claims em `declared` até observar um executável local ou um
artefato do repositório. Consulte também o
[guia Devin](integrations/API_FORGE_DEVIN.md).

## Limites da paridade

A paridade funcional total entre Claude, Devin, Codex, Copilot e outros hosts
continua fora desta onda. Cada capability precisa de evidência própria; hosts
sem MCP, hooks ou subagents continuam podendo usar o core local e os comandos
portáteis.

[English version](HOST_PARITY.md) · [Distribuição portátil em português](guides/API_FORGE_PORTABLE_DISTRIBUTION.pt-BR.md)
