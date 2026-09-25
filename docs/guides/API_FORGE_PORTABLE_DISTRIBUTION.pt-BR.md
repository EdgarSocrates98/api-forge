# Distribuição portátil e workspace do API Forge

Este é o passo a passo da primeira onda portátil para máquinas sem privilégio
de administrador, com rede bloqueada ou com hosts de agentes indisponíveis.

[English version](API_FORGE_PORTABLE_DISTRIBUTION.md) · [Guia de uso da
plataforma em português](API_FORGE_PLATFORM_USAGE.md) · [English platform
usage](API_FORGE_PLATFORM_USAGE.en.md)

## 1. Instale em um local controlado pelo usuário

Escolha um virtual environment, prefixo, volume ou diretório portátil que você
possa gravar. Não é necessário instalar no sistema nem usar symlink.

### Windows PowerShell

```powershell
uv venv E:\tools\api-forge-env
E:\tools\api-forge-env\Scripts\python.exe -m pip install 'apiforge[all]'
$env:PATH = "E:\tools\api-forge-env\Scripts;$env:PATH"
```

Se o `PATH` não puder ser alterado, chame o executável por caminho absoluto:

```powershell
E:\tools\api-forge-env\Scripts\apiforge.exe --help
```

### Linux, macOS, WSL ou container

```bash
uv venv "$HOME/.local/share/api-forge-env"
"$HOME/.local/share/api-forge-env/bin/python" -m pip install 'apiforge[all]'
export PATH="$HOME/.local/share/api-forge-env/bin:$PATH"
```

`.[all]` é opcional. O core continua utilizável sem MCP, TUI/Rich, AWS ou
outras integrações opcionais; `doctor` mostra o que está disponível.

## 2. Redirecione estado, configuração e cache

Use variáveis de ambiente quando o diretório do projeto não puder receber
`.apiforge` ou quando o estado precisar ficar em um volume portátil:

```powershell
$env:APIFORGE_HOME = "E:\portable\api-forge-state"
$env:APIFORGE_CONFIG = "E:\portable\api-forge.yaml"
$env:APIFORGE_CACHE = "E:\portable\api-forge-cache"
```

```bash
export APIFORGE_HOME="$HOME/.local/state/api-forge"
export APIFORGE_CONFIG="$HOME/.config/api-forge/config.yaml"
export APIFORGE_CACHE="$HOME/.cache/api-forge"
```

Esses valores são resolvidos sem escrever nada. `inspect` e `doctor` exibem o
package root, executável, state root, configuração, cache e as fontes de cada
path.

## 3. Faça a inspeção inicial

Execute a sequência abaixo no repositório consumidor:

```text
apiforge inspect
apiforge doctor
```

`inspect` confirma os assets empacotados e a descoberta limitada de raízes.
`doctor` verifica permissões, `git`, MCP opcional, rede declarada e hashes dos
assets. Um estado `unavailable`, `degraded` ou `unresolved` é diagnóstico
explícito, não falha da instalação, quando a capacidade é opcional.

## 4. Inicialize somente o manifesto mínimo

Para um repositório comum:

```text
apiforge init
apiforge status
```

Isso cria somente `.apiforge/project.yaml`. Agents, skills, knowledge packs,
contratos e templates continuam pertencendo à instalação do API Forge; eles não
são copiados para o repositório consumidor.

Para criar um workspace virtual:

```text
apiforge init --workspace --name platform
```

O arquivo gerado é `.apiforge/workspace.yaml`. Ele registra raízes
independentes e não transforma os repositórios em monorepo.

## 5. Resolva o contexto do repositório

```text
apiforge context resolve --scope repo
```

O resolver procura a raiz do módulo atual, o repositório Git, o manifesto do
projeto e, quando declarado, o workspace pai. O resultado contém `scope`,
`targets`, `included_repositories`, `graph`, `funnel`, `evidence`, `gaps` e
`unresolved`.

`apiforge here` não existe nesta onda: a resolução é interna ao `context` e às
outras facades.

## 6. Registre repositórios independentes

No diretório escolhido para o workspace:

```text
apiforge workspace discover --root E:\work\platform
apiforge workspace init --root E:\work\platform --name platform
apiforge workspace add E:\work\orders --root E:\work\platform
apiforge workspace add E:\work\billing --root E:\work\platform
apiforge workspace status --root E:\work\platform
```

Em POSIX, substitua os caminhos, por exemplo:

```bash
apiforge workspace add "$HOME/work/orders" --root "$HOME/work/platform"
```

Cada repositório conserva seu próprio `.git`. Relações não observadas ficam
`unresolved`; o graph não presume deploy, tráfego ou dependência de produção.

## 7. Restrinja o contexto e o impacto

Use os três escopos fechados:

```text
apiforge context resolve --root E:\work\platform --scope repo
apiforge context resolve --root E:\work\platform --scope workspace
apiforge context resolve --root E:\work\platform --scope target --target repository:<id>
apiforge context resolve --root E:\work\platform --scope workspace --impact direct
apiforge context resolve --root E:\work\platform --scope workspace --impact transitive
```

Os valores aceitos para `--impact` são `direct`, `transitive` e `all`. Um alvo
desconhecido retorna `AF-CONTEXT-TARGET-NOT-FOUND`; não é convertido em uma
seleção heurística silenciosa.

## 8. Roteamento, scorecards e expertise sem host

A distribuição portátil também executa o núcleo de roteamento sem Claude,
Codex, Devin, Copilot, MCP ou rede. Depois de criar um TaskSpec, rode:

```bash
apiforge runtime run <task-id> --root .
apiforge runtime status <task-id> --root .
```

Na run, `routing.json` guarda a decisão compatível e `routing-plan.json`
separa primary, fallbacks, revisão paralela, reviewer, critic e referee.
Fallbacks não usados são `skipped` com motivo; a execução padrão continua
determinística e bounded.

Scorecards podem registrar qualidade por dimensão, custo, duração, tokens e
frescor. O gate pode exigir `golden`, `holdout`, `mutation` e `adversarial`;
receipts são obrigatórios para sinais observados e dados stale/unresolved não
promovem qualidade. Expertise packs são carregados localmente, e uma família
pode selecionar mais de uma implementação. Se um pack exigido não estiver
disponível, o candidato é recusado com `AF-CAPABILITY-ELIGIBILITY` e
`field=capability.expertise_packs`.

## 9. Use hosts e MCP somente quando necessário

O core não exige Claude, Codex, Devin, Copilot ou MCP. Quando um host estiver
presente, inspecione as capacidades e gere um plano:

```text
apiforge agentops hosts
apiforge agentops parity
apiforge agentops negotiate --capability mcp
apiforge agentops activation-plan --host claude
apiforge agentops activation-plan --host gpt-codex
apiforge agentops activation-plan --host devin
apiforge agentops activation-plan --host copilot
```

O plano é `plan_only`, mostra a origem/hash do template e exige aprovação para
ações mutáveis. Não há sobrescrita automática de arquivos do usuário. MCP local
usa stdio; se o extra não estiver instalado, a CLI continua utilizável e o
refusal é `AF-MCP-OPTIONAL-UNAVAILABLE`.

## 10. Rode a cadeia determinística completa

Depois de inicializar um case, a sequência governada é:

```text
analyze → next-step → graph → evidence → brief
```

Exemplo:

```bash
apiforge analyze \
  --contract tests/fixtures/openapi/orders-v1.yaml \
  --project tests/fixtures/fastapi_orders \
  --out-dir .apiforge/case

apiforge next-step --findings .apiforge/case/findings.json --phase verify
apiforge graph build --case .apiforge/case --out .apiforge/graph
apiforge evidence emit --case .apiforge/case --out .apiforge/evidence/receipt.json
apiforge evidence verify --receipt .apiforge/evidence/receipt.json
apiforge task create platform-review --outcome "revisar a plataforma" --root .apiforge
apiforge brief show --task platform-review --root .apiforge
```

Não remova diagnósticos ou `unresolved` para obter `DONE`. Um receipt prova
correspondência de bytes; ele não prova autoria, deploy, permissão ou saúde de
produção.

## 11. Solução de problemas

| Situação | Comando/ação segura |
|---|---|
| Sem permissão no diretório padrão | Defina `APIFORGE_HOME` e `APIFORGE_CACHE` para paths do usuário. |
| Executável não está no `PATH` | Use o caminho absoluto do virtual environment. |
| Rede bloqueada | Mantenha operação offline; `doctor` nomeia a limitação. |
| MCP ausente | Instale `apiforge[mcp]` somente se precisar de MCP local. |
| Manifesto inválido | Preserve o arquivo, leia `AF-MANIFEST-INVALID` e corrija o campo indicado. |
| Arquivo de host em conflito | Revise o plano/hash; não use sincronização automática. |
| Nenhuma raiz encontrada | Execute a partir do repositório ou passe `--root` explicitamente. |

Os itens adiados — orquestração autônoma de alto nível, inferência completa,
`apiforge here`, auto-update, symlink garantido, overwrite automático,
precedência por task, debate distribuído e paridade total — continuam no
roadmap e não são ativados implicitamente.
