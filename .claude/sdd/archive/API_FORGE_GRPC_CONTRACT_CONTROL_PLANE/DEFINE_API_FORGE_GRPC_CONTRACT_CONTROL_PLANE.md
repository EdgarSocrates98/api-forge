# DEFINE: API Forge gRPC Contract Control Plane

> Control plane agentico para analisar, evoluir, gerar, testar e operar APIs gRPC com contrato `.proto` verificável.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_GRPC_CONTRACT_CONTROL_PLANE |
| **Date** | 2026-09-22 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 15/15 |

---

## Problem Statement

Desenvolvedores precisam evoluir APIs gRPC sem quebrar clientes, servidores, mensagens, generated code ou gateways, mas o API Forge possui apenas extração protobuf parcial. Falta um control plane verificável para compatibilidade, codegen, streaming, gateways, testes, performance e operação.

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Engenheiro de software | Cria e evolui serviços gRPC | Não consegue medir o impacto de mudanças em `.proto` e generated code. |
| Engenheiro de plataforma | Padroniza runtimes e gateways | Precisa manter codegen, Envoy, gRPC-Gateway, segurança e observabilidade coerentes. |
| Engenheiro de dados/API | Integra serviços, bancos e streaming | Precisa validar contratos, throughput, backpressure e integrações AWS/Kafka. |
| Agent/subagent | Executa tarefas agenticas | Precisa de IR, TaskSpec, capabilities, limites, evidências e verifier. |
| Revisor técnico | Aprova mudanças de alto risco | Precisa distinguir compatível, review, breaking e inconclusive com provas. |

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | Criar IR gRPC versionado e determinístico a partir de `.proto` e descriptor sets, com proveniência e hashes. |
| **MUST** | Detectar unary, client-streaming, server-streaming e bidirectional streaming, além de messages, fields, enums, oneof, maps, repeated, optional, presence, imports e options. |
| **MUST** | Classificar mudanças como `compatible`, `review`, `breaking` ou `inconclusive`, com evidências para field numbers, tipos, enums, RPCs, streaming e annotations. |
| **MUST** | Gerar artefatos reais e reproduzíveis para Python, Go e Java quando as toolchains estiverem disponíveis; declarar capability ausente quando não estiverem. |
| **MUST** | Projetar gRPC-Gateway, Envoy, gRPC-Web e OpenAPI por capability matrix, sem acoplar o core a um gateway. |
| **MUST** | Integrar TaskSpec, Runtime Agentico, debate por risco/divergência, revisor, verifier, holdout/mutation e brief `DONE/REVIEW/BLOCKED`. |
| **SHOULD** | Validar deadlines, status codes, metadata, retry, health, reflection, interceptors, keepalive, graceful shutdown e limites de mensagens. |
| **SHOULD** | Cobrir contrato, integração, streaming, property/fuzz, mutation, holdout e gateway REST/JSON ↔ gRPC. |
| **SHOULD** | Integrar OTel ao Observability Control Plane para traces, métricas RPC, status, streaming e correlação. |
| **COULD** | Adicionar C#, Node.js, Rust e Kotlin após estabilizar IR e adapters iniciais. |
| **COULD** | Gerar recomendações AWS/EKS/ECS/Lambda/EC2/MSK e service mesh a partir do workload gRPC. |

## Success Criteria

- [x] 100% das fixtures `.proto` válidas geram IR, hash e proveniência determinísticos em duas execuções.
- [x] 100% dos quatro padrões de RPC são detectados corretamente.
- [x] Casos declarativos cobrem mensagens, enums, repeated, optional, imports, RPCs, options e annotations.
- [x] Casos de field number reutilizado, remoção incompatível, tipo incompatível e streaming alterado são classificados corretamente.
- [x] Codegen Python, Go e Java é byte-reprodutível no fake adapter e `unsupported` explícito quando a toolchain está ausente.
- [x] Casos cobrem gRPC-Gateway, Envoy, gRPC-Web, OpenAPI, annotations HTTP, unary e streaming.
- [x] Streaming cobre os quatro modos, deadline, limite de mensagem e status; harness externo permanece capability-gated.
- [x] Nenhuma mutação externa ocorre sem policy, capability, diff, approval, credential broker e rollback.
- [x] O vertical slice local/CI retorna corretamente `DONE`, `REVIEW`, `INCONCLUSIVE` ou `BLOCKED` sem credenciais.
- [x] Performance diferencia RPS, TPS, concorrência, latência e saturação do gerador.
- [x] Release gate, Ruff, mypy e pytest passam sem regressão na suíte existente.

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Parse protobuf | Diretório contém `.proto` válido | Adapter é executado | Facts e IR contêm package, imports, services, messages e hashes. |
| AT-002 | Invalid protobuf | Bloco não está fechado | Parser é executado | `AF-PROTO-PARSE` é emitido; erro não é escondido. |
| AT-003 | Unary | RPC não usa `stream` | IR é construído | RPC é marcado unary. |
| AT-004 | Client streaming | Request usa `stream` | IR é construído | `client_streaming=true`. |
| AT-005 | Server streaming | Response usa `stream` | IR é construído | `server_streaming=true`. |
| AT-006 | Bidi streaming | Request e response usam `stream` | IR é construído | Ambos os flags são verdadeiros. |
| AT-007 | Descriptor set | Descriptor contém serviços/options | Loader é executado | IR e provenance são preservados. |
| AT-008 | Compatible evolution | Campo opcional novo usa número livre | Diff é executado | Resultado `compatible` com evidência. |
| AT-009 | Removed field | Campo removido sem reserva | Diff é executado | Resultado `breaking` ou `review` com field number. |
| AT-010 | Reused number | Número antigo é reutilizado | Diff é executado | Resultado `breaking` com colisão identificada. |
| AT-011 | Type change | Tipo wire-incompatível muda | Diff é executado | Resultado `breaking` com tipos anterior/novo. |
| AT-012 | Enum evolution | Enum recebe e remove valores | Diff é executado | Adição e remoção recebem classificações distintas. |
| AT-013 | Codegen Python | Plugin está disponível | Codegen roda duas vezes | Artefatos e manifests são idênticos. |
| AT-014 | Codegen unavailable | Plugin Go/Java ausente | Codegen é solicitado | `unsupported`/`BLOCKED` explícito; sem falso sucesso. |
| AT-015 | HTTP annotation | RPC possui `google.api.http` | Projection é solicitada | Método, path e binding são preservados. |
| AT-016 | Gateway capability | Envoy/gRPC-Gateway ausente | Projection é solicitada | Capability ausente é nomeada; core continua verificável. |
| AT-017 | Streaming gateway | Server stream possui binding HTTP | Projection é gerada | Semântica e representação JSON são documentadas/testadas. |
| AT-018 | Deadline/status | Fixture excede deadline | Runtime policy é avaliada | Usa `DEADLINE_EXCEEDED`; não sugere retry indiscriminado. |
| AT-019 | Retry safety | RPC mutating não idempotente | Retry policy é avaliada | Retry é recusado ou exige evidence. |
| AT-020 | Health/reflection | Serviço declara health/reflection | Analyzer roda | Gaps/capabilities são relatados sem inventar runtime ativo. |
| AT-021 | OTel | Fixture contém spans/métricas RPC | Adapter roda | Service, method, status, streaming e correlation são preservados. |
| AT-022 | Performance | Run declara amostras, duração, TPS e p99 | Verdict roda | RPS/TPS e p99 são separados; falta/saturação vira inconclusive. |
| AT-023 | TaskSpec | Intenção pede evolução `.proto` | Supervisor compila | TaskSpec contém acceptance, rollback, proof, budget e capabilities. |
| AT-024 | High-risk review | Diff é breaking ou gateway mutation | Runtime planeja | Debate/reviewer/verifier é acionado antes da decisão. |
| AT-025 | Mutation safety | Apply não tem approval/broker | Adapter é chamado | Recusa/dry-run; nenhuma mutação externa. |
| AT-026 | Holdout/mutation | Fixture muda após planejamento | Verifier roda holdout | Mudança é detectada; status não é `DONE`. |
| AT-027 | Replay | Mesma fixture/policy/toolchain | Run é reexecutado | IR, diff, manifest, evidence e status são reproduzíveis. |
| AT-028 | CLI/MCP parity | CLI e MCP recebem mesma entrada | Ambos executam | Payloads são semanticamente equivalentes. |

## Out of Scope

- Targets além de Python, Go e Java.
- Testes contra produção, tenants reais ou clusters externos.
- Provisionamento automático de Envoy, gRPC-Gateway, EKS, ECS ou service mesh.
- Auto-merge, auto-deploy ou alteração automática sem aprovação.
- Gateway proprietário fora de Envoy/gRPC-Gateway/gRPC-Web.
- Benchmark distribuído de produção e afirmações sem ambiente certificado.
- Conectores de credenciais dentro do core.

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Núcleo local/CI-safe e offline-first | Fixtures/fake adapters funcionam sem toolchains ou servidores ativos. |
| Technical | `.proto`/descriptor é contrato canônico | IR, diff, codegen e gateway citam provenance e hashes. |
| Technical | Python, Go e Java primeiros targets | Plugins são capabilities, não dependências hard-coded. |
| Technical | Streaming e gateway estão no escopo | Testes cobrem fluxo, cancelamento, backpressure e transcoding. |
| Security | Nenhum segredo no core | Adapters recebem referências de credential broker, não valores brutos. |
| Safety | Mutação exige policy e aprovação | Plan, diff, dry-run, apply, verify e rollback são separados. |
| Quality | Não há amostras reais | Fixtures sintéticas, evals, holdout e mutation são obrigatórios. |
| Repository | Preservar extractor protobuf | Novos recursos mantêm facts legados e adicionam IR sem regressão. |

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/adapters/protobuf`, `src/apiforge/grpc`, `src/apiforge/codegen`, `src/apiforge/gateway`, `src/apiforge/contracts`, `tests/grpc`, `tests/fixtures/grpc` | O extractor existente será expandido, mantendo separação entre IR, policy, projections e adapters. |
| **KB Domains** | `contract-testing`, `observability`, `genai`, `testing`, `pydantic`, `python`, `terraform`, `aws` | Não há KB gRPC dedicado; usar fontes oficiais e registrar gaps para Design. |
| **IaC Impact** | Adapters/projections opcionais; sem mutação no MVP | Envoy, gRPC-Gateway e AWS serão capability checks/manifests. |

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Extractor existente pode evoluir sem quebrar `proto.*` facts | Versionar adapter paralelo e migrar consumidores | [ ] |
| A-002 | Descriptor sets cobrem opções não detectadas pelo parser textual | Integrar parser protobuf completo | [ ] |
| A-003 | Toolchains podem ser instaladas ou simuladas por adapters | Codegen será unsupported em alguns ambientes | [ ] |
| A-004 | Envoy/gRPC-Gateway podem ser projections equivalentes por capability | Criar contratos específicos por gateway | [ ] |
| A-005 | Fixtures sintéticas cobrem riscos relevantes | Adicionar corpus anonimizado antes de certificar performance | [ ] |
| A-006 | Observability Control Plane aceita sinais RPC por adapter | Evoluir contrato OTel com atributos gRPC | [ ] |
| A-007 | Streaming offline pode validar semântica, mas não capacidade de produção | Harness certificado será uma feature posterior | [ ] |

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Risco de breaking changes e divergência está claro. |
| Users | 3 | Software, plataforma, dados/API, agents e revisores identificados. |
| Goals | 3 | MoSCoW e targets estão explícitos. |
| Success | 3 | Critérios numéricos e 28 acceptance tests definidos. |
| Scope | 3 | Inclusões, exclusões, gateways e linguagens definidos. |
| **Total** | **15/15** | Pronto para Design. |

## Open Questions

- Versões certificadas de `protoc`, Buf, plugins e runtimes.
- Proto3 versus editions no primeiro slice.
- Estratégia oficial: protoc plugins, Buf generate, templates ou combinação.
- Subconjunto obrigatório de annotations HTTP.
- Subconjunto de retries, hedging, keepalive e service config.
- Harness local para streaming, flow control, TPS e message size.
- Métricas gRPC específicas padronizadas no Observability Control Plane.

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-22 | define-agent | Requirements captured from approved gRPC brainstorm; clarity 15/15. |

## Next Step

**Archived:** `.claude/sdd/archive/API_FORGE_GRPC_CONTRACT_CONTROL_PLANE/`

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.1 | 2026-09-22 | Shipped and archived. |
