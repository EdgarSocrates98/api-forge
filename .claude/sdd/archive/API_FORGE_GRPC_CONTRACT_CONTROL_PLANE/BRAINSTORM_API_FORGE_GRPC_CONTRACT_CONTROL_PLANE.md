# BRAINSTORM: API Forge gRPC Contract Control Plane

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_GRPC_CONTRACT_CONTROL_PLANE |
| **Date** | 2026-09-22 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Complete (Defined) |

---

## Initial Idea

**Raw Input:** Fazer uma especialização completa em gRPC para o API Forge, cobrindo análise, contrato, geração, evolução, testes, performance, segurança, observabilidade, streaming, gRPC-Web, transcoding e gateways.

**Context Gathered:**

- O API Forge já possui `src/apiforge/adapters/protobuf/extract.py`, um parser offline que identifica arquivos, packages, imports, services, messages, enums e RPCs.
- O extractor já registra `client_streaming` e `server_streaming`, portanto unary, client-streaming, server-streaming e bidirectional streaming têm uma base de proveniência existente.
- O projeto já possui TaskSpec, Runtime Agentico 2.0, verificação independente, graphify, TokenSave, adapters OTel, performance e SDD.
- A feature anterior de Observability Control Plane estabeleceu contratos provider-neutral, capabilities, dry-run, redaction, SLO, receipts e integração segura com Datadog/Dynatrace.
- Não existem amostras reais de `.proto`, generated code, gateways ou relatórios gRPC neste ciclo; serão criadas fixtures sintéticas representativas.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/adapters/protobuf`, novos módulos `src/apiforge/grpc`, `contracts`, `codegen`, `gateway` e `tests/grpc` | Evoluir o extractor existente sem quebrar facts legados e introduzir um IR gRPC versionado. |
| Relevant KB Domains | `contract-testing`, `observability`, `genai`, `testing`, `pydantic`, `python`; não há domínio gRPC dedicado no KB | Usar contratos, evidências, evals, segurança e testes existentes; validar detalhes gRPC em documentação oficial. |
| IaC Patterns | Não há IaC gRPC específico no núcleo; existem adapters AWS/Terraform, Envoy e Kubernetes serão projections | Gateways e ambientes devem permanecer adapters/capabilities, sem acoplar o core a uma infraestrutura. |

**Evidence confidence:** 0.95 para evolução do extractor/IR, baseada no código existente; 0.85 para codegen/gateway, baseada em padrões oficiais e adapters a construir; 0.80 para benchmarks de runtime, pois não há ambientes reais nem amostras de produção.

**Official references consulted:**

- [gRPC core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/)
- [gRPC deadlines](https://grpc.io/docs/guides/deadlines/)
- [gRPC health checking](https://grpc.io/docs/guides/health-checking/)
- [gRPC guides](https://grpc.io/docs/guides/)
- [Protocol Buffers proto3 guide](https://protobuf.dev/programming-guides/proto3/)
- [Protocol Buffers version support](https://protobuf.dev/support/version-support/)
- [Envoy gRPC-JSON transcoder](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/grpc_json_transcoder_filter.html)
- [gRPC-Gateway FAQ](https://grpc-ecosystem.github.io/grpc-gateway/docs/faq/)

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Qual é o objetivo principal? | **Plataforma completa**: analisar APIs gRPC, projetar contratos, gerar código, evoluir, testar e operar. | A feature será um control plane, não apenas um parser ou benchmark. |
| 2 | Quais linguagens entram primeiro? | **Python, Go e Java**. | O IR será language-neutral, com targets explícitos para as três linguagens. |
| 3 | Quais capacidades gRPC são obrigatórias? | **Os quatro padrões de RPC/streaming e gateway completo**. | O modelo deverá distinguir unary, client-streaming, server-streaming e bidi; também suportará gRPC-Web, REST/JSON transcoding e gateway. |
| 4 | Como medir sucesso? | **Todos os critérios**: funcionalidade, segurança/compatibilidade, performance operacional e vertical slice verificável. | Acceptance tests precisam cobrir contrato, codegen, gateway, testes e performance declarada. |
| 5 | Existem amostras reais? | **Não; criar fixtures sintéticas representativas**. | Fixtures serão fonte de few-shot, testes, evals e casos de compatibilidade. |
| 6 | Qual abordagem foi escolhida? | **Approach A — gRPC Contract Control Plane**. | `.proto`/descriptor → IR → compatibilidade → codegen/gateway → testes/evidências. |
| 7 | Como selecionar gateway? | **Capability matrix**, com gRPC-Gateway e Envoy equivalentes/opcionais conforme o ambiente. | Nenhum vendor/runtime será obrigatório no core; resultados não suportados ficam explícitos. |

**Minimum Questions:** 7

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | N/A — a criar em `tests/fixtures/grpc/` | 0 reais | Fixtures `.proto` com unary, quatro stream modes, options, imports, enums, oneof, maps, presence e annotations HTTP. |
| Output examples | N/A — a gerar durante o build | 0 reais | Expected IR, compatibility findings, generated manifests, gateway configs e evidence receipts. |
| Ground truth | N/A — a definir em casos declarativos | 0 reais | Matriz manual de mudanças compatíveis, breaking, review e inconclusive. |
| Related code | `src/apiforge/adapters/protobuf/extract.py` e `tests/adapters/protobuf/test_extract.py` | 1 adapter + testes existentes | Parser atual detecta RPCs e flags de streaming; será preservado e expandido. |

**How samples will be used:**

- Few-shot estrutural para agents reconhecerem padrões protobuf/gRPC sem inventar semântica.
- Validação de schema do gRPC IR e dos manifests de codegen.
- Testes determinísticos de compatibilidade, streaming, gateway e generated artifacts.
- Evals para diferenciar breaking change, recommendation, unresolved e ausência de capability.
- Holdout/mutation checks para garantir que o verifier detecta alteração de field number, tipo, streaming ou annotation.

---

## Approaches Explored

### Approach A: gRPC Contract Control Plane ⭐ Recommended

**Description:** Criar um IR gRPC canônico derivado de `.proto` e descriptors, com análise de compatibilidade, codegen real para Python/Go/Java, projections para gRPC-Gateway/Envoy/gRPC-Web/OpenAPI, testes, performance, observabilidade e execução governed por TaskSpec.

**Pros:**

- Reutiliza diretamente o extractor protobuf existente.
- Centraliza compatibilidade e evolução em um contrato único.
- Permite múltiplos runtimes e gateways sem acoplar o núcleo.
- Produz evidências reproduzíveis antes de qualquer execução externa.
- Suporta crescimento futuro para AWS, Kubernetes, service mesh e bancos downstream.

**Cons:**

- Maior superfície inicial: IR, codegen, gateway, testes e runtime policies.
- Codegen depende de toolchains opcionais e versões compatíveis.
- Streaming e gateway exigem fixtures e verificações mais complexas.

**Why Recommended:** O código existente já contém extração protobuf/streaming e o projeto já possui contracts, TaskSpec, verifier, TokenSave, graphify e observability control plane. A abordagem preserva esses padrões. A especificação oficial também define `.proto`/descriptors como fonte estrutural, quatro modalidades de streaming e mecanismos próprios de deadlines, health e status.

### Approach B: Runtime Specialists First

**Description:** Construir primeiro adapters profundos para `grpcio`, `grpc-go` e `grpc-java`, com codegen e testes por linguagem; unificar o modelo depois.

**Pros:**

- Profundidade maior em cada runtime.
- Mais cedo surgem exemplos executáveis.

**Cons:**

- Regras de compatibilidade podem ser duplicadas por linguagem.
- Maior risco de divergência entre targets.
- O contrato canônico e o diff ficariam atrasados.

### Approach C: Gateway/Mesh First

**Description:** Começar por Envoy, gRPC-Gateway, gRPC-Web, REST/JSON transcoding e integração de perímetro.

**Pros:**

- Valor rápido para consumidores REST e browser.
- Aproveita descriptors e annotations HTTP.

**Cons:**

- Pode esconder problemas no contrato e codegen.
- Introduz parsing JSON/binary, regeneração e diferenças operacionais cedo.
- Não resolve sozinho compatibilidade de messages, enums, fields e streaming.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A — gRPC Contract Control Plane |
| **User Confirmation** | 2026-09-22 |
| **Reasoning** | O usuário confirmou uma plataforma completa, Python/Go/Java, quatro modos de streaming, codegen real e gRPC-Gateway/Envoy/gRPC-Web via capability matrix. |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | `.proto` + descriptor set alimentam um IR canônico | O contrato é a fonte mais estável para diff, codegen e gateway | Runtime-first sem IR comum |
| 2 | Codegen real entra no primeiro ciclo | Usuário explicitamente priorizou geração Python, Go e Java | Adiar codegen para uma fase posterior |
| 3 | gRPC-Gateway, Envoy e gRPC-Web entram como projections | Usuário quer gateway completo, mas ambientes variam | Escolher um gateway obrigatório |
| 4 | Capability matrix decide o que pode ser executado | `protoc`, Buf, plugins e Envoy podem não estar instalados | Assumir toolchain disponível |
| 5 | Streaming completo entra no contrato, com fixtures sintéticas | Unary sozinho não representa a especialização desejada | Limitar MVP a unary |
| 6 | Local/CI seguro antes de tenants reais | Mantém o padrão do Runtime Agentico e Observability Control Plane | Testar contra serviços externos durante o build |
| 7 | Compatibilidade é evidência, não inferência | Mudanças de números, tipos, enums, presence e options têm riscos diferentes | Classificar toda mudança como breaking automaticamente |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| C#, Node.js, Rust e Kotlin no primeiro target | Não fazem parte da prioridade declarada Python/Go/Java | Yes |
| Provisionamento automático de clusters e service mesh | Amplia risco e exige mutação externa | Yes |
| Teste contra tenants gRPC reais | Não há ambientes/amostras reais e violaria o escopo local/CI seguro | Yes |
| Auto-merge de mudanças de `.proto` | Decisão de contrato exige evidência e aprovação | Yes |
| Benchmark distribuído em produção | Não há baseline ou autorização operacional | Yes |
| Implementação de um gateway proprietário | Envoy e gRPC-Gateway já cobrem projections maduras | No, salvo lacuna comprovada |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Architecture concept | ✅ | Confirmado com “Ok” | Não; arquitetura mantida. |
| Component breakdown | ✅ | Confirmado com “Ok” | Não; components mantidos. |
| Scope/YAGNI | ✅ | Codegen e gateway foram promovidos para o primeiro ciclo | Sim; escopo expandido de acordo com a decisão do usuário. |
| Approach comparison | ✅ | Approach A escolhida | Sim; runtime/gateway ficaram como projections do control plane. |

**Minimum Validations:** 4

---

## Suggested Requirements for /define

Based on this brainstorm session, the following should be captured in the DEFINE phase:

### Problem Statement (Draft)

O API Forge precisa analisar, projetar, gerar, testar, evoluir e operar APIs gRPC de forma agentica e verificável, mantendo `.proto`/descriptors como contrato canônico e suportando Python, Go, Java, streaming, gateways e REST/JSON sem depender de ambientes externos no núcleo.

### Target Users (Draft)

| User | Pain Point |
|------|------------|
| Engenheiro de software | Evoluir contratos gRPC sem quebrar clientes, servidores ou generated code. |
| Engenheiro de plataforma | Padronizar codegen, gateway, observabilidade, segurança e deployment. |
| Engenheiro de dados/API | Integrar APIs gRPC com pipelines, bancos, Kafka/MSK e serviços AWS. |
| Agent/subagent | Receber um IR, TaskSpec, capabilities, evidências e limites verificáveis. |
| Revisor técnico | Avaliar breaking changes, performance, segurança e provas antes da decisão. |

### Success Criteria (Draft)

- [ ] Um `.proto` fixture gera IR versionado com proveniência e hash determinísticos.
- [ ] Unary e os quatro modos de streaming são identificados corretamente.
- [ ] Diffs classificam mudanças como compatible, review, breaking ou inconclusive com evidências.
- [ ] Codegen para Python, Go e Java é reprodutível e declara toolchain/capabilities.
- [ ] gRPC-Gateway, Envoy, gRPC-Web e OpenAPI são gerados ou explicitamente marcados como unsupported.
- [ ] Testes cobrem contrato, generated artifacts, integração, streaming, property/fuzz, mutation e holdout.
- [ ] O sistema valida deadlines, status codes, metadata, retry, health, reflection, interceptors e graceful shutdown.
- [ ] Performance mede latência, TPS/RPS, concorrência, message size, flow control, stress e soak sem inventar resultados.
- [ ] OTel produz sinais RPC correlacionados com o Observability Control Plane existente.
- [ ] TaskSpec, debate por risco/divergência, revisor, verifier, receipts e brief `DONE/REVIEW/BLOCKED` são usados nos gates críticos.
- [ ] Nenhuma mutação externa ou uso de credencial ocorre sem adapter, policy, aprovação, diff e rollback.

### Constraints Identified

- O núcleo deve continuar local/CI-safe e offline-first.
- Não há amostras reais; fixtures sintéticas são obrigatórias.
- Python, Go e Java são os primeiros targets.
- `protoc`, Buf, plugins de codegen, Envoy e gRPC-Gateway são opcionais e capability-aware.
- O parser atual não substitui um parser completo de descriptors; gaps devem ser nomeados.
- Compatibilidade protobuf precisa respeitar field numbers, reserved fields, enum behavior, presence e evolução de editions.
- O resultado nunca deve afirmar TPS, latência, disponibilidade ou compatibilidade sem evidência suficiente.

### Out of Scope (Confirmed)

- Targets de linguagem além de Python, Go e Java neste primeiro ciclo.
- Testes contra produção, tenants reais ou clusters externos.
- Provisionamento automático de infraestrutura.
- Auto-merge ou auto-deploy de alterações de contrato.
- Gateway proprietário fora das projections Envoy/gRPC-Gateway/gRPC-Web.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 7 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 6 |
| Validations Completed | 4 |
| Duration | 2026-09-22, sessão interativa |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_API_FORGE_GRPC_CONTRACT_CONTROL_PLANE.md`
