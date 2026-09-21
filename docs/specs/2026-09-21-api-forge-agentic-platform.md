# API Forge — Plataforma agêntica de especialistas em APIs

Data: 2026-09-21. Status: visão operacional — expande o spec arquitetural
(`2026-09-21-api-forge-design.md`) no desenho concreto do time de
especialistas, do catálogo de verbos, dos catálogos de regras e da sequência
de entrega. Inspiração estrutural: spark-forge-aws (coordinators + executors
+ catálogo de regras + knowledge packs + gates por evidência + economia
medida), transplantado para o domínio de APIs.

## 1. Posição

API Forge é uma plataforma **agentic-first, deterministic-core**: um time de
especialistas em APIs cujo trabalho inteiro se apoia em evidência extraída
deterministicamente. O LLM orquestra, decompõe e redige — nunca extrai fatos
amostrando código. O produto do sistema é evidência verificável, não
narrativa.

Disciplinas herdadas, inegociáveis:

- **Três estados, nunca dois.** `confirmed`, `unresolved`, ou recusa nomeada.
  Ausência de evidência não é evidência de ausência — o ponto cego é
  reportado pelo nome.
- **Determinístico antes de LLM.** Extratores são offline; `collect *` é a
  única família que toca AWS; o core não importa `openai`, `anthropic`,
  `boto3`, `litellm` (o release gate já enforce).
- **Facts sem julgamento, Findings sempre com evidence.** Todo finding carrega
  `rule_id` rastreável a fonte datada + `evidence` não-vazia de `fact_id`.
- **Gates destravam por evidência, nunca por flag.** O que abre um gate é a
  presença do kind de fato exigido, não `--gate-value true`.
- **Economia medida, nunca reivindicada.** `detail_level` em toda tool MCP,
  `payload_bytes` registrado por chamada, `economy report` compara níveis
  antes de concluir.

## 2. O time de especialistas

Poucos papéis estáveis (spec §8); especialização entra por **knowledge pack +
catálogo de regras**, não por multiplicar agentes. Coordinators decidem e
registram quem executou; executors executam. Coordinators despachados como
subagent não despacham executors — a decomposição roda inline.

### Coordinators de domínio

| Coordinator | Pergunta que responde | `rule_areas` |
|---|---|---|
| `api-contract-architect` | o contrato está bem desenhado? recursos, naming, métodos, status, paginação, filtros, idempotência, maturidade REST, Problem Details | AF-DESIGN, AF-REST, AF-ERR |
| `api-governance-reviewer` | a evolução respeita a política? lint, style guide, breaking changes, versionamento, depreciação, lifecycle, consumer impact | AF-GOV, AF-BREAKING, AF-VERSION |
| `api-security-reviewer` | a API é segura por operação? OWASP API Top 10, authN/authZ, BOLA/BFLA, scopes, rate limiting, CORS, transport, supply chain | AF-SEC, AF-AUTHZ, AF-DEPSEC |
| `api-performance-engineer` | onde está o gargalo e a mudança melhorou? baseline→hipótese→mudança→benchmark→validação funcional | AF-PERF, AF-BENCH |
| `api-testing-strategist` | a pirâmide cobre o risco? contrato, integração, property-based, fuzz, mutação, carga, chaos | AF-TEST |
| `api-reliability-engineer` | a API sobrevive a falha? timeout, retry/jitter, circuit breaker, bulkhead, backpressure, graceful shutdown, SLO | AF-REL |
| `aws-api-infra-reviewer` | a infra AWS da API está certa? API Gateway REST/HTTP/WS, Lambda, ALB, WAF, Cognito, IAM, usage plans, throttling, quotas | AF-GW, AF-LAMBDA, AF-WAF, AF-IAM |
| `api-modernization-specialist` | como sair do legado sem quebrar consumidor? monólito→serviços, runtime/framework upgrade, REST↔gRPC/GraphQL, Strangler | AF-MIG |
| `api-observability-engineer` | dá para operar e depurar? OTel, logs estruturados, RED/USE, tracing, SLI/SLO, alertas | AF-OBS |
| `api-dx-docs-reviewer` | um consumidor consegue usar? docs completas, exemplos, SDK gerado, qualidade de erro, changelog | AF-DOC |

### Papéis de plataforma (spec §8)

`orchestrator` (intenção, risco, orçamento, handoffs), `af-inventory`,
`af-extractor`, `af-judge`, `af-verifier`, `af-synthesizer` (os cinco
executors — mesma fronteira `## Não faz` / `## Pressupõe`/`## Entrega` do
spark-forge), `builder` (só em sandbox/worktree), `release-guardian`
(evidence bundle, rollout, rollback).

### Roteamento é dado, não julgamento

`rules/catalog/routing.yaml` mapeia (fase do caso, área dominante do finding)
→ `recommended_agent`. `apiforge next-step` lê o catálogo; ninguém escolhe
coordinator por inspeção. Debate multiagente só nos gatilhos do spec §8 —
decisão concorrente, contradição de evidência, mudança crítica, regressão
inexplicada, migração de alto risco — e o resultado é decisão estruturada,
não transcript.

## 3. Superfície de verbos

`analyze *` extrai de artefato já em disco; `collect *` toca AWS e exige
`--now` explícito; verbos de composição operam sobre facts já extraídos e
nunca leem artefato. Paridade CLI/MCP é requisito (spec §12).

### analyze * — extratores determinísticos

| Artefato | Verbo | Lê |
|---|---|---|
| OpenAPI 3.1 | `analyze openapi` | documento (strict loader) — **feito** |
| AsyncAPI | `analyze asyncapi` | documento de eventos/mensagens |
| GraphQL / gRPC | `analyze graphql-schema`, `analyze protobuf` | SDL / `.proto` |
| Código Python | `analyze fastapi` | `*.py` via `ast.parse` — **feito** |
| Código Java | `analyze spring-boot` | `*.java` via tree-sitter (decisão §8) |
| Código Go | `analyze go-chi` | `*.go` via tree-sitter (decisão §8) |
| Lint de contrato | `analyze spectral-report`, `analyze vacuum-report` | saída SARIF/JSON das ferramentas |
| Diff de contrato | `analyze contract-diff` | dois OpenAPI — **feito** (bounded) |
| Contract tests | `analyze pact`, `analyze schemathesis-report` | pactos / saída JSON |
| Coleções | `analyze postman`, `analyze har` | exports |
| Carga | `analyze k6`, `analyze gatling`, `analyze jmeter`, `analyze locust` | relatórios de benchmark |
| Segurança | `analyze zap-report`, `analyze semgrep`, `analyze trivy`, `analyze gitleaks` | relatórios de scanner |
| IaC de API | `analyze terraform-api`, `analyze sam-api`, `analyze cdk-api` | `aws_api_gateway_*`, `AWS::Serverless::Api`, constructs |
| Dumps AWS | `analyze gateway-dump`, `analyze waf`, `analyze cognito`, `analyze iam-access`, `analyze cloudwatch-api` | JSON de describe/get |
| Test coverage | `analyze coverage` | jacoco/coverage.xml/go-cover |

### collect * — únicos que tocam AWS

`collect gateway`, `collect lambda`, `collect waf`, `collect iam-access`
(`iam:SimulatePrincipalPolicy` — simula, nunca parseia policy), `collect
cloudwatch`. Todos exigem `--now`; credenciais temporárias; escopo mínimo.

### Verbos de composição

`review`, `design`, `plan-change`, `harden`, `tune`, `test-plan`, `migrate`,
`benchmark`, `release-evidence`, `investigate`, `economy report`,
`next-step`. Cada um responde uma pergunta sobre facts — nenhum lê artefato.

## 4. Catálogo de regras

`src/apiforge/rules/catalog/` cresce de `contract.yaml` para áreas por
arquivo — schema fechado, `action:` block em vocabulário trancado,
`runtime_scope` com version guard, `expected_gain` **recusado por schema**
(afirmar economia exige o custo do run que não aconteceu):

```
contract.yaml      routing.yaml    design.yaml      rest.yaml
errors.yaml        versioning.yaml security.yaml    authz.yaml
depsec.yaml        perf.yaml       bench.yaml       resilience.yaml
testing.yaml       gateway.yaml    lambda-api.yaml  waf.yaml
observability.yaml docs-dx.yaml    migration.yaml   breaking.yaml
gates.yaml         proof_axes.yaml env.yaml
```

Fontes normativas datadas por área (cada regra cita a fonte + data de
verificação): RFC 9110 (semântica HTTP), RFC 9457 (Problem Details), SemVer
para contratos, Google AIPs, Zalando RESTful Guidelines, OWASP API Security
Top 10 (2023), OWASP Cheat Sheets, well-architected API Gateway/Lambda
guidance, politica de depreciação RFC 8594 (`Sunset` header).

Regras determinísticas representativas por área:

- **design**: path usa substantivo plural; verbo fora do path; `GET` sem
  body; coleção paginada; mutação com idempotency key documentada.
- **errors**: erro estruturado `application/problem+json`; status coerente
  com `response` declarado; sem stack trace em payload.
- **security**: operação sem `security` declarada quando o API exige auth;
  `401`/`403` documentados; scope por operação; rate limit/throttle
  declarado no gateway; `Authorization` não vaza para logs.
- **breaking**: catálogo `AF-BREAKING-*` já entregue no MVP — estendido a
  parâmetros required, enums encolhendo, default mudando.
- **perf**: endpoint de listagem sem paginação; payload sem bound; N+1
  detectável no call graph; ausência de `Cache-Control` em GET estável.
- **testing**: operação de contrato sem pacto/schemathesis correspondente;
  endpoint crítico sem teste de contrato; fuzz ausente em handler que
  desserializa.
- **gateway**: rota declarada no código sem recurso no Terraform/SAM; stage
  sem throttling; API sem WAF quando exposta.

## 5. Knowledge packs

`knowledge/<domínio>/` com `source_authority.yaml` + data de verificação —
conteúdo sensível a versão sempre citado. Packs iniciais:

```
http-semantics/        rest-design/          openapi-31/
json-schema/           problem-details/      pagination-versioning/
idempotency/           oauth-oidc/           owasp-api-2023/
api-style-guides/      perf-methodology/     contract-testing/
resilience-patterns/   spring-boot/ (matrix)  go-chi/ (matrix)
fastapi/ (matrix)      aws-api-gateway/      terraform-api/
deprecation-policy/    api-lifecycle/
```

As **runtime matrices** (equivalente a `runtime-matrix.yaml` do spark-forge)
são o version guard: `spring-boot/matrix.yaml` (Boot × Java × Jackson ×
Spring Security), `go-chi/matrix.yaml`, `fastapi/matrix.yaml` (FastAPI ×
Pydantic × Starlette × Python), `aws-api-gateway/matrix.yaml` (REST vs HTTP
API — auth, payload, throttling, preço). Toda regra declara `runtime_scope`;
fora de range, skip — e o runtime detectado é declarado antes de qualquer
finding. Divergência de fontes é finding (ex.: versão declarada no pom vs.
detectada no IaC), nunca resolvida escolhendo uma.

## 6. Economia de tokens desde o nascimento

Não é retrofit — nasce na V1:

- `detail_level` (`summary|normal|full`) em **toda** tool MCP; denominador
  medido por `economy report` (bytes por nível, sem concluir por você).
- `call_tool` registra `payload_bytes` por chamada, recusas incluídas;
  ausência de transcript do host → `tokens_unresolved`.
- Índices locais antes de arquivo: símbolos, rotas, schemas, call graph,
  contratos — tokensave/codebase-memory já são a infra; context funnel
  (inventário → candidatos → símbolos → evidências dedup → snapshot mínimo).
- Cascata spec §9: análise determinística → cache por hash → retrieval
  mínimo → especialista → raciocínio → debate só com gatilho.
- O próprio core é a maior economia: `analyze *` + `judge` respondem em
  zero-token o que um agente gastaria milhares lendo código.

## 7. SDD próprio

Já planejado em `docs/plans/2026-09-21-api-forge-sdd-policy-sandbox-evidence.md`:
fases canônicas, perfis `quick|standard|critical|migration`, frontmatter
YAML com cascata `upstream.sha256` + `upstream_stale`, recusas nomeadas com
`field`/`unlock`, recibo provando correspondência (nunca autoria), sandbox
before/after com `sandbox_id` de diff+manifesto. Fases `not_required`
registradas com regra e justificativa. CLI: grupo `sdd` (`init`, `check`,
`status`, `stamp`).

## 8. Estratégia de adapters de linguagem

Decisão pendente de ADR: **tree-sitter vs parser nativo por subprocesso**.

| Opção | Prós | Contras |
|---|---|---|
| tree-sitter (python binding, grammars java/go) | um mecanismo, três+ linguagens; sem toolchain do projeto; incremental; offline | dependência nativa (wheel); AST menos tipado que o nativo |
| subprocesso nativo (`go/parser` via binário, `javac -proc` / spoon) | AST fiel da linguagem | exige toolchain instalada; dois executáveis para distribuir; acoplamento de versão |

Recomendação: tree-sitter — mesma razão do `ast.parse` no FastAPI:
extração sem executar código nem exigir toolchain do alvo. Contrato comum do
adapter: emite o `CodeInventory` (generalizar `FastApiInventory`) com facts
`code.route` (method, path, handler, framework, source) + diagnostics
`unresolved` nomeados + hash de todo arquivo varrido. Java: anotações
`@RestController`/`@GetMapping`/`@RequestMapping`, `RouterFunction`, Jax-RS
`@Path`/`@GET`. Go: `chi.Mux`, `r.Get(...)`, `http.HandleFunc`, Gin/Echo como
extensão. Rotas dinâmicas → `unresolved`, nunca inferência.

## 9. Laboratórios de eval

`tests/labs/`: três repositórios-equivalente `orders-fastapi`,
`orders-spring`, `orders-go` — mesma API, mesmos endpoints — cada um com
variante correta e variantes com falhas deliberadas (rota faltante, sem auth,
sem paginação, breaking change disfarçado, sem teste de contrato). Evals:
golden cases por área, adversarial, holdout, economia e regressão — o critério
§14 do spec vira corpus executável.

## 10. Sequência de entrega

Cada linha vira um plano datado em `docs/plans/` (mesmo formato do MVP):
briefs por task, RED→GREEN registrado, ledger SDD, commit atômico.

| # | Plano | Estado |
|---|---|---|
| 1 | MVP vertical slice (FastAPI + OpenAPI + diff + judge + case + CLI) | **entregue** |
| 2 | SDD profiles, policy engine, sandbox/worktree, release evidence | **entregue** |
| 3 | Fundação do catálogo: `routing.yaml`, `gates.yaml`, áreas de regras esqueléticas, `next-step`, `detail_level` no core — **+ adapter Spring Boot + lab `orders-spring`** (Java antes de Go, decisão do operador) | **entregue** |
| 4 | Adapter Go/Chi + lab `orders-go` (ADR tree-sitter já decidido no plano 3) | **entregue** |
| 5 | ~~Adapter Spring Boot + lab `orders-spring`~~ → absorvido pelo plano 3 | |
| 6 | AWS: `collect/model api-gateway` (slice 1) + `collect/model lambda`, `model terraform`, `model sam` (slice 2) | **entregue** |
| 6b | Builder Java: `build endpoint` (sandbox-first, worktree-gated, receipt) | **entregue** |
| 6c | Conhecimento do catálogo: 37 regras em 6 áreas + `rules list/lookup` | **entregue** |
| 7 | Testes: `model pact/schemathesis/k6/coverage` report readers | **entregue** |
| 8 | Segurança: `model zap/semgrep/trivy/gitleaks` report readers (AF-SEC judge rules ficam para evolução) | **entregue** |
| 9 | Camada agêntica: coordinators/executors em `agents/` + `AGENT_PROTOCOL.md` + `playbook` floor + economy ledger | **entregue** |
| 9b | MCP server (`apiforge-mcp`, extra `[mcp]`) + `context funnel` medido | **entregue** |
| 10 | Release evidence bundle: `report build/sign/verify` — divergência nomeada por parte | **entregue** |
| 11 | AsyncAPI (`model asyncapi`, 2.x/3.x) | **entregue** |
| 12 | GraphQL (`model graphql`, graphql-core confinado) + gRPC (`model proto`, mini-parser) | **entregue** |
| 13 | Performance: `model jfr/pprof/pyroscope` → `perf.*` facts | **entregue** |
| 14 | Modernização assistida: `plan strangler` (cut plan por rota) | **entregue** |
| 15 | Regras executáveis `check:` no catálogo + `judge --facts` | **entregue** |
| 16 | Debate protocol: `debate open/submit/close` com quorum + referee | **entregue** |

## 11. Decisões abertas

1. ~~**tree-sitter** para Java/Go vs parser nativo por subprocesso~~ —
   **decidido**: tree-sitter (ADR-006); adapters Spring e Go já em produção.
2. Monorepo único vs pacotes por adapter (`apiforge-spring`,
   `apiforge-go`) — tende a monorepo enquanto o core for estável.
3. Empacotamento do MCP server: mesmo wheel vs extra `[mcp]`.
4. Licenciamento das fontes normativas nos knowledge packs (citadas, não
   copiadas — `source_authority.yaml` já prevê).
5. Escopo do protocolo de debate: quorum, árbitro, e quando o resultado é
   `unresolved` em vez de decisão.
