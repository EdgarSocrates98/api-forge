# Distribution-v1 (PT-BR)

O API Forge é um pacote Python instalado. O pacote, e não um mirror copiado
para o repositório consumidor, é dono do executável, contratos, agents, skills,
knowledge packs, templates SDD e adapters de host.

[English](Distribution-v1.md) · [Guia portátil](../guides/API_FORGE_PORTABLE_DISTRIBUTION.pt-BR.md)

## Paths

| Nome | Padrão | Override |
|---|---|---|
| Package root | pacote `apiforge` instalado | exibido por `apiforge inspect` |
| Estado do usuário | `<project>/.apiforge` | `APIFORGE_HOME` |
| Configuração | ausente | `APIFORGE_CONFIG` |
| Cache | `<state>/cache` | `APIFORGE_CACHE` |

Valores são normalizados para caminhos absolutos. O API Forge nunca escreve no
package root. O usuário pode instalar em virtualenv, prefixo local, volume
montado ou outro caminho gravável sem privilégio administrativo.

## Operação sem host

`inspect`, `init`, `status`, `doctor`, `context`, SDD, agents, skills, graph,
evidence e verification não exigem processo host, porta de rede, SDK de
provider ou servidor MCP remoto. `doctor` retorna capacidades opcionais com
estado e `field`/`unlock` acionáveis.

## Proveniência de assets

Assets empacotados são carregados por `importlib.resources` e expõem SHA-256.
Assets ausentes ou divergentes são recusados com código nomeado. Repositórios
consumidores recebem apenas manifests mínimos e adapters solicitados e
visualizáveis.
