# API Forge — control plane de API, Git e CI/CD

Idioma: [English](API_FORGE_API_GIT_CICD_CONTROL_PLANE.md) · [Português (Brasil)](API_FORGE_API_GIT_CICD_CONTROL_PLANE.pt-BR.md)

## Fronteira

O recurso normaliza um pull request, branch ou artefato de replay em
`ChangeBundle/v1`. O core consome esse bundle sem importar SDK do GitHub nem
chamar um provedor. A coleta externa fica isolada atrás de
`ReadOnlyTransport` e `GitHubReadOnlyAdapter`; a reprodução local usa
`ReplayAdapter`.

```text
provider/replay
      |
      v
ChangeBundle/v1
      |
      v
analyze -> next-step -> graph -> evidence -> brief
      |                         |
      +--> recommendation eval  +--> result + metrics
                                  +--> verify -> JUnit/Markdown
                                  +--> projeções locais IDE/UI
```

O pipeline emite um `ChangeControlResult` canônico e não permite que CLI, MCP,
IDE ou UI reinterpretem estado de suporte, status, evidência, limitações ou
lacunas. As superfícies são projeções sobre a mesma matriz.

## Determinismo

As entradas de contrato e projeto são hasheadas pelo case service existente.
Artefatos de grafo e receipt são canônicos. A identidade da execução deriva
do repositório, SHA base e SHA head. Durações de etapas são observações
operacionais armazenadas em `metrics.json` e não entram nas decisões
determinísticas.

O ingresso live grava um `ChangeCollectionReceipt` ao lado do bundle
sanitizado. Ele vincula provedor, refs, hashes de origem, resumos de checks e
o SHA-256 do bundle sem persistir credenciais. O receipt prova quais bytes
foram coletados em determinado momento; não prova autoria, saúde do deploy,
freshness do provedor ou permissões além da observação declarada.

## Governança das recomendações

`Recommendation/v1` exige recomendação, fatos, premissas, alternativas, riscos,
itens não resolvidos, referências de evidência, verificador e confiança. O
avaliador local verifica a forma e a evidência declarada. Ele não afirma que a
recomendação está correta em produção; um verificador independente e
aprovação humana continuam necessários para uma decisão de release.

## Reports publicados e superfícies host

`apiforge change-control publish` produz JUnit XML, Markdown, SARIF e HTML
standalone determinísticos a partir de `result.json`; o CI os publica como
artefatos. O mesmo resultado canônico está disponível por
`change-control surface --surface ide|ui` e no host `change-control serve` em
`/api/ide`, `/api/ui`, `/api/result`, `/healthz`, `/readyz` e nos quatro
endpoints de reports.

O host faz bind em loopback por padrão, não serve arquivos do projeto e não
executa mutações externas. Um deploy remoto ou de produção ainda exige
autenticação, política de rede e retenção controladas pelo host.

## Caminho de evolução

Freshness do provedor é representada por `af-external-read-receipt/1` e pode
ser verificada com `apiforge integration verify-receipt`. Servir UI/IDE remoto
é suportado pelo host autenticado com TLS, pela receita de container e pelo
workflow do GitHub Pages. Mutação continua sendo um adaptador de host
separado: a fronteira CI-only `scripts/github_pr_host.py` pode criar/reusar um
PR e solicitar auto-merge, emitindo `af-github-pr-receipt/1`; o core continua
sem poder executar essas operações. Saúde de deploy permanece um receipt GET
separado, não uma inferência de um build verde.
