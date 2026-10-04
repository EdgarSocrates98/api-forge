# API Forge — step11 baseline & capability gap matrix

Date: 2026-10-04
Branch: `evo/step11-agentic-closure`
Source: `prompt_evo_step11.md` (closure/next-generation mission)

## Delivered waves (update log)

| Wave | Prompt phase | SDD feature | Status |
|---|---|---|---|
| 1 | Phase 1 — Context Quality Engine, Minimum Sufficient Context, RoleContext v2 | `API_FORGE_STEP11_CONTEXT_QUALITY` | shipped: 7 contracts, `context quality` verb, `evals context-quality` (4/4), v2 `policies:` enforced; `sdd check` ok |
| 2 | Phase 2 — Trust Plane, taint propagation, Agentic Security v2, memory security v2 | `API_FORGE_STEP11_TRUST_PLANE` | shipped: 11 contracts (`TrustUnit`/`TrustedRef`/`TrustPropagation`/`ToolRiskProfile`/`AgentPermissionSet`/`ToolAuthorization`/`MemoryGateResult`/`MemoryQuarantine`/`MemoryInvalidationPlan`/`MemoryScore`/`MemoryRankedResult`), DATA IS NOT INSTRUCTION by validator, quarantine + ranked retrieval + advisory invalidation triggers + checkpoint parity; `sdd check` ok |

## MAIN_BASELINE — GREEN

| Item | Value |
|---|---|
| commit | `7e75723` (`style: format agentic governance wave`) |
| Python | `3.12.13` (project declares `>=3.12,<3.13`) |
| env extras | `.[dev,mcp]` — boto3/textual absent, matching CI `.[dev]` plus MCP `1.30.0` |
| pytest | `1436 passed, 2 skipped` (`--basetemp` outside the repo; see host quirk) |
| ruff check | `All checks passed` (`src tests`) |
| ruff format | `871 files already formatted` (`src tests`) |
| mypy strict | `Success: no issues found in 486 source files` |
| vendor check | `127 arquivos conferem com o manifest` |
| skills mirrors | `skills: ok` |
| agents check | `drift: [], ok: true` |
| capabilities verify | `ok: true, verified: 21, gaps: []` |
| platform verify-runtime | `ok: true`, 6 verticals passed, `unresolved: []` |
| sdd check | `ok: true`, all features `done`, `refused: []` |
| pip check | no broken requirements |

### Host quirks recorded (not code defects)

- `%TEMP%\pytest-of-edgar` is ACL-corrupted on this Windows host
  (`WinError 5`, unfixable without admin). pytest must run with
  `--basetemp <dir outside the repository>`; basetemp inside the repo
  makes git-fixture tests resolve the parent `.git` and falsely pass
  refusal assertions (observed: `test_create_refuses_non_git`,
  `test_delta_refusals_carry_field_and_unlock`, `test_infer_cli...`).
- `test_collect_without_boto3_refuses` requires boto3 **absent**; it is a
  `.[dev]`-parity assumption, not a defect.
- `ruff format --check evals` reports 26 unformatted **fixture** files
  (`evals/corpus/**`); CI scopes format/lint to `src tests` — fixtures are
  adversarial inputs, not shipped code.

## Audit method

Read-path audit over `src/apiforge/**`, contracts, rules catalog, tests,
evals corpora, recent SDD cases (`API_FORGE_EVOLUTION1_*`), the EVOLUTION1
outcome brief, CI workflow and `AGENT_PROTOCOL.md`. Claims below cite the
inspected module; anything not opened is marked `unverified`, never
assumed.

## Capability matrix

Legend: **KEEP** shipped & protected · **EXTEND** exists, evolve in place ·
**REFACTOR_SMALL** exists, small reshape · **MISSING** build new ·
**DEFER** explicitly out of scope · **DEFERRED_EXTERNAL** needs
provider/cloud/credentials — contract + offline proof only.

### Context Plane

| Capability | State | Evidence | Action |
|---|---|---|---|
| ContextCapsule / refs / CAS | KEEP | `context/gateway/capsule.py`, `refs.py` | protect per §86 |
| Delta / dedup / levels / selection cache | KEEP | `context/gateway/{delta,dedup,levels,selection_cache}.py` | protect |
| Context slicing / compact | KEEP | `agentops/{slicing,compact}.py` | protect |
| RoleContextPlan | EXTEND | `contracts/selective.py:RoleContextPlan` — bytes/budget only; no required/allowed/denied kinds, memory/knowledge/artifact visibility, min trust, or per-role telemetry | v2 policy fields in `rules/role_context.yaml` + telemetry counters |
| Context Quality Engine | MISSING | no quality metrics module | new `context/quality.py` + `ContextQualityReport`/`Metric`/`UseRecord`/`SufficiencyResult` contracts; precision/recall/density/dup/stale/reuse/cache-hit/evidence-per-token |
| Minimum Sufficient Context | MISSING | none | deterministic pruning eval: full → remove low-value → rerun → compare quality; sufficiency gate |

### Memory / Knowledge Plane

| Capability | State | Evidence | Action |
|---|---|---|---|
| Governed memory store | KEEP | `memory/store.py` — append-only, candidate→persist gates, dedup, invalidation events | protect |
| Memory security gates | DONE (w2) | `memory/security.py::evaluate_gates` — §14 pipeline scope→origin→evidence→trust→outcome→freshness, persist/quarantine/reject + `quarantine.jsonl` + `review_quarantine` | shipped |
| Memory retrieval v2 | DONE (w2) | `memory/retrieval.py` — 8 deterministic signals + optional semantic bonus; `query_memory` reuses ranking | shipped |
| Memory invalidation v2 | DONE (w2) | `memory/invalidation.py::suggest_invalidations` — 8 advisory triggers (runtime/framework/contract/policy/source/evidence/outcome/dependency) | shipped |
| Trust taxonomy | DONE (w2) | `contracts/trust.py::TrustUnit` + `trust/plane.py` — transversal annotation across all §9 boundaries; `MemoryOrigin` +`knowledge` | shipped |
| Taint propagation | DONE (w2) | `trust/propagation.py::propagate` — union taint, weakest-source trust, 1-tier evidence lift, authority never widens | shipped |
| Knowledge freshness | EXTEND | `knowledge/freshness.py` (fresh/stale/unresolved/unknown) | add states verified/conflicted/deprecated + source authority + version applicability |
| Knowledge impact graph | MISSING | `graph/` is provenance-only | relation contract source→knowledge→rule→skill→agent→eval |
| SemanticCheckpoint | DONE (w2) | `tests/runtime/test_checkpoint_parity.py` — continuous == checkpoint→fresh-load→resume, `equivalent()` ignores identity only | shipped |

### Economy Plane

| Capability | State | Evidence | Action |
|---|---|---|---|
| Economy ledger / run_ledger / phase_budget | KEEP | `economy/{ledger,run_ledger,phase_budget}.py` | protect |
| Token accounting discipline | KEEP | `economy/tokens.py` — observed vs `--estimate` labeled; cost_basis_missing named | reuse pattern for unified pipeline |
| Unified token pipeline | EXTEND | pieces exist across ledger/budget/providers | `TokenLedger`/`BudgetReconciliation` contracts; estimated vs observed calibration error |
| ProviderPricing | MISSING | `rules/providers.yaml` has tiers, no versioned prices | `ProviderPricing` contract + catalog yaml, no hardcoded prices |
| Agentic budgets governor | KEEP | `governance/budget.py` hierarchical admission | protect |
| Agent Governor (holistic) | MISSING→EXTEND | supervisor + budget governor exist separately | governor contract: profile/risk/confidence/evidence/context/budget/security/complexity → max_agents/reviews/debates/retries/replans/tokens/cost/modes/tools |
| Expected Information Gain | EXTEND | `runtime/information_gain.py` (low/med/high over artifacts) | pre-action gain check for spawn/review/debate/retrieval; thresholded STOP |
| Agent Stop Policy | MISSING | no explicit STOP decision | `StopPolicy` contract: continue only when expected gain > threshold or mandatory requirement |
| Recovery governance | MISSING | none | `RecoveryPolicy`: RETRY/REPLAN/FALLBACK/ESCALATE/STOP over failure classes |
| Loop detection | MISSING | none | strategy fingerprint + repeat-strategy block |

### Decision / Policy Plane

| Capability | State | Evidence | Action |
|---|---|---|---|
| Fail-closed decision gate | KEEP | `governance/decision.py` + approval artifacts | protect |
| Shadow decision records | KEEP→EXTEND | `runtime/{shadow,scorecard_shadow}.py` | unify under lifecycle |
| Decision lifecycle shadow→assisted→active | MISSING→EXTEND | shadow exists; no lifecycle states or promotion criteria | `DecisionLifecycle` contract + fallback policy + promotion evidence gate |
| Fallback policy | MISSING | none | fallback triggers: low confidence/missing evidence/security/provider/budget |

### Runtime / Agents

| Capability | State | Evidence | Action |
|---|---|---|---|
| TaskSpec supervisor | KEEP | `runtime/supervisor.py`, sealed tasks, bounded runs | protect |
| Agent routing | KEEP | `runtime/routing.py`, scorecard routing | protect |
| Model router | EXTEND | `economy/providers.py` tiers T0–T3 + `scorecard_routing.py` | `ModelScorecard` per task class + routing shadow→assisted→active |
| Adaptive retrieval L0–L4 | EXTEND | `knowledge/retrieval.py` tiers (3/5/20) + deterministic expansion | ladder contract; escalate only on need |
| Semantic/vector retrieval | MISSING | none (deterministic only) | optional local adapter interface; never a hard dependency |
| Retrieval evals | EXTEND | eval corpora exist, none for retrieval | corpus comparing lexical/graph/hybrid on recall/precision/latency/tokens |
| Query rewriting | MISSING | deterministic expansion only | gated rewrite record (deterministic failed + budget + profile allow) |

### Tool Surface

| Capability | State | Evidence | Action |
|---|---|---|---|
| Tool adapter registry | KEEP | `agentops/tools.py`, `run_tools.py` | protect |
| Tool risk classification | DONE (w2) | `rules/tool_risk.yaml` + `trust/tools.py::authorize` — 8 risk classes, allowlist-first, default DENY with `AF-TOOL-*` | dispatcher wiring deferred to governor phase |
| Dynamic tool disclosure | EXTEND | adapters carry `capabilities`/`modes` | capability→active-tool-set resolver |
| Tool output contract | EXTEND | outputs vary | `summary/items/refs/evidence/unresolved/pagination` shape |
| Tool token benchmark | MISSING | none | measured bytes/tokens per tool + cost ranking |

### Security Plane

| Capability | State | Evidence | Action |
|---|---|---|---|
| Source path security | KEEP | `security/source_paths.py` | protect |
| Agentic threat model | MISSING | no agentic threat doc | `docs/security/agentic-threat-model.md` covering injection classes in §12 |
| Security adversarial evals | MISSING | none | `evals/corpus/security-adversarial` local corpus |

### Observability Plane

| Capability | State | Evidence | Action |
|---|---|---|---|
| Local agent spans | KEEP | `runtime/agent_telemetry.py` `AgentSpan` | protect |
| OTel GenAI export | MISSING→EXTEND | spans are local JSONL only | OTLP-shaped span projection + extended operation vocabulary |
| Correlation IDs | EXTEND | `run_id`/`task_id`/`span` exist | standardized id set (task/run/trace/span/agent/model_call/tool_call/decision/memory/context) |
| Real OTel Collector test | DEFERRED_EXTERNAL | needs docker/collector | offline OTLP acceptance test now; collector job documented |
| Observability control plane | KEEP | `observability/` adapters + receipts | protect |

### AgentOps Plane

| Capability | State | Evidence | Action |
|---|---|---|---|
| AgentOps inspect | MISSING | run ledgers + spans exist | `agentops inspect <run>` text+JSON per §54 |
| AgentOps compare | MISSING | none | `agentops compare RUN_A RUN_B` |
| Token Waste Detector | MISSING | none | `agentops waste` — duplicate context/retrieval/repeat calls/redundant agents/oversized outputs; each finding labeled OBSERVED/ESTIMATED/HYPOTHESIS |
| Self-profiling doctor | EXTEND | `economy/doctor.py`, `doctor` verb | `doctor agentic` health report across planes |

### Evals Plane

| Capability | State | Evidence | Action |
|---|---|---|---|
| Deterministic eval matrix | KEEP | `evals/` + corpora | protect |
| Live-model eval architecture | MISSING→EXTEND | none; must not gate CI | layer config + corpus; provider calls DEFERRED_EXTERNAL |
| Trace grading | MISSING | none | rubric contract over span/trace records |
| Quality/cost frontier | EXTEND | `evals agentic-quality` exists | frontier report; cost stays UNRESOLVED without provider data |
| Memory evals | MISSING | unit tests only | `evals/corpus/memory-evals` |

### Interop / MCP

| Capability | State | Evidence | Action |
|---|---|---|---|
| MCP server + gateway | KEEP | `mcp/` | protect |
| MCP 2026 compliance matrix | MISSING | no doc | `docs/mcp-compliance.md`; fill gaps without breaking old clients |
| Forge Protocol / A2A contracts | MISSING | none | `ForgeCapabilityDescriptor/Task*/Status/Result/EvidenceBundle/Handoff/Health` contracts |
| Forge kernel boundary | MISSING | none | `docs/architecture/forge-kernel-boundary.md` analysis, no extraction |

### Lab / CI

| Capability | State | Evidence | Action |
|---|---|---|---|
| Deterministic lab | KEEP→EXTEND | `tests/labs` + `matrix.yaml` | extend scenarios per §66 |
| CI matrix / wheel validation | EXTEND | `ci.yml` single py3.12 | matrix + wheel smoke where declared support exists |
| Locked dependencies | DEFER→ADR | no lock strategy | ADR documenting choice vs Spark Forge approach |
| Supply-chain audit | EXTEND | vendor manifest check exists | dependency audit step + artifact parity check |
| `doctor agentic` | MISSING | `economy/doctor.py` economy-only | aggregate health across planes |

## Explicit protections (§86)

`ContextCapsule`, `RoleContextPlan`, deterministic routing, evidence model,
content-addressed refs, context caching, information gain, compaction,
slicing, sandbox, CLI/MCP parity, SDD hash cascade — none may degrade.

## Ordering

Waves follow prompt §81 phases; each wave is one SDD feature, one commit,
with the §82 acceptance gate (problem, baseline, design, contracts,
policy, implementation, tests, evals, benchmarks, security analysis,
backward compatibility, rollback, result).
