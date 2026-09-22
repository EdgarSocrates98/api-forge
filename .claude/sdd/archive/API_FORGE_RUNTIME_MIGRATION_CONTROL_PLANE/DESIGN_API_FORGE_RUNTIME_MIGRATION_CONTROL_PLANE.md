# DESIGN: API Forge Runtime Migration Control Plane

> Arquitetura técnica do control plane agentico para migrações verificáveis de runtime.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_RUNTIME_MIGRATION_CONTROL_PLANE |
| **Date** | 2026-09-22 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_RUNTIME_MIGRATION_CONTROL_PLANE.md](./DEFINE_API_FORGE_RUNTIME_MIGRATION_CONTROL_PLANE.md) |
| **Status** | ✅ Shipped |

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────────┐
│                 RUNTIME MIGRATION CONTROL PLANE                      │
├──────────────────────────────────────────────────────────────────────┤
│  CLI / MCP / Python API                                               │
│          │                                                            │
│          ▼                                                            │
│  MigrationSpec Validator ──► Discovery Coordinator                    │
│          │                         │                                  │
│          │                         ├─ Java Adapter                     │
│          │                         ├─ Python Adapter                   │
│          │                         ├─ Go Adapter                       │
│          │                         ├─ Dependency/Toolchain Adapters    │
│          │                         └─ Contract/Data/Cloud Extractors   │
│          ▼                                                            │
│  Compatibility Aggregator ──► Risk + Evidence IR                      │
│          │                         │                                  │
│          ▼                         ▼                                  │
│  Migration Planner ──► TaskSpec/TaskPlan ──► Runtime Agentic 2.0      │
│          │                                   │                         │
│          │                                   ├─ bounded fan-out         │
│          │                                   ├─ debate gates            │
│          │                                   ├─ sandbox/worktree         │
│          │                                   └─ approval policy          │
│          ▼                                                            │
│  Patch/Tool Executor ──► Build/Test/Perf Evidence Store               │
│          │                         │                                  │
│          ▼                         ▼                                  │
│  Independent Verifier ◄──── Receipt + Diff + Contract/Perf Results    │
│          │                                                            │
│          ▼                                                            │
│  OutcomeBrief: DONE | REVIEW | BLOCKED                                │
└──────────────────────────────────────────────────────────────────────┘
```

O núcleo é uma biblioteca local/CI. O CLI e o MCP são superfícies finas; não contêm regras de migração. O supervisor existente continua sendo o único responsável por política, orçamento, fan-out e gates. O novo domínio apenas compila uma migração em contratos que o runtime atual já entende.

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `MigrationSpec` | Entrada normalizada e validada da intenção | Pydantic, `VersionedContract` |
| Runtime registry/matrix | Resolve versões, saltos, suporte, regras e toolchains | YAML + adapters Python |
| Discovery coordinator | Orquestra descoberta estática e adapta fatos existentes | Python, adapters read-only |
| Language adapters | Java, Python e Go: manifests, breaking changes e comandos seguros | Python, subprocess bounded |
| Impact aggregator | Consolida código, dependências, contratos, dados, cloud, observabilidade e risco | IR imutável + evidence refs |
| Migration planner | Converte achados em tarefas fechadas e plano ordenado | `TaskSpec`, `TaskPlan` |
| Agentic bridge | Executa o plano dentro de políticas existentes | Runtime Agentic 2.0 |
| Sandbox/tool runner | Aplica patches e executa comandos permitidos | sandbox/worktree existente |
| Evidence/receipt adapter | Registra hashes, comandos, diffs, resultados e gaps | evidence store existente |
| Independent verifier | Recalcula provas, testa holdout/mutation e bloqueia falso `DONE` | verifier + `OutcomeBrief` |
| Report/CLI/MCP surface | Exibe relatório reproduzível e estado final | Typer, MCP, JSON/YAML |

## Key Decisions

### Decision 1: Control plane único com adapters versionados

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** Cada par de versões possui diferenças próprias, mas o ciclo de descoberta, planejamento, execução, evidência e verificação é comum. Um agente por par de versões duplicaria políticas e dificultaria a evolução.

**Choice:** Criar um `MigrationEngine` agnóstico de linguagem que resolve `RuntimeAdapter` por `(ecosystem, source, target)` e combina regras declarativas com analisadores opcionais.

**Rationale:** Mantém `TaskSpec`, gates, evidências e resultado final uniformes. Novas versões entram em metadados/adapters sem alterar o supervisor nem o contrato de saída.

**Alternatives Rejected:**
1. Packs independentes por par de versão — fragmentam a governança e multiplicam lógica.
2. Toolchain-first — falha quando o runtime não está instalado e não permite análise estática útil.

**Consequences:**
- O núcleo precisa representar “não verificado” explicitamente.
- O build inicial deve separar regras declarativas de comandos executáveis.
- Adapters têm que ser determinísticos e read-only por padrão.

### Decision 2: `MigrationSpec` e `MigrationReport` como contratos versionados

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** A intenção precisa sobreviver a handoffs, replay, CI e execução por providers diferentes.

**Choice:** Adicionar contratos Pydantic versionados para entrada, matriz/resolução, finding, plano e relatório. Referências a arquivos/evidências serão hashes ou IDs, nunca conteúdo implícito.

**Rationale:** Alinha com `contracts/registry.py`, congela payloads e torna o resultado auditável e testável sem depender do texto do modelo.

**Alternatives Rejected:**
1. Dicionários livres — permitem campos ausentes, status ambíguo e falso positivo.
2. Markdown como estado interno — é adequado para relatório humano, não para transições e validações.

**Consequences:**
- Evolução exige versionamento compatível e testes de conformance.
- Relatórios humanos serão derivados dos contratos.

### Decision 3: Evidência obrigatória e `DONE` conservador

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** Build/testes indisponíveis, contratos breaking e toolchains ausentes são comuns em migrações.

**Choice:** O verificador calcula o status a partir de provas, gaps, risco e mutation/holdout. `DONE` só é permitido com evidências mínimas, gaps críticos vazios e aceitação distinta do executor.

**Rationale:** Reutiliza `OutcomeBrief.done_requires_clean`, receipts e `AcceptanceRecord`, impedindo que o modelo transforme recomendação em autorização.

**Alternatives Rejected:**
1. Confiar no texto do agente — não é verificável.
2. Sempre bloquear quando qualquer ferramenta faltar — reduz utilidade; `REVIEW` representa limitação conhecida sem mentir.

**Consequences:**
- Cada adapter precisa declarar capabilities, provas produzidas e blind spots.
- Evals devem conter casos de falso `DONE` e toolchain ausente.

### Decision 4: Paralelismo por DAG, não por número fixo de agentes

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** Migrações pequenas não precisam de uma sala completa; migrações de alto risco precisam de especialistas concorrentes.

**Choice:** O planner emite tarefas com dependências e o scheduler existente calcula o fan-out permitido pela `AgenticPolicy`, disponibilidade e orçamento. Debate só é uma tarefa/gate derivado de risco ou divergência.

**Rationale:** Preserva economia de tokens e permite paralelismo amplo sem trabalho ilimitado ou execução conflitante.

**Alternatives Rejected:**
1. Sempre executar todos os agentes — caro e gera ruído.
2. Número fixo de workers — não acompanha complexidade real.

**Consequences:**
- O plano deve explicitar dependências e tarefas idempotentes.
- Métricas de custo, duração e cobertura precisam ser persistidas.

### Decision 5: Integrações externas somente read-only no MVP

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-22 |

**Context:** A análise deve cobrir AWS, bancos e observabilidade sem risco de mutação nem credenciais obrigatórias.

**Choice:** Adapters aceitam manifests, dumps, configurações e contratos locais; SDK/CLI externo, se usado, passa por allowlist e política `external_mutation=False`.

**Rationale:** Permite desenvolver sem ambientes reais e torna fixtures reproduzíveis. Qualquer ausência vira gap nomeado.

**Alternatives Rejected:**
1. Conectar diretamente em produção — risco incompatível com o MVP.
2. Ignorar plataforma/dados — produz uma migração incompleta para APIs reais.

**Consequences:** Não haverá prova de estado vivo; o relatório deve distinguir fato estático, evidência fornecida e blind spot.

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/migration/__init__.py` | Create | Exportar API pública do domínio | `@api-modernization-specialist` | 2–5 |
| 2 | `src/apiforge/migration/contracts.py` | Create | `MigrationSpec`, findings, plan/report e capabilities | `@api-modernization-specialist` | None |
| 3 | `src/apiforge/migration/matrix.py` | Create | Resolver ecossistema, origem/alvo e regras de salto | `@api-modernization-specialist` | 2, 6 |
| 4 | `src/apiforge/migration/adapters/base.py` | Create | Protocolo comum de adapter, comandos e evidências | `@api-agentic-orchestrator` | 2 |
| 5 | `src/apiforge/migration/adapters/java.py` | Create | Java 11/17/21/25, Maven/Gradle e checks JDK | `@api-modernization-specialist` | 4, 6 |
| 6 | `src/apiforge/migration/adapters/python.py` | Create | Python 2→3 e 3.8–3.14, packaging e checks | `@api-modernization-specialist` | 4, 6 |
| 7 | `src/apiforge/migration/adapters/go.py` | Create | Go 1.18–1.27, modules, race/test/fuzz checks | `@api-modernization-specialist` | 4, 6 |
| 8 | `src/apiforge/migration/discovery.py` | Create | Descoberta estática de manifests, contratos e integrações | `@api-architecture-reviewer` | 3–7, existing extractors |
| 9 | `src/apiforge/migration/planner.py` | Create | Compilar achados em `TaskSpec`/`TaskPlan` | `@api-planner` | 2, 8, existing taskspec |
| 10 | `src/apiforge/migration/verifier.py` | Create | Regras de status, gaps, holdout e mutation | `@api-verification-engineer` | 2, 9, evidence |
| 11 | `src/apiforge/migration/report.py` | Create | Brief JSON/Markdown reproduzível | `@api-dx-docs-reviewer` | 2, 10 |
| 12 | `src/apiforge/contracts/registry.py` | Modify | Registrar contratos de migração versionados | `@api-task-spec-reviewer` | 2 |
| 13 | `src/apiforge/cli.py` | Modify | Comandos `migration analyze/plan/verify` read-only | `@api-agentic-orchestrator` | 8–11 |
| 14 | `src/apiforge/mcp/tools.py` | Modify | Tools MCP para analisar/planejar/verificar migração | `@api-agentic-orchestrator` | 8–11 |
| 15 | `knowledge/runtime-migration/index.md` | Create | Índice e resolução das regras | `@api-modernization-specialist` | 5–7 |
| 16 | `knowledge/runtime-migration/matrix.yaml` | Create | Versões Java/Python/Go e metadados de suporte | `@api-modernization-specialist` | 3, 15 |
| 17 | `knowledge/runtime-migration/evals.yaml` | Create | Casos, rubricas e thresholds do domínio | `@api-test-strategist` | 15, 16 |
| 18 | `agents/api-runtime-migration-planner.md` | Create | Especialização de planejamento de migração | `@api-modernization-specialist` | 9 |
| 19 | `agents/api-runtime-migration-verifier.md` | Create | Especialização de verificação independente | `@api-verification-engineer` | 10 |
| 20 | `tests/migration/test_contracts.py` | Create | Conformance e invariantes dos contratos | `@api-task-spec-reviewer` | 2, 12 |
| 21 | `tests/migration/test_matrix.py` | Create | Resolução de versões, saltos e unsupported | `@api-modernization-specialist` | 3, 16 |
| 22 | `tests/migration/test_adapters.py` | Create | Discovery e comandos seguros por linguagem | `@api-modernization-specialist` | 4–8 |
| 23 | `tests/migration/test_planner_verifier.py` | Create | TaskSpec, gates, status e independência | `@api-verification-engineer` | 9, 10 |
| 24 | `tests/migration/test_vertical_slice.py` | Create | Fluxo completo com fixture e receipt | `@api-agentic-orchestrator` | 8–14, 20–23 |
| 25 | `tests/fixtures/migrations/java/spring-java11-to-21/` | Create | Fixture Java representativa | `@api-modernization-specialist` | 21–24 |
| 26 | `tests/fixtures/migrations/python/python2-to-3/` | Create | Fixture Python legada | `@api-modernization-specialist` | 21–24 |
| 27 | `tests/fixtures/migrations/go/go121-to-124/` | Create | Fixture Go concorrente | `@api-modernization-specialist` | 21–24 |
| 28 | `tests/fixtures/migrations/platform-data/` | Create | Fixture Terraform/container/dados read-only | `@api-architecture-reviewer` | 8, 24 |

**Total Files:** 28 entries (25 novos arquivos/diretórios e 3 modificações/integrações de código existentes, podendo ser consolidados no Build sem alterar o contrato).

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| `@api-modernization-specialist` | 1, 3, 5–7, 15–18, 21–22, 25–27 | É o especialista de origem→destino, versão, framework e plano de migração. |
| `@api-agentic-orchestrator` | 4, 13–14, 24 | Conhece supervisor, policies, fan-out, handoffs e superfícies MCP/CLI. |
| `@api-architecture-reviewer` | 8, 28 | Revisa arquitetura, Terraform, cloud e limites de evidência offline. |
| `@api-planner` | 9 | Especialista no planejamento de intenção em tarefas fechadas. |
| `@api-verification-engineer` | 10, 19, 23 | Recalcula receipts, provas, gaps e resultado independente. |
| `@api-task-spec-reviewer` | 12, 20 | Valida risco, rollback, paths, provas e selagem. |
| `@api-dx-docs-reviewer` | 11 | Garante que relatório e comandos sejam reproduzíveis e claros. |
| `@api-test-strategist` | 17 | Define evals, cobertura de risco e thresholds. |

**Agent Discovery:**
- Scanned: `agents/**/*.md` do repositório.
- Matched by: especialização declarada, `rule_areas`, executors, propósito do arquivo e KB domains.
- Os executors existentes `af-inventory`, `af-extractor`, `af-judge`, `af-verifier` e `af-synthesizer` são reutilizados; os novos agentes não criam um segundo runtime.

## Code Patterns

### Pattern 1: Contract-first `MigrationSpec`

```python
from pydantic import Field

from apiforge.contracts.base import VersionedContract


class MigrationSpec(VersionedContract):
    """Closed input for a local/CI runtime migration."""

    project_root: str
    ecosystem: str
    source_version: str
    target_version: str
    framework: str | None = None
    build_tool: str | None = None
    package_manager: str | None = None
    contract_paths: tuple[str, ...] = ()
    integration_kinds: tuple[str, ...] = ()
    read_only: bool = True
    max_parallel_agents: int = Field(default=4, ge=1, le=64)

    def identity(self) -> str:
        return (
            f"{self.ecosystem}:{self.source_version}->{self.target_version}:"
            f"{self.project_root}"
        )
```

O parser deve rejeitar origem/alvo vazios, paths fora do root e `read_only=False` no perfil MVP. A ordem dos campos de entrada não pode alterar o digest.

### Pattern 2: Adapter determinístico e read-only

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class MigrationFinding:
    rule_id: str
    severity: str
    message: str
    evidence: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()


class RuntimeAdapter(Protocol):
    ecosystem: str

    def can_handle(self, source: str, target: str) -> bool: ...

    def discover(self, root: Path) -> tuple[MigrationFinding, ...]: ...

    def commands(self, root: Path) -> tuple[tuple[str, ...], ...]: ...

    def supports(self, source: str, target: str) -> bool: ...
```

Adapters não podem executar comandos diretamente. Eles apenas descrevem comandos allowlisted; o executor/sandbox aplica timeout, cwd, ambiente sanitizado e política de mutação.

### Pattern 3: Planejamento por DAG e `TaskSpec`

```python
from apiforge.contracts.task import Budgets, Recipe, TaskRisk, TaskSize, TaskSpec


def compile_migration_task(spec: MigrationSpec, findings: tuple[MigrationFinding, ...]) -> TaskSpec:
    return TaskSpec(
        id=f"migration-{spec.identity()}",
        outcome=f"migrate {spec.ecosystem} {spec.source_version} to {spec.target_version}",
        size=TaskSize.M,
        writable_paths=(spec.project_root,),
        inputs=(spec.identity(),),
        preconditions=("source and target are resolved", "sandbox is active"),
        tests=("migration unit tests", "build/test evidence", "independent verification"),
        expected_proofs=("runtime discovery", "compatibility findings", "diff receipt"),
        budgets=Budgets(max_calls=20, max_rounds=3),
        risk=TaskRisk.LOCAL_REVERSIBLE,
        strategy=Recipe.PLAN_EXECUTE_VERIFY,
        rollback="discard or restore the isolated worktree",
        acceptance_criteria=("no critical unresolved finding", "verifier accepts evidence"),
        capability_covered="runtime-migration-control-plane",
    )
```

Cada tarefa derivada por eixo (runtime, dependencies, contract, data, cloud, tests) recebe dependências explícitas. Tarefas sem dependência podem ser fan-out; tarefas que escrevem o mesmo path não podem ser concorrentes.

### Pattern 4: Status conservador

```python
def decide_status(*, critical_gaps: tuple[str, ...], evidence_ok: bool,
                  contract_breaking: bool, verification_ok: bool) -> str:
    if critical_gaps or contract_breaking:
        return "BLOCKED"
    if not evidence_ok or not verification_ok:
        return "REVIEW"
    return "DONE"
```

A implementação real deve devolver um `OutcomeBrief` e referências de prova. Não deve inferir sucesso a partir de ausência de exceção.

### Pattern 5: Configuração declarativa de matriz

```yaml
schema_version: "1"
ecosystems:
  java:
    versions: ["11", "17", "21", "25"]
    build_tools: [maven, gradle]
  python:
    versions: ["2", "3.8", "3.9", "3.10", "3.11", "3.12", "3.13", "3.14"]
    package_managers: [pip, poetry, uv]
  go:
    versions: ["1.18", "1.19", "1.20", "1.21", "1.22", "1.23", "1.24", "1.25", "1.26", "1.27"]
    tools: [go, gofmt, gofmt, govulncheck]
policies:
  allow_external_mutation: false
  require_independent_verifier: true
  critical_statuses: [contract_breaking, destructive_change, missing_toolchain]
```

O arquivo é fonte de dados, não autorização. A policy persistida do runtime continua sendo a autoridade para comandos e mutações.

## Data Flow

```text
1. Usuário fornece intenção, root e origem/alvo
   │
   ▼
2. CLI/MCP valida MigrationSpec e resolve matriz
   │
   ▼
3. Discovery lê manifests, contratos, IaC, adapters e integrações
   │
   ▼
4. Adapters produzem findings, capabilities, evidence refs e unresolved
   │
   ▼
5. Planner constrói DAG, TaskSpec selado e TaskPlan com budgets
   │
   ▼
6. Runtime Agentic executa tarefas independentes no sandbox/worktree
   │
   ▼
7. Build/test/perf/contract outputs viram receipts versionados
   │
   ▼
8. Verifier independente executa revisão, holdout/mutation e status
   │
   ▼
9. Report deriva OutcomeBrief + diff + gaps + próximos passos
```

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|------------------|----------------|
| Existing TaskSpec/runtime | Python API | Local process; policy file |
| Sandbox/worktree | Local filesystem/process | OS permissions; allowlisted commands |
| OpenAPI/gRPC contracts | Local files/parsers | None |
| Maven/Gradle/JDK | Bounded subprocess | Installed toolchain only |
| pip/Poetry/uv/Python | Bounded subprocess | Installed toolchain only |
| Go Modules/go test/race/fuzz | Bounded subprocess | Installed toolchain only |
| Redis/Mongo/DynamoDB/Neptune | Static manifests, dumps and source scans | None in MVP; SDK read-only future |
| Terraform/Docker/ECS/EKS/Lambda | Static files and existing adapters | None in MVP |
| CloudWatch/X-Ray/OTel/Datadog/Dynatrace | Existing artifacts/configuration | None in MVP; imported evidence only |
| Graphify | Local graph API | Local store |

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Contracts, matrix resolver, adapter rules, status decision | `tests/migration/test_contracts.py`, `test_matrix.py`, `test_adapters.py` | pytest, Pydantic | 90% of new decision logic |
| Integration | TaskSpec/planner, registry, CLI/MCP boundaries | `tests/migration/test_planner_verifier.py` | pytest + temp workspace | All acceptance paths |
| Vertical slice | Java, Python, Go fixtures through discovery→verify | `tests/migration/test_vertical_slice.py` | pytest, existing sandbox/evidence | 6 canonical fixtures |
| Contract/conformance | Versioned contracts and registry | `tests/contracts/test_registry.py`, `test_conformance.py` | pytest | No schema regression |
| Mutation/holdout | Falso `DONE`, missing toolchain, breaking contract, tampered receipt | `tests/migration/test_planner_verifier.py` | pytest mutation fixtures | ≥95% intentional mutations detected |
| Security | Path escape, disallowed command, external mutation flag, secret redaction | `tests/runtime/test_security.py` + migration tests | pytest | 100% critical guard cases |
| Regression | Existing runtime, gRPC, observability, performance and data adapters | Existing suite | pytest | Zero regressions |

Every acceptance test AT-001–AT-010 maps to one or more cases in the migration suite. Real toolchains are optional in CI; unavailable tools must produce a structured `blocked`/`review` evidence record, not a skipped silent pass.

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Invalid `MigrationSpec` | Fail before discovery with structured field errors | No |
| Unsupported ecosystem/version | Return `REVIEW`/`BLOCKED` with matrix gap and no patch | No |
| Toolchain absent | Record precondition failure and continue static analysis where possible | No automatic install |
| Command timeout/non-zero exit | Persist stdout/stderr, exit code and command digest; stop dependent tasks | Bounded retry only if policy allows |
| Path escape/disallowed command | Hard block and emit security finding | No |
| Contract breaking change | Block `DONE`; route to reviewer/debate gate | No |
| Conflicting specialist findings | Persist dissent and trigger referee/review gate | One bounded debate round |
| Evidence receipt mismatch | Reject verification and mark `BLOCKED` | No |
| Tampered or missing artifact | Reject `DONE`, name missing artifact | No |
| External mutation requested | Require approval gate; MVP policy rejects it | No in MVP |

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `migration.matrix_path` | string | `knowledge/runtime-migration/matrix.yaml` | Version/rule registry |
| `migration.read_only` | bool | `true` | Proíbe mutações externas no MVP |
| `migration.max_parallel_agents` | int | inherited policy | Limite superior de fan-out |
| `migration.max_calls` | int | inherited policy | Orçamento de invocações |
| `migration.command_timeout_seconds` | int | `120` | Timeout por comando bounded |
| `migration.require_independent_verifier` | bool | `true` | Gate obrigatório antes de `DONE` |
| `migration.allow_tool_install` | bool | `false` | Mantido falso no MVP |
| `migration.debate_on` | list | risk/divergence/user | Gatilhos de sala de debate |
| `migration.fixture_root` | string | `tests/fixtures/migrations` | Fixtures oficiais |

Valores de segurança não podem ser relaxados por prompt. Alterações de policy precisam passar por arquivo/policy gate persistido.

## Security Considerations

- Validar e canonicalizar todos os paths dentro do project root; rejeitar traversal, symlink escape e escrita fora de `writable_paths`.
- Usar allowlist de comandos por adapter; sem shell arbitrário, sem credenciais herdadas e com ambiente sanitizado.
- Redigir secrets de stdout/stderr e não persistir tokens, connection strings ou payloads sensíveis.
- Manter `allow_external_mutation=false` e adapters AWS/bancos/vendors read-only no MVP.
- Separar executor, planner e verifier por identidade lógica, contexto e artefatos; o verificador não pode aceitar como prova o próprio artefato originador.
- Assinar/hashear TaskSpec, plano, diff, comandos e receipts; rejeitar artefatos alterados.
- Tratar código, manifests e relatórios analisados como dados não confiáveis, impedindo prompt injection de alterar policy ou escopo.
- Exigir gate humano para `external_mutation`, `destructive`, `irreversible`, baixa confiança ou debate não resolvido.

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | JSON estruturado com `run_id`, `task_id`, `revision`, `adapter`, `phase`, `risk`, `status` e referências; sem secrets. |
| Metrics | Contar invocações, tokens, fan-out máximo, duração, retries, custo estimado, findings por severidade, evidências faltantes e `DONE/REVIEW/BLOCKED`. |
| Tracing | Spans por discovery, adapter, planner, executor, debate, verifier e receipt; preservar correlation IDs em subprocessos. |
| Vendor adapters | Datadog/Dynatrace/CloudWatch/X-Ray/OTel somente como consumidores de artefatos/configuração no MVP; nenhum vendor é requisito para decidir. |
| Graphify | Nós para serviço, runtime, versão, dependência, contrato, finding, tarefa e evidência; arestas representam impacto e prova. |
| Replay | Persistir política, versão de matriz, inputs hashes, adapter versions e normalized trajectory para replay local/CI. |

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-22 | design-agent | Arquitetura, ADRs, manifest, patterns, integrações, segurança e testes definidos. |

## Next Step

**Ready for:** `/ship .claude/sdd/features/DEFINE_API_FORGE_RUNTIME_MIGRATION_CONTROL_PLANE.md`


## Shipment Record

Shipped and archived on 2026-09-22.

