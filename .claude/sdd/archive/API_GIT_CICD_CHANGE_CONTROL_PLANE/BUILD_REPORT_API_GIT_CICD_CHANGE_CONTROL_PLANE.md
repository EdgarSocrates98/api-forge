# BUILD REPORT: API Git CI/CD Change Control Plane

> Implementação do control plane read-only para mudanças de API associadas a
> Git e CI/CD, com replay determinístico e evidência auditável.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `API_GIT_CICD_CHANGE_CONTROL_PLANE` |
| **Date** | 2026-09-22 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_API_GIT_CICD_CHANGE_CONTROL_PLANE.md](./DEFINE_API_GIT_CICD_CHANGE_CONTROL_PLANE.md) |
| **DESIGN** | [DESIGN_API_GIT_CICD_CHANGE_CONTROL_PLANE.md](./DESIGN_API_GIT_CICD_CHANGE_CONTROL_PLANE.md) |
| **Status** | ✅ Shipped |

## Summary

O build entrega um contrato `af-change-bundle/1`, replay local, coleta GitHub
GET-only, execução `analyze -> next-step -> graph -> evidence -> brief`,
recommendation estruturada, métricas, CLI/MCP, matriz de capabilities,
fixtures/golden/holdout e workflows de CI. Nenhuma operação de merge, push,
workflow dispatch, deploy, comentário/status ou autofix foi habilitada.

O caminho comprovado é local e offline. A coleta GitHub está implementada por
adapter e transporte injetáveis, mas uma receipt live e exemplos reais
anonimizados continuam sendo evidência externa pendente.

## Task execution and attribution

| Group | Assigned design agent | Execution | Status |
|-------|-----------------------|-----------|--------|
| Contracts | `@api-contract-architect` | direct | ✅ |
| GitHub transport/CI | `@api-vendor-integration-engineer` | direct | ✅ |
| Replay and proof | `@api-verification-engineer` | direct | ✅ |
| Application/CLI/MCP | `@api-agentic-orchestrator` | direct | ✅ |
| Governance/routing | `@api-governance-reviewer` | direct | ✅ |
| Evaluations/fixtures | `@api-test-strategist` | direct | ✅ |
| Metrics | `@api-agentic-observability-engineer` | direct | ✅ |
| Security | `@api-security-reviewer` | direct | ✅ |
| Docs/surfaces | `@api-dx-docs-reviewer` | direct | ✅ |
| Architecture | `@api-architecture-reviewer` | direct | ✅ |

`direct` significa que a implementação aplicou as responsabilidades e padrões
dos agents atribuídos no DESIGN. A ferramenta de delegação `Task` não estava
disponível; nenhum agent é reportado como executado remotamente.

## Implemented artifacts

### Core and integrations

- `src/apiforge/contracts/change_control.py`: bundle, source, check, policy,
  recommendation, evaluation and result contracts.
- `src/apiforge/integrations/github.py`: GET-only `UrllibReadOnlyTransport`,
  injected `ReadOnlyTransport`, normalization and secret redaction.
- `src/apiforge/integrations/replay.py`: validated offline bundle replay.
- `src/apiforge/application/change_control.py`: governed critical chain and
  artifact publication.
- `src/apiforge/evals/change_control.py`: deterministic recommendation shape
  evaluation.
- `src/apiforge/observability/change_metrics.py`: correlated run/stage metrics.

### Public surfaces and governance

- `apiforge change-control run`, `collect` and `verify`.
- MCP tools `change_control_run` and `change_control_collect`.
- Capability records `api.change-control`, `git.read-context` and
  `cicd.inspect-run`.
- `discover + CONTRACT` routing gap closed in the routing catalog.
- `.github/workflows/ci.yml` includes the smoke and evidence-reference gate.
- `.github/workflows/api-change-control.yml` runs the artifact replay workflow
  with `contents: read` and always uploads evidence.

### Proof and documentation

- `tests/fixtures/api_git_cicd/change_bundle.json`, `golden.json`,
  `holdout.yaml` and `real_anonymized/README.md`.
- `evals/datasets/api-git-cicd/manifest.yaml`.
- Capability matrix, usage guide, security boundary, architecture and agent
  output contract updated.
- Platform completion skill updated through `skill-creator`, validated and
  synchronized to `.agents`, `.claude`, `.devin` and `.github` mirrors.
- `api-governance-reviewer` updated and synchronized to `.agents` and
  `.claude`; `CLAUDE.md` documents the new boundary.

## Manifest deviations

The DESIGN manifest listed 37 entries. 34 were implemented directly. Three
entries were safely reduced because the existing generic implementation already
provided the required behavior without a new feature-specific branch:

| Manifest item | Decision |
|---------------|----------|
| `src/apiforge/surfaces/ide.py` | Existing `CapabilityRequest` projection preserves the new matrix record. |
| `src/apiforge/surfaces/ui.py` | Existing canonical projection preserves state/evidence/limitations. |
| `src/apiforge/capabilities/registry.py` | Existing closed matrix loader and verifier validate the new records. |

Markdown/JUnit publisher files were not added because the existing public
critical path is JSON/receipt/brief and the DEFINE marks those projections as
`SHOULD`; the workflow uploads the complete JSON artifact directory. No
provider mutation or persistent metrics backend was introduced.

## Verification results

```text
pytest -q
822 passed, 1 skipped in 43.73s

ruff check src tests
All checks passed!

ruff format --check src tests
549 files already formatted

mypy src/apiforge
Success: no issues found in 304 source files

scripts/check_release.py
API Forge release gate: PASS

apiforge agents check --root .
{"drift": [], "ok": true}

apiforge capabilities verify
{"capability_count": 13, "verified": 13, "gaps": [], "ok": true}

skill-creator quick_validate
Skill is valid!
```

Focused evidence includes change-control tests, CLI malformed-bundle
no-traceback coverage, MCP registry parity, fake-transport GitHub coverage and
two-run replay status/case identity comparison.

## Acceptance verification

| ID | Result | Evidence or remaining boundary |
|----|--------|--------------------------------|
| AT-001 | ✅ Pass locally | E2E replay exercises all five stages and produces result, receipt, recommendation and brief. Live PR ingress remains unproven. |
| AT-002 | ✅ Pass | `ReplayAdapter` and the fixture execute without network. |
| AT-003 | ✅ Governed | Missing/malformed inputs produce `AF-*` CLI errors; live token policy remains read-only. |
| AT-004 | ✅ Pass | Existing integration gateway blocks external `apply`; adapters expose no mutating method. |
| AT-005 | ✅ Pass | Closed Pydantic contracts, path checks and CLI/MCP error boundaries preserve failure state. |
| AT-006 | ✅ Pass | Existing analysis/findings and the new `discover + CONTRACT` route are exercised. |
| AT-007 | ✅ Pass as heuristic | CI observations are modeled with explicit limitations; no runtime/deploy claim is made. |
| AT-008 | ✅ Pass | E2E covers graph, receipt and governed brief. |
| AT-009 | ✅ Pass | `Recommendation` has all nine required fields and evaluator coverage. |
| AT-010 | ✅ Fixture coverage | Golden and holdout are present and declared; real anonymized samples are still pending. |
| AT-011 | ✅ Matrix/surface pass | New capabilities use existing canonical IDE/UI projections; CLI/MCP commands are registered. |
| AT-012 | ✅ Adapter pass | Source refs carry provider, kind, reference, timestamp and SHA-256; no live receipt yet. |
| AT-013 | ✅ Boundary pass | Provider secret-shaped keys and signed query strings are redacted before hashing. |
| AT-014 | ✅ Pass | `metrics.json` records run/source/base/head, stage durations, status, unresolved, adapter errors and artifact refs. |
| AT-015 | ✅ Boundary preserved | Unknown providers remain unsupported by the matrix/gateway; no silent fallback is introduced. |

## Security and operational gaps

The following are intentionally unresolved and must remain visible in the next
phase:

- no live GitHub collection receipt has been approved or replayed;
- no real anonymized PR/CI sample is committed, only the curation README;
- fork policy, provider token scope and freshness policy need a host-level
  decision before live CI collection is promoted;
- IDE/UI integration is canonical projection only, not a deployed host;
- JUnit/Markdown publisher projections and a persistent metrics backend remain
  outside this build;
- the control plane does not prove deployment success, runtime health, cost,
  rollback capability or provider permission from static/check evidence.

## Autonomous decisions

1. Kept the core bundle-first: the application consumes a normalized bundle and
   never imports a GitHub SDK or performs provider writes.
2. Used `review` for the fixture because unresolved findings and provider
   freshness limitations must not be converted into `DONE` or `ok`.
3. Reused the existing IDE/UI capability projection instead of introducing a
   parallel surface contract.
4. Added the public `collect` command while keeping credentials in the injected
   transport environment and out of persisted contracts.
5. Updated the flaky signature test input mutation so the security test always
   changes the signed value; the signature implementation was not weakened.

## Final build status

**✅ Shipped.** DEFINE, DESIGN and this build report are archived together.

The implementation is ready for the supported local read-only path; live
provider receipts and real anonymized samples remain explicitly unresolved.

The previous handoff was:

```text
/ship .claude/sdd/features/DEFINE_API_GIT_CICD_CHANGE_CONTROL_PLANE.md
```

This build report is the archived handoff artifact. Commit and push were
completed by the `/ship` phase.

## Shipment Revision

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | 2026-09-22 | ship-agent | Build report marked shipped and links relocated to the immutable archive. |
