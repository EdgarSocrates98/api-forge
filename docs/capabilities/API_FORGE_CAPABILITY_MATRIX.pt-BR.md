# Matriz de capacidades do API Forge

Idioma: [English](API_FORGE_CAPABILITY_MATRIX.md) · [Português (Brasil)](API_FORGE_CAPABILITY_MATRIX.pt-BR.md)

A fonte legível por máquina é
`src/apiforge/rules/capability_matrix.yaml`. Este documento explica como ler
essa fonte e o significado de cada estado.

Para o fluxo operacional completo, consulte [Uso da plataforma](../guides/API_FORGE_PLATFORM_USAGE.md).

| Estado | Significado | O que não significa |
|---|---|---|
| `supported` | O caminho local possui contrato, fonte de evidência e verificador | Não prova todos os provedores ou modos de runtime |
| `heuristic` | Uma projeção determinística fornece orientação útil a partir de evidência estática ou declarada | Não prova comportamento live, índices, lag, custo ou performance |
| `unresolved` | A pergunta é válida, mas falta evidência necessária ou adapter seguro | Não é um finding negativo |
| `unsupported` | A fronteira atual do produto recusa intencionalmente a capacidade | Não é uma tentativa silenciosa |

Todo registro público declara vertical, operação, superfícies suportadas,
evidências, limitações, pré-requisitos, risco, rollback e verificador. O
comando `apiforge capabilities verify` verifica esses campos e os caminhos de
documentação.

## Capacidades principais

| Capacidade | Estado | Limitação principal |
|---|---|---|
| `api.analyze` | supported | Adapters estáticos não executam o código da aplicação. |
| `api.next-step` | supported | Findings precisam mapear para o catálogo de routing. |
| `api.provenance` | supported | Aceitação ainda exige verificação independente. |
| `database.inspect` | heuristic | Query plans, índices e cardinalidade exigem evidência do banco. |
| `database.verify-runtime` | supported | Prova a fixture SQLite local commitada, não um banco remoto. |
| `messaging.inspect` | heuristic | Lag de broker e garantias de entrega exigem observações. |
| `messaging.verify-runtime` | supported | Prova entrega/ack local, não garantias do broker. |
| `cicd.inspect` | heuristic | Configuração de pipeline não prova execução. |
| `cicd.verify-runtime` | supported | Prova o ensaio local do pipeline, não o CI hospedado. |
| `cloud.inspect` | heuristic | Estado remoto e posture live exigem evidência explícita. |
| `cloud.verify-runtime` | supported | Prova parse local de IaC, não apply ou posture cloud. |
| `frontend.inspect` | heuristic | Browser e acessibilidade exigem host frontend. |
| `frontend.verify-runtime` | supported | Prova a fixture local tipada, não acessibilidade no browser. |
| `git.plan` | unresolved | O core offline não altera um host Git. |
| `api.change-control` | supported | Freshness do provedor e segurança de deploy continuam não provadas. |
| `git.read-context` | heuristic | Leituras GitHub são GET-only e não estabelecem sozinhas freshness ou permissões. |
| `cicd.inspect-run` | heuristic | Observações de checks não provam deploy ou saúde de runtime. |
| `external.apply` | unsupported | Mutação live exige adapter aprovado e rollback. |

## Regras de evidência

- Fixture é exemplo de entrada, não prova de produção.
- Golden é resultado esperado revisado para uma entrada representativa.
- Holdout exercita incerteza, evidência ausente ou caminho negativo.
- Receipt vincula artefatos persistidos a hashes e metadados de política.
- Recomendação de agente deve separar fatos, premissas, riscos e itens não
  resolvidos.
- Ferramenta externa ausente permanece visível como pré-requisito ou limitação.

## Change-control de API + Git + CI/CD

O caminho público de replay é:

```bash
apiforge change-control run \
  --bundle tests/fixtures/api_git_cicd/change_bundle.json \
  --out-dir .apiforge/change-control
apiforge change-control verify --run-dir .apiforge/change-control
```

O bundle é `af-change-bundle/1`. Ele normaliza refs do repositório, entradas
de contrato e projeto, observações do provedor, checks de CI, política e
limitações. A execução emite `analyze -> next-step -> graph -> evidence ->
brief`, além de `result.json`, `metrics.json` e uma recomendação
determinística.

`GitHubReadOnlyAdapter` é injetado por transporte e expõe somente requests
GET. Nunca faz merge, push, dispatch de workflow, deploy ou alteração de
estado. A coleta live é uma etapa separada de evidência e permanece
`heuristic` até que um receipt anonimizado prove freshness e permissões.

`apiforge platform verify-runtime` executa somente probes commitados e
allowlisted em `tests/fixtures/platform/`, emitindo
`af-platform-runtime-receipt/1`. Isso é evidência de execução local real para
cada vertical, não uma afirmação sobre um provedor remoto.

## Adicionando uma capacidade

Adicione um registro ao YAML, documente-o aqui, forneça um verificador e as
fixtures, golden e holdout correspondentes quando a vertical exigir. Não mude
`unsupported` para `supported` só porque existe um parser ou prompt; a mudança
de estado exige evidência independente.
