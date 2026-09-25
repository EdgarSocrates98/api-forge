# API Forge

Engenharia determinística, offline-first e local-first de APIs com evidência,
contratos, graph, SDD e execução de agentes governada.

[English README](README.md) · [Índice de documentação](docs/README.pt-BR.md) · [Documentation index in English](docs/README.md) · [Guia portátil em português](docs/guides/API_FORGE_PORTABLE_DISTRIBUTION.pt-BR.md) · [Portable guide in English](docs/guides/API_FORGE_PORTABLE_DISTRIBUTION.md)

## Instalação sem administrador

```powershell
uv venv E:\tools\api-forge-env
E:\tools\api-forge-env\Scripts\python.exe -m pip install 'apiforge[all]'
$env:PATH = "E:\tools\api-forge-env\Scripts;$env:PATH"
```

```bash
uv venv "$HOME/.local/share/api-forge-env"
"$HOME/.local/share/api-forge-env/bin/python" -m pip install 'apiforge[all]'
export PATH="$HOME/.local/share/api-forge-env/bin:$PATH"
```

Se o local padrão não for gravável:

```text
APIFORGE_HOME   estado do usuário
APIFORGE_CONFIG configuração opcional
APIFORGE_CACHE  cache local
```

## Passo a passo rápido

```text
apiforge inspect
apiforge doctor
apiforge init
apiforge status
apiforge context resolve --scope repo
```

Para repositórios independentes:

```text
apiforge workspace init --root <workspace> --name platform
apiforge workspace add <repo> --root <workspace>
apiforge workspace status --root <workspace>
apiforge context resolve --root <workspace> --scope workspace
```

Os escopos de contexto são `repo`, `workspace` e `target`; o impacto pode ser
`direct`, `transitive` ou `all`. O projeto consumidor recebe apenas manifests
mínimos; agents, skills, knowledge e templates permanecem na instalação.

### Roteamento adaptativo entregue em três ondas

O programa de roteamento adaptativo está concluído e disponível no core
portátil e sem host:

- Onda 1 adiciona `RoutingPlan/v1` com papéis explícitos de primary, fallback,
  paralelo, reviewer, critic e referee.
- Onda 2 adiciona scorecards multidimensionais, sinais com frescor, receipts
  para observações e um gate opcional de avaliação adversarial.
- Onda 3 adiciona expertise packs locais versionados, roteamento por
  família/implementação e recusa explícita quando o conhecimento local exigido
  não está disponível.

As runs preservam `routing.json` para a decisão compatível e
`routing-plan.json` para o plano de execução bounded. As três ondas não exigem
host, rede, SDK de modelo ou mutação externa. O mapa de evolução registra os
itens pós-ship ainda adiados, incluindo orquestração de alto nível com
`ask`/`improve`/`migrate`/`fix`, inferência completa de relações, atualização
remota de Knowledge Packs, instalação por symlink, overwrite automático de
arquivos de host, precedência por task, debate distribuído no workspace e
paridade total entre hosts.

## Hosts e MCP

Claude, Codex, Devin, Copilot e MCP são adapters opcionais. Verifique:

```text
apiforge agentops hosts
apiforge agentops parity
apiforge agentops negotiate --capability mcp
apiforge agentops activation-plan --host claude
```

Ativação é `plan_only`, com hash de origem e aprovação para mutações. Não há
overwrite automático de arquivos do usuário. Rede bloqueada ou MCP ausente não
impedem o uso local do core.

## Fluxo governado

```text
analyze → next-step → graph → evidence → brief
```

Preserve sempre `facts`, hashes, receipts, diagnósticos e `unresolved`. Um
receipt prova correspondência de bytes, não autoria, deploy ou saúde de
produção.

## Documentação

- [Uso da plataforma em português](docs/guides/API_FORGE_PLATFORM_USAGE.md)
- [Platform usage in English](docs/guides/API_FORGE_PLATFORM_USAGE.en.md)
- [Interoperabilidade em português](docs/guides/API_FORGE_EXPERIENCE_INTEROPERABILITY.md)
- [Interoperability in English](docs/guides/API_FORGE_EXPERIENCE_INTEROPERABILITY.en.md)
- [Paridade de hosts em português](docs/HOST_PARITY.pt-BR.md)
- [Host parity in English](docs/HOST_PARITY.md)
- [Mapa de evolução em português](docs/API_FORGE_EVOLUTION_MAP.md)
- [Evolution map in English](docs/API_FORGE_EVOLUTION_MAP.en.md)
- [Catálogo de contratos e recusas](docs/catalog-contract.md)
- [Política de segurança em português](SECURITY.pt-BR.md)
- [Security policy in English](SECURITY.md)
- [Especificação de encerramento em português](SPEC.pt-BR.md)
- [Product closure specification in English](SPEC.md)
- [Arquitetura e fronteiras do MVP em português](docs/architecture/API_FORGE_PLATFORM_COMPLETION.pt-BR.md)
- [Architecture and MVP boundaries in English](docs/architecture/API_FORGE_PLATFORM_COMPLETION.md)
- [Matriz de capacidades em português](docs/capabilities/API_FORGE_CAPABILITY_MATRIX.pt-BR.md)
- [Capability matrix in English](docs/capabilities/API_FORGE_CAPABILITY_MATRIX.md)
- [Host de change-control em português](docs/integrations/API_FORGE_CHANGE_CONTROL_HOST.pt-BR.md)
- [Change-control host in English](docs/integrations/API_FORGE_CHANGE_CONTROL_HOST.md)
- [Integração Devin em português](docs/integrations/API_FORGE_DEVIN.pt-BR.md)
- [Devin integration in English](docs/integrations/API_FORGE_DEVIN.md)
- [Integrações de observabilidade em português](docs/OBSERVABILITY_INTEGRATIONS.md)
- [Observability integrations in English](docs/OBSERVABILITY_INTEGRATIONS.en.md)
- [Roadmap prioritário em português](docs/roadmaps/API_FORGE_PRIORITY_EXECUTION_ROADMAP.md)
- [Priority roadmap in English](docs/roadmaps/API_FORGE_PRIORITY_EXECUTION_ROADMAP.en.md)
