# DEFINE: API Forge Field Validation + System Graph Inference

> Instrumented, bias-controlled field-validation cycle on real repositories, plus an isolated (flag-off) cross-repo relation inference track validated by A/B at cycle end.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_FIELD_VALIDATION |
| **Date** | 2026-09-28 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 14/15 |
| **Source** | `.claude/sdd/features/BRAINSTORM_API_FORGE_FIELD_VALIDATION.md` (brainstorm_document) |
| **Branch** | `sdd/new-forge` |

---

## Problem Statement

API Forge's roadmap has been driven by features rather than evidence: all evals are synthetic (`evals/corpus/README.md` admits no production-coverage proof), no real-repository run has ever been recorded, and the owner cannot measure where or why users leave the API Forge flow — so the next structural investment (System/Workflow Intelligence vs Contract-to-Runtime) would be chosen by intuition. Meanwhile the multi-repo workspace graph only holds **declared** relations (`workspace/graph.py:66` ← `manifest.relations`), forcing users to explain service relationships by hand.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Owner/maintainer | Decides API Forge roadmap | No frequency data on real gaps; bets pre-written before data |
| API engineer on multi-repo system | Runs API Forge against 2+ services | Must manually declare/explain how services call each other and which topics link them |
| Independent verifier (`api-verification-engineer`) | Re-validates outcomes | No structured run record nor ground truth to check against |
| Adversarial critic (`api-adversarial-critic`) | Reviews gap report | No pre-registered hypothesis to test conclusions against |

---

## Goals

### Track F — Field Validation

| Priority | Goal |
|----------|------|
| **MUST** | F1: Versioned run-record schema `apiforge/field-run/v1` (task, scenario, repo hash, linked run_ids, automatic fields, human fields, verifier fields) |
| **MUST** | F2: `apiforge field record` derives automatic metrics from existing ledger/`summary.json`/runtime checkpoint — no new telemetry layer |
| **MUST** | F3: `apiforge field annotate` captures human fields with closed enums; invalid input refused with cataloged `AF-FIELD-*` code + `field` + `unlock` (CLI and MCP parity) |
| **MUST** | F4: Corpus manifest (`docs/field/corpus.yaml`) and pre-registered hypothesis (`docs/field/hypothesis.md`) validated by schema; `field record` refuses runs for tasks not pre-registered or registered after first run |
| **MUST** | F5: `apiforge field report` emits counts + Wilson 95% CI per `exit_reason` × repo, theme qualification (≥5 tasks across ≥2 distinct repos), H1 verdict `confirmed|refuted|inconclusive` |
| **MUST** | F6: Verifier blind re-validation recorded per run; human/verifier divergence → `unresolved`, never silently merged |
| **MUST** | F7: Wall-clock `time_to_solution` and `time_to_evidence` via recorded start/end timestamps (not `CostVector.duration_ms`) |
| **SHOULD** | F8: `apiforge field export` writes anonymized tasks into `evals/corpus/field/` runnable by the evals suite |
| **SHOULD** | F9: Semi-automatic `wrong_context` hint: ledger `LedgerRef.provenance` refs vs files touched by the solution |
| **COULD** | F10: `field report --format md` for publisher/PR comment |

### Track S — System Graph Inference (isolated)

| Priority | Goal |
|----------|------|
| **MUST** | S1: Infer cross-repo relations offline — HTTP/gRPC client call → operation served by another repo; producer/consumer of same topic/queue from existing messaging facts |
| **MUST** | S2: Inferred relations are typed `origin=inferred` (distinct from `declared`), each with `confidence` ∈ [0,1] and `provenance` (file:line / fact id) |
| **MUST** | S3: Feature flag, default OFF; field-run records the flag state and `field record` refuses baseline runs with flag ON |
| **MUST** | S4: A/B: at cycle end, re-run all multi-repo scenario tasks with flag ON; `field report --ab` reports deltas of `manual_context_required` and `time_to_solution` |
| **SHOULD** | S5: `apiforge workspace graph --inferred` / impact query traverses inferred edges, labeling them in output |
| **COULD** | S6: Emit suggested manifest relations for human promotion `inferred → declared` |

### Cycle (process, not code)

| Priority | Goal |
|----------|------|
| **MUST** | C1: Run ≥30 field tasks OR stop at 4 weeks, over 6 scenarios × ≥5 tasks, ≥3 distinct repos (≥1 own, ≥1 OSS, OpenTelemetry Demo as anchor) |
| **MUST** | C2: Critic review of gap report before any follow-up SDD opens; ≤2 qualified themes become next SDDs; none qualified → `inconclusive`, extend corpus, no new feature |

Scenarios: (1) maintenance/bug fix, (2) evolution/breaking change, (3) security (BOLA/BFLA/SSRF/authz/secrets), (4) multi-repo impact, (5) incident/observability from trace/log/metric, (6) performance.

`exit_reason` enum (closed): `knowledge_gap | capability_gap | context_gap | graph_gap | tool_gap | ux_gap | evaluation_gap | integration_gap | none`.

---

## Success Criteria

- [ ] `field-run/v1` JSON Schema published; 100% of recorded runs validate against it.
- [ ] Automatic fields (`provider_calls`, `context_bytes`, `cache_reuse`, `time_to_evidence`, `time_to_solution`) populated for ≥95% of runs without manual entry.
- [ ] Every `AF-FIELD-*` refusal code appears in the catalog; CLI and MCP outputs both carry `code`, `field`, `unlock` (parity test).
- [ ] `corpus.yaml` + `hypothesis.md` committed before the first field run (git commit timestamp < first run `started_at`); `field record` rejects 100% of non-pre-registered task ids in tests.
- [ ] Cycle closes with ≥30 runs (or 4-week stop recorded), 6 scenarios each ≥5 runs, ≥3 distinct repos.
- [ ] 100% of runs carry verifier verdict; divergence rate reported.
- [ ] `field report` output is deterministic (same inputs → byte-identical JSON) and includes Wilson 95% CI, theme qualification and H1 verdict.
- [ ] Track S on OpenTelemetry Demo: inferred relations precision ≥0.80 and recall ≥0.60 against a hand-curated ground-truth relation list (committed before inference is tuned).
- [ ] Zero baseline runs with inference flag ON (enforced + audited in report).
- [ ] A/B report covers 100% of multi-repo scenario tasks (≥5) with before/after deltas.
- [ ] ≥20 anonymized tasks exported into `evals/corpus/field/` and passing evals schema check (SHOULD).
- [ ] `apiforge sdd check --root docs/sdd` green; targeted tests green; full suite green once before ship.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Record happy path | Pre-registered task T1, completed run R1 with ledger + summary + checkpoint | `apiforge field record --task T1 --run R1 --started ... --ended ...` | Writes field-run/v1 record with automatic fields filled from existing artifacts; schema-valid |
| AT-002 | Non-pre-registered task | Task T9 absent from `corpus.yaml` | `field record --task T9` | Refused `AF-FIELD-TASK-UNREGISTERED`, `field=task`, `unlock` names corpus registration |
| AT-003 | Late registration | T2 added to corpus after first run timestamp | `field record --task T2` | Refused `AF-FIELD-LATE-REGISTRATION` |
| AT-004 | Invalid enum | Record R1 exists | `field annotate --exit-reason vibes` | Refused `AF-FIELD-ENUM`, `field=exit_reason`, `unlock` lists allowed values; CLI & MCP identical |
| AT-005 | Divergent verifier | Human `task_completed=true`, verifier `false` | `field report` | Run counted under `unresolved`, not as completed |
| AT-006 | Flag contamination | Run recorded with inference flag ON, phase=baseline | `field record` | Refused `AF-FIELD-FLAG-CONTAMINATION` |
| AT-007 | Theme qualification | 6 runs `graph_gap` across 2 repos; 7 runs `ux_gap` in 1 repo | `field report` | `graph_gap` qualified; `ux_gap` not qualified (single repo); CI reported for both |
| AT-008 | Inconclusive | No category ≥5 runs in ≥2 repos | `field report` | H1 verdict `inconclusive`; recommendation "extend corpus", no theme |
| AT-009 | Determinism | Same record set | `field report` twice | Byte-identical JSON |
| AT-010 | Missing ledger | Run R3 has no ledger file | `field record --run R3` | Automatic fields `null` with `unresolved_reason=ledger_missing`; record still valid; never fabricated |
| AT-011 | HTTP inference | Repo A has client call `POST {base}/authorize`; repo B serves `POST /authorize` | inference (flag ON) | Edge A→B `origin=inferred`, confidence, provenance file:line |
| AT-012 | Topic inference | Repo B produces `payment.authorized`; repo C consumes it | inference | Edge B→C via topic, `origin=inferred` |
| AT-013 | Flag default | Fresh workspace, no config | `workspace graph` | Zero inferred edges; declared edges unchanged |
| AT-014 | Ambiguous target | Two repos serve same path | inference | Both candidate edges with confidence <0.5 or edge withheld + `unresolved`; never silent pick |
| AT-015 | A/B | Multi-repo tasks with baseline records | re-run flag ON, `field report --ab` | Delta table per task + aggregate for `manual_context_required`, `time_to_solution` |
| AT-016 | Anonymized export | Own-repo task | `field export` | No repo name, paths hashed, no source code beyond allow-listed snippets |

---

## Out of Scope

- Arazzo, Overlay, OpenAPI 3.2.x parsing (versions `unresolved` — no primary source).
- `BusinessFlow` as a first-class entity / named workflows.
- Contract-to-Runtime Intelligence beyond existing `adapters/otel` + `observability/health`.
- Framework packs (Spring, FastAPI, Go, .NET, NestJS, Quarkus).
- GraphQL, DX/onboarding, enterprise governance.
- Scenarios: construction, architecture, migration, standalone API+events, CI/CD governance, REST↔gRPC.
- New agents, new MCP tools beyond `field` surface parity, new workflows.
- Runtime/dynamic inference from live traffic; any live AWS/DB/broker access.
- Automatic `inferred → declared` promotion (only suggestion, COULD).
- Implementing the "OAuth 2.1 across 20 repos" north-star scenario.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | No provider SDK imports in `src/`; offline, local-first | Inference is static analysis over repo facts |
| Technical | Reuse existing telemetry (`economy/run_ledger.py`, `contracts/economy.py`, `runtime/supervisor.py` checkpoint, `summary.json`) | `field record` is a join/projection, not a collector |
| Technical | Every refusal: `AF-*` code + `field` + `unlock`, cataloged (`docs/catalog-contract.md`) | New `AF-FIELD-*` family + catalog entries |
| Technical | CLI/MCP parity for new surface | Host mirrors updated |
| Technical | Edits via `apply_patch`; no direct writes to main tree during build | Build happens on branch `sdd/new-forge` |
| Process | Tests + SDD artifacts (`docs/sdd/<feature>/`) updated together; `sdd check` green | Build includes docs/sdd feature folder |
| Process | Targeted tests per task; full suite once before ship; pytest basetemp outside repo (`E:/afpt`) | Build test strategy |
| Privacy | Own repos anonymized in exports; no proprietary code in `evals/corpus/` | Export allow-list + hashing |
| Timeline | Cycle bounded: 30 runs or 4 weeks | Harness must ship before cycle start |
| Validity | Inference flag OFF during baseline | Enforced by record-time refusal |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/field/` (new: schema, record, annotate, report, export); `src/apiforge/workspace/` (inference module + graph origin field); `src/apiforge/cli*.py` + MCP surface; `docs/field/`; `evals/corpus/field/`; `docs/sdd/API_FORGE_FIELD_VALIDATION/` | Follows existing package-per-concern layout |
| **KB Domains** | agentspec: `data-quality`, `streaming`, `anti-patterns`; project skills: `api-forge-context`, `api-forge-sdd`, `api-forge-verification`, `api-forge-observability`, `api-forge-messaging` | Ledger/evidence, independent verification, OTel, producer/consumer facts |
| **IaC Impact** | None | Local-only; no infra |

---

## Data Contract

### Source Inventory
| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| Economy ledger (`economy.jsonl`) | JSONL | per run | at run end | runtime |
| `summary.json` | JSON | per run | at run end | runtime supervisor |
| Runtime checkpoint | JSON | per run | at run end | runtime supervisor |
| `docs/field/corpus.yaml` | YAML | ~30–40 tasks | before cycle | owner |
| Human annotation | CLI input | 1 per run | same day as run | owner |
| Verifier verdict | CLI/agent input | 1 per run | ≤48h after run | `api-verification-engineer` |

### Schema Contract (field-run/v1, key fields)
| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| schema | string | `apiforge/field-run/v1` | No |
| task_id | string | ∈ corpus, pre-registered | No |
| scenario | enum | 6 values | No |
| repo_ref | string | sha256 hash for own repos | No (hashed) |
| run_ids | string[] | ≥1, exist in ledger | No |
| phase | enum | `baseline | ab_on` | No |
| inference_flag | bool | false when phase=baseline | No |
| started_at / ended_at | RFC3339 | ended ≥ started | No |
| provider_calls, context_bytes, cache_reuse | int / null | null ⇒ unresolved_reason | No |
| time_to_evidence_ms, time_to_solution_ms | int / null | wall-clock | No |
| task_completed | bool | human | No |
| exit_reason | enum | 9 values | No |
| manual_context_required, human_intervention | bool | human | No |
| false_positives, false_negatives | int ≥0 | vs ground truth | No |
| verifier_verdict | enum | `agree | disagree | unresolved` | No |
| unresolved | string[] | reasons | No |

### Completeness Metrics
- ≥95% runs with all automatic fields non-null.
- 100% runs with human + verifier fields.

### Lineage Requirements
- Every automatic value traceable to source artifact path + run_id.
- Every inferred edge traceable to file:line / fact id.

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Existing ledger/summary/checkpoint contain provider_calls, context_bytes, cache_hits per run | Need small emission additions in runtime | [ ] (critic report cites `supervisor.py:283,1263`, `contracts/economy.py`) |
| A-002 | OpenTelemetry Demo is runnable/analyzable offline and its feature-flag failures give usable incident ground truth | Incident scenario needs another source | [ ] |
| A-003 | Owner can dedicate time for ~30 tasks in 4 weeks | Cycle closes at 4-week stop with <30 runs; lower power | [ ] |
| A-004 | Static facts suffice to infer HTTP client targets (base URLs via config/env) | Recall < 0.60; S limited to topic edges | [ ] |
| A-005 | Existing messaging/data facts expose topic names for producers/consumers | Topic inference needs extractor work | [ ] |
| A-006 | Verifier agent can judge completion given ground truth without seeing human label | Divergence metric meaningless | [ ] |
| A-007 | 30 runs give enough signal to qualify ≤2 themes | Report `inconclusive` more likely; extend corpus | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Specific, evidenced by repo paths |
| Users | 3 | Four roles with pain points |
| Goals | 3 | MoSCoW per track, enums fixed |
| Success | 3 | Numeric thresholds, testable |
| Scope | 2 | Explicit exclusions, but corpus repos (own + OSS besides OTel Demo) not yet named |
| **Total** | **14/15** | |

---

## Open Questions

- Which own repos + which OSS repos (with known fix/CVE) join the corpus? → needed before cycle start, not before Design.
- Primary-source verification of Arazzo 1.1 / OpenAPI 3.2.1 / Overlay 1.1 / AsyncAPI 3.1 → only matters for post-cycle SDD; stays `unresolved`.
- Exact wall-clock capture mechanism (explicit `--started/--ended` vs runtime-emitted timestamps) → Design decision.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | define-agent | Initial version from BRAINSTORM (approach C + isolation guardrail) |
| 1.1 | 2026-09-28 | ship-agent | Shipped and archived |

---

## Next Step

**Ready for:** `/ship .claude/sdd/features/DEFINE_API_FORGE_FIELD_VALIDATION.md`
