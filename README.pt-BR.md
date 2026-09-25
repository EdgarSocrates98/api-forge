# API Forge

Engenharia determinística, offline-first e local-first de APIs com evidência,
contratos, graph, SDD e execução de agentes governada.

[English README](README.md) · [Guia portátil em português](docs/guides/API_FORGE_PORTABLE_DISTRIBUTION.pt-BR.md) · [Portable guide in English](docs/guides/API_FORGE_PORTABLE_DISTRIBUTION.md)

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

Os itens adiados — `ask`, `improve`, `migrate`, `fix`, inferência completa,
`apiforge here`, auto-update, symlink, overwrite automático, precedência por
task, debate distribuído e paridade total — continuam no roadmap.
