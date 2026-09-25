# API Forge Platform Usage

Este guia descreve o uso público da fundação de completude da API Forge. Ele
é válido para CLI, MCP, bridges de IDE e projeções de UI porque essas surfaces
compartilham `CapabilityRequest/v1` e `CapabilityResult/v1`.

## 1. Princípio operacional

API Forge é um control plane determinístico, offline-first e evidence-first.
Ele observa artefatos, constrói IRs e facts, recomenda técnicas e arquiteturas
e produz planos verificáveis. Não presume que um parser provou runtime, que um
golden provou produção ou que uma integração nominal tem permissão para mutar.

Agents devem entender a necessidade antes de recomendar. A resposta deve
separar observações, premissas, alternativas, trade-offs, riscos, limitações,
gaps e o próximo verificador. Não há wizard obrigatório: a adaptação acontece
por contexto, contratos e evidências.

Antes de uma análise:

```text
1. Leia AGENT_PROTOCOL.md.
2. Carregue ou crie um case em .apiforge/case/.
3. Se houver findings, rode apiforge next-step antes de escolher especialista.
4. Preserve todos os diagnósticos e hashes.
```

## 2. Instalação e primeiro diagnóstico

```bash
python -m pip install -e '.[dev]'
apiforge capabilities list
apiforge capabilities verify
apiforge analyze \
  --contract tests/fixtures/openapi/orders-v1.yaml \
  --project tests/fixtures/fastapi_orders \
  --out-dir .apiforge/case
```

`capabilities verify` deve retornar `ok: true`. Se uma capability aparecer
como `heuristic`, `unresolved` ou `unsupported`, esse estado é a conclusão
correta até que sua evidência e verificador sejam adicionados.

## 2.1 Distribuição portátil e operação sem host

O pacote pode ser instalado em virtual environment, prefixo user-local,
volume, container ou outro diretório escolhido pelo usuário sem privilégio de
administrador. `APIFORGE_HOME`, `APIFORGE_CONFIG` e `APIFORGE_CACHE` movem o
estado, a configuração e o cache para locais permitidos. O pacote instalado
continua sendo a fonte de verdade; o repositório consumidor recebe apenas
manifests mínimos e adapters explicitamente solicitados.

```text
apiforge inspect
apiforge init
apiforge status
apiforge doctor
apiforge context resolve --scope repo
```

Rede bloqueada, host ausente ou MCP não instalado não impedem SDD, agents,
skills, graph, evidence e verification locais. `doctor` preserva as lacunas
opcionais com estado, `field`, `unlock` e evidência.

Para múltiplos repositórios independentes:

```text
apiforge workspace init --root <workspace>
apiforge workspace add <repo> --root <workspace>
apiforge workspace status --root <workspace>
apiforge context resolve --root <workspace> --scope workspace
```

## 3. Cadeia crítica completa

O fluxo mínimo de prova é:

```text
analyze → next-step → graph → evidence → brief
```

Exemplo usando os artefatos oficiais:

```bash
apiforge next-step \
  --findings .apiforge/case/findings.json \
  --phase verify

apiforge graph build \
  --case .apiforge/case \
  --out .apiforge/graph

apiforge evidence emit \
  --case .apiforge/case \
  --out .apiforge/evidence/receipt.json \
  --now 2026-09-22T00:00:00Z

apiforge evidence verify \
  --receipt .apiforge/evidence/receipt.json

apiforge task create platform-review \
  --outcome "revisar a prontidão da plataforma" \
  --root .apiforge
apiforge brief show --task platform-review --root .apiforge
```

`brief show` pode terminar em `REVIEW`, `DECIDE` ou `BLOCKED`. Isso é uma
decisão governada, não uma falha do pipeline. `DONE` só é aceitável quando a
evidência independente, o receipt, os hashes, os holdouts e os gaps obrigatórios
estão resolvidos.

### Fluxo de mudança API + Git + CI/CD

Para uma mudança de API associada a uma branch, PR ou replay local, use o
bundle versionado e o executor read-only:

```bash
apiforge change-control run \
  --bundle tests/fixtures/api_git_cicd/change_bundle.json \
  --out-dir .apiforge/change-control
apiforge change-control verify --run-dir .apiforge/change-control
apiforge change-control publish --run-dir .apiforge/change-control
apiforge change-control surface --run-dir .apiforge/change-control --surface ide \
  --out .apiforge/change-control/ide.json
apiforge change-control serve --run-dir .apiforge/change-control
```

Quando uma coleta GitHub read-only for autorizada, gere primeiro um bundle
sanitizado. O token é lido apenas da variável de ambiente
`APIFORGE_GITHUB_READ_ONLY_TOKEN` e nunca vira campo do bundle:

```bash
apiforge change-control collect \
  --repository owner/repository \
  --base-sha <40-hex-base> \
  --head-sha <40-hex-head> \
  --pull-number 123 \
  --contract openapi.yaml \
  --project . \
  --out-bundle .apiforge/change-control/change-bundle.json
```

Essa coleta só faz leituras GET; rate limit, escopo ausente e payload inválido
terminam como erro governado. Para forks ou código não confiável, prefira
replay de artefato sem segredos.

O bundle pode ser produzido por um adapter de provider ou revisado como
artefato. O executor não executa a aplicação, não altera GitHub e não presume
que uma check de CI prova deploy ou saúde em produção. Consulte
[`docs/security/api-git-cicd-control-plane.md`](../security/api-git-cicd-control-plane.md)
para limites e
[`docs/architecture/API_FORGE_API_GIT_CICD_CONTROL_PLANE.md`](../architecture/API_FORGE_API_GIT_CICD_CONTROL_PLANE.md)
para o contrato interno.

## 4. Capability matrix

A fonte é `src/apiforge/rules/capability_matrix.yaml` e a explicação humana é
`docs/capabilities/API_FORGE_CAPABILITY_MATRIX.md`.

| Estado | Interpretação | Próximo passo |
|---|---|---|
| `supported` | Existe caminho local reproduzível com contract, evidence e verifier. | Reexecutar o verifier quando os inputs mudarem. |
| `heuristic` | Há orientação determinística a partir de sinais estáticos/declarados. | Coletar evidência de runtime antes de declarar suporte. |
| `unresolved` | A pergunta é válida, mas falta evidência ou adapter seguro. | Nomear o gap e solicitar contexto/evidência. |
| `unsupported` | A operação é recusada pela fronteira atual. | Criar design e policy explícitos antes de implementar. |

Toda capability pública precisa declarar documentação, limitações, evidências,
pré-requisitos, risco, rollback e verificador. O gate é:

```bash
apiforge capabilities verify
```

## 5. Verticais e projetos de exemplo

Cada vertical possui uma célula de prova em `tests/fixtures/platform/`:

| Vertical | Fixture | Golden | Holdout |
|---|---|---|---|
| API | `api/openapi.yaml`, `api/app.py` | `api/golden.json` | `api/holdout.yaml` |
| Database | `database/schema.sql`, `database/repository.py` | `database/golden.json` | `database/holdout.yaml` |
| Messaging | `messaging/asyncapi.yaml`, `messaging/consumer.py` | `messaging/golden.json` | `messaging/holdout.yaml` |
| CI/CD | `cicd/pipeline.yaml` | `cicd/golden.json` | `cicd/holdout.yaml` |
| Cloud | `cloud/main.tf` | `cloud/golden.json` | `cloud/holdout.yaml` |
| Front-end | `frontend/package.json`, `frontend/src/api.ts` | `frontend/golden.json` | `frontend/holdout.yaml` |

Valide a matriz com:

```bash
python -m pytest -q tests/labs/test_platform_verticals.py
```

Fixture é exemplo; golden é expectativa revisada; holdout é o caminho de
incerteza/ausência/negativo. Nenhum deles prova custo, throughput, lag,
permissão, índice, browser behavior ou garantia de entrega em produção.

## 6. Agents e recomendações

O agent `api-platform-completion-reviewer` revisa:

- estado, limites, docs e verifier de cada capability;
- fixture/golden/holdout das seis verticais;
- paridade CLI/MCP/IDE/UI;
- evidências independentes e bloqueios de mutação;
- recomendação arquitetural baseada na necessidade e restrições declaradas.

O output deve seguir `docs/agents/AGENT_OUTPUT_CONTRACT.md`, com no mínimo:
`recommendation`, `facts`, `assumptions`, `alternatives`, `risks`,
`unresolved`, `evidence_refs`, `verifier` e `confidence`. O supervisor rejeita
payload incompleto e mantém os gaps visíveis.

## 7. Git, CI/CD, IDE, UI e integrações

As integrações locais em `src/apiforge/integrations/` oferecem uma boundary
estática/read-only. Elas podem inspecionar contexto, montar plano e nomear
requisitos; não devem publicar, executar SQL, alterar pipeline, fazer deploy,
commitar, enviar mensagens ou mudar topology.

GitHub é suportado somente por `GitHubReadOnlyAdapter` com transporte
injetável; o caminho offline recomendado é `ReplayAdapter`. Isso permite
reproduzir uma decisão sem credenciais e separar prova local de evidência
externa.

Uma ação `apply` só pode avançar quando houver adapter explícito, policy
allowlist, identidade/credencial, aprovação humana, rollback e receipt. Sem
isso, o resultado correto é `blocked`, `unresolved` ou `unsupported`.

CLI, MCP, IDE e UI devem projetar o mesmo resultado canônico. A apresentação
pode mudar; estado, evidência, gaps e semântica de segurança não.

`change-control collect` também escreve um receipt
`af-change-collection-receipt/1` ao lado do bundle. Ele prova a
correspondência dos bytes coletados e os hashes das fontes, mas não prova
autoria, freshness, permissões, deployment ou rollback. `publish` gera as
projeções JUnit, Markdown, SARIF e HTML; `surface` exporta uma projeção para
IDE; e `serve` oferece um host UI/IDE local ou remoto. Binding remoto exige
Bearer token e TLS, salvo uso explícito atrás de proxy HTTPS confiável.

Integrações externas read-only são explícitas e geram
`af-external-read-receipt/1`:

```bash
apiforge integration github-issues \
  --repository owner/repository \
  --out .apiforge/github-issues.json
apiforge integration health \
  --url https://host.example/readyz \
  --out .apiforge/health.json
apiforge integration json \
  --url https://tracker.example/api/issues \
  --out .apiforge/tracker.json
apiforge integration verify-receipt \
  --receipt .apiforge/health.json \
  --now 2026-09-22T12:00:00+00:00
```

O receipt prova a resposta observada e sua janela de frescor declarada; não
prova autoria, rollback, SLO ou saúde geral da aplicação.
O adapter `integration json` pode ler endpoints de Jira, Linear ou outras
ferramentas por URL e token de host, mas preserva o JSON sem inventar semântica
de issue, permissão ou workflow.

Para prova de execução local das seis verticais, use somente os probes
versionados e allowlisted:

```bash
apiforge platform verify-runtime \
  --now 2026-09-22T12:00:00+00:00 \
  --out .apiforge/platform-runtime-receipt.json
```

Esse receipt prova execução local de API, banco, mensageria, CI/CD, cloud/IaC
e front-end. Ele não transforma essa prova em saúde de provider, deployment ou
performance de produção.

## 8. Verificação antes de commit/release

```bash
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src/apiforge
python -m pytest -q
python scripts/check_release.py
apiforge agents check --root .
apiforge capabilities verify
```

Para alterações em skill ou agent, sincronize os mirrors antes dos gates:

```bash
python scripts/sync_skills.py --root .
apiforge agents sync --root .
```

O workflow `.github/workflows/ci.yml` executa os mesmos gates em cada push.
Quando um push para uma branch diferente de `main` termina verde, o job
`open-green-pr` abre ou reutiliza uma PR para `main` através do host dedicado
`scripts/github_pr_host.py`, que emite um receipt de mutação. Ele possui apenas
permissão para ler o conteúdo e criar PR; merge, push, deploy e dispatch
continuam proibidos por padrão. Para habilitar a criação, o repositório deve fornecer o
secret `APIFORGE_PR_TOKEN` com escopo mínimo de pull request, ou um
administrador deve habilitar “Allow GitHub Actions to create and approve pull
requests” nas configurações de Actions. O token pessoal nunca deve ser
commitado nem gravado em arquivos do projeto.

## 9. Limitações públicas

O container `Dockerfile.change-control`, o compose restrito e o workflow de
Pages fornecem implantação reproduzível do host remoto read-only. Ainda assim,
o operador precisa configurar domínio, TLS, secret, retenção e monitoramento
do ambiente de produção. O auto-merge é opt-in por `APIFORGE_AUTO_MERGE=true`
e continua sujeito às regras de proteção da branch. Providers live específicos,
scanners ausentes e benchmarks de produção só podem ser promovidos após um
receipt externo e verificador independente.
