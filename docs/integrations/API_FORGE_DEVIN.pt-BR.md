# API Forge + Devin Desktop / CLI / Cloud

Idioma: [English](API_FORGE_DEVIN.md) · [Português (Brasil)](API_FORGE_DEVIN.pt-BR.md)

Esta integração é deliberadamente orientada a payload. O API Forge gera uma
tarefa Devin versionada, suas instruções de execução, checks e fronteiras de
segurança; ele nunca chama a API do Devin, inicia uma sessão, altera um
repositório ou abre um pull request.

## O que é suportado

Devin Desktop é o IDE local e centro de comando de agentes. Ele gerencia
agentes locais/cloud, workspaces e extensões. Devin CLI é a superfície de
terminal distribuída com o Desktop ou instalada separadamente em Windows,
Linux e macOS. A CLI roda localmente, retoma sessões, exporta transcript,
entrega uma tarefa ao Devin Cloud ou abre uma sessão cloud no Desktop. Sessões
cloud são uma fronteira separada e exigem escolha de conta, repositório e
plataforma.

O API Forge trata capacidades do produto como `declared` até que uma probe
local ou receipt as observe:

| Capacidade | Estado API Forge | Fronteira de prova |
|---|---|---|
| Geração de payload | observado no repositório | `apiforge devin payload` e testes de contrato |
| Devin CLI instalado | observado ou unresolved | `apiforge devin probe` executa apenas `devin --version` local |
| Desktop | declarado | instalação/conta não são sondadas pelo core |
| Handoff cloud | declarado | conta, repositório e plataforma continuam estado humano/externo |
| Skills, agents, hooks e MCP | observados como configuração | Devin precisa carregá-los/executá-los na superfície escolhida |

## Início rápido

Na raiz do repositório:

```text
apiforge devin probe
apiforge devin capabilities
apiforge devin payload "Map the next safe API Forge evolution slice" --surface cli --task-kind planning
apiforge devin payload "Implement the approved slice" --surface desktop --task-kind implementation
apiforge devin payload "Continue the reviewed task in Devin Cloud" --surface cloud --task-kind handoff
```

A saída é JSON `DevinPayload/v1`: prompt para copiar, dados de launch por
superfície, saídas esperadas, comandos de verificação, ações proibidas e
limitações de evidência. `--sandbox` é recusado em payloads da CLI nativa
Windows porque o sandbox do Devin é documentado via WSL 2 nesse caso.

Para uso pela CLI, o formato gerado corresponde aos comandos documentados:

```text
devin <generated args> -- <prompt>
devin -p -- <prompt>                 # modo print não interativo
devin --prompt-file <file>           # prompt longo em arquivo
devin -c                             # retoma a última sessão local
devin -r <session-id>                # retoma uma sessão selecionada
devin --cloud                        # inicia no Devin Cloud
```

Use `/plan` para planejamento somente leitura, `/ask` para uma pergunta,
`/handoff` para mover trabalho local ao Cloud, `/open desktop` para abrir uma
sessão cloud no Desktop, `/pickup` para retornar à branch local e `/export` ou
`--export` quando um transcript for necessário como evidência. `/loop` é útil
para um ciclo local limitado de revisão/correção, mas deve começar de um
estado Git limpo e não substitui a verificação do API Forge.

## Camada Devin nativa do repositório

O projeto contém uma configuração `.devin/` commitada:

- `config.json` permite inspeção segura, bloqueia operações destrutivas e
  pergunta antes de commit, push, Docker ou escrita em arquivos de secrets;
- `hooks.v1.json` chama `scripts/devin_pretool_guard.py` em `PreToolUse` e
  imprime as pré-condições de case/routing em `SessionStart`;
- `.devin/skills/api-forge-devin-runbook/SKILL.md` é o entry point recomendado;
- `.devin/agents/api-forge-reviewer.md` é um perfil de revisão somente leitura;
- `.devin/mcp_config.example.json` é opt-in e nunca deve carregar credenciais
  commitadas.

A CLI Devin carrega `AGENTS.md`; portanto o contrato operacional do API Forge
continua sendo a fonte única para case, routing, SDD, evidência, sandbox e
política de PR. Skills `.claude/` e `.agents/skills/` continuam disponíveis
quando importadas pelo Devin, mas suas afirmações seguem governadas pela
evidência do API Forge.

## Superfície recomendada por etapa

| Etapa | Superfície padrão | Modo Devin | Fronteira API Forge |
|---|---|---|---|
| Discovery/arquitetura | CLI ou Desktop | `/plan` / Normal | fatos somente leitura, case e next-step |
| Implementação | CLI ou Desktop | Normal, depois Accept Edits após aprovação | paths graváveis do TaskSpec e sandbox |
| Verificação/revisão | CLI, reviewer Desktop ou `api-forge-reviewer` | `/plan` ou `/ask` | checks independentes e Outcome Brief |
| Trabalho longo | CLI `--cloud` ou `/handoff` | política Cloud + revisão humana | nenhuma mutação externa pelo core |
| Execução local unattended | CLI | `--sandbox`/Autonomous apenas quando suportado | fronteira OS fail-closed; WSL 2 no Windows nativo |

Não use Bypass/Dangerous por padrão. O Devin documenta que Bypass aprova
automaticamente chamadas de ferramenta, inclusive destrutivas; Autonomous é a
alternativa protegida por sandbox e exige `--sandbox`. Configurações de
empresa/equipe podem substituir permissões de projeto e usuário.

## MCP e ferramentas externas

A configuração MCP do Devin aceita servidores stdio locais e HTTP remotos. O
API Forge fornece um exemplo sem secrets para o servidor local `apiforge-mcp`:

```text
devin mcp add -s project api-forge -- apiforge-mcp
devin mcp list
devin mcp get api-forge
```

Prefira ferramentas MCP somente leitura para discovery, análise de contrato,
grafo, evidência e brief. Nunca adicione um servidor de mutação GitHub à
configuração do projeto. O workflow dedicado de validação verde continua
sendo o único caminho de mutação de PR.

## Atualizando a configuração Devin

A CLI Devin muda rapidamente. Antes de depender de novo flag, modelo,
transporte, hook ou comportamento Desktop, consulte novamente a referência
oficial e registre a data de consulta. Não fixe uma versão atual do Devin nos
contratos do API Forge. Use `apiforge devin probe` para o binário instalado e
mantenha claims de produto como `declared` até observá-los.

Referências oficiais: [Devin Desktop](https://devin.ai/desktop), [Devin CLI](https://devin.ai/cli), [extensibilidade](https://docs.devin.ai/cli/extensibility), [configuração](https://docs.devin.ai/cli/extensibility/configuration), [regras e AGENTS.md](https://docs.devin.ai/cli/extensibility/rules), [MCP](https://docs.devin.ai/cli/extensibility/mcp/configuration), [skills](https://docs.devin.ai/cli/extensibility/skills/overview), [subagents](https://docs.devin.ai/cli/subagents), [hooks](https://docs.devin.ai/cli/extensibility/hooks/overview), [comandos](https://docs.devin.ai/cli/reference/commands) e [permissões](https://docs.devin.ai/cli/reference/permissions).
