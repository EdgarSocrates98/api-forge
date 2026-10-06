# Host IDE/UI de change-control

Idioma: [English](API_FORGE_CHANGE_CONTROL_HOST.md) · [Português (Brasil)](API_FORGE_CHANGE_CONTROL_HOST.pt-BR.md)

O host transforma uma execução concluída de `change-control` em uma ponte
somente leitura para browser e IDE sem introduzir um segundo contrato de
resultado. Ele pode rodar localmente ou como serviço TLS autenticado atrás de
um host controlado.

```bash
apiforge change-control serve --run-dir .apiforge/change-control
```

O bind padrão é `127.0.0.1`. Os endpoints fixos são:

| Endpoint | Finalidade |
|---|---|
| `/` | Report visual sem dependências. |
| `/api/result` | `ChangeControlResult` canônico. |
| `/api/ide` | Envelope `CapabilityResult/v1` para um host IDE. |
| `/api/ui` | Mesmo resultado canônico para uma superfície visual. |
| `/healthz` | Liveness sem dados do projeto. |
| `/readyz` | Readiness que prova que `result.json` é legível. |
| `/reports/change-control.junit.xml` | Projeção JUnit compatível com CI. |
| `/reports/change-control.md` | Projeção Markdown para revisão humana. |
| `/reports/change-control.sarif.json` | SARIF compatível com code scanning. |
| `/reports/change-control.html` | Report HTML estático para hosting remoto. |

O host lê somente o diretório da execução selecionada e não expõe rota de
arquivo arbitrário. Ele não pode fazer merge, push, dispatch, deploy,
comentário, mudança de status ou autofix. `state`, `status`, `evidence`,
`gaps` e `limitations` são copiados do resultado canônico; uma superfície não
pode promover `review`, `blocked` ou `unresolved` para sucesso.

Para um editor que prefere um artefato a HTTP:

```bash
apiforge change-control surface \
  --run-dir .apiforge/change-control \
  --surface ide \
  --out .apiforge/change-control/ide.json
```

O host prova um deploy local. Um deploy compartilhado ou de produção ainda
precisa de autenticação, TLS, política de rede, retenção, identidade e
verificação independente controlados pelo host. Um bind remoto recusa iniciar
sem Bearer token e TLS; `--trust-proxy` só é permitido quando um proxy HTTPS
confiável termina o TLS antes do host.

Para um host remoto conteinerizado:

```powershell
$env:APIFORGE_HOST_TOKEN = 'use-a-secret-manager-value'
docker compose -f docker-compose.change-control.yml up --build
```

Monte certificado e chave em `deploy/tls/`, ou termine HTTPS em um proxy
confiável seguindo a fronteira documentada. O container é somente leitura,
remove capabilities Linux e expõe apenas a execução selecionada.

O repositório também contém `.github/workflows/change-control-pages.yml`.
Depois que Pages estiver habilitado, ele publica HTML, Markdown e SARIF
standalone a partir do resultado canônico em `main`. Se Pages ainda não
estiver habilitado, configure um plano compatível e o secret
`APIFORGE_PAGES_TOKEN`. Esse token é usado apenas por
`actions/configure-pages` na habilitação inicial; o host de runtime continua
sem autoridade de mutação.

## Ciclo de PR verde

O workflow de CI abre ou reutiliza o pull request somente depois de o job
completo de validação passar. Um administrador pode habilitar o job separado
de auto-merge definindo a variável de repositório
`APIFORGE_AUTO_MERGE=true`; o job usa o token do workflow, lê o PR de volta e
envia um receipt `af-github-pr-receipt/1`. O receipt prova a solicitação e a
leitura posterior, não autoria, branch protection, conclusão do merge ou saúde
do deploy. Habilite essa variável somente com a política de reviews e checks
obrigatórios do repositório; o core e os agentes nunca recebem autoridade de
merge.
