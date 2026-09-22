# DEFINE: API Forge v1 Closure

> Close the 9 residual literal requirements of `prompt_evo_api_forge_v1.md` that the v1.1 implementation left open — without re-implementing anything already delivered.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_V1_CLOSURE |
| **Date** | 2026-09-22 |
| **Author** | define-agent |
| **Status** | ✅ Complete (Designed) |
| **Clarity Score** | 14/15 |

---

## Problem Statement

`prompt_evo_api_forge_v1.md` — the original spec that v1.1 extends — still has 9 literal requirements with no implementation: `suggest_fix`, `search_performance_memory`, noise-floor measurement, 8 of the 12 TokenSave index kinds, the named self-healing pipeline, the 5-mode autonomy vocabulary, the 11-type eval vocabulary, the lab matrix, and an operational rollback mechanism. The operator and the spec evaluator cannot verify claims the spec demands.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| API Forge operator | Engineer running the platform | Verbs the spec promises (`suggest_fix`, `search_performance_memory`) don't exist |
| Spec evaluator | Reviewer auditing against the prompt | Silent divergences (3 autonomy modes vs 5 requested; eval kinds ≠ the 11 types) undermine auditability |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | `perf memory` — persist PerformanceRuns append-only (`.apiforge/perf/runs.jsonl`, payload hash) and search by subject/tool/window, no inference |
| **MUST** | Noise floor — `perf compare --repeat-baseline` measures variance across repeated runs of the same subject; `perf verdict` names `inconclusive` when |delta| < measured floor |
| **MUST** | `perf suggest` — emits ActionPlan/diff from perf findings + facts; pure composition, never applies |
| **MUST** | `index build` emits all 12 v1 index kinds — files/symbols/routes/facts (existing) + schemas/dependencies/calls/tests/iac/databases/findings/decisions derived from facts |
| **MUST** | Self-healing pipeline `detect→explain→propose→authorize→execute→verify→compare→accept\|rollback` as a structured runbook over the policy engine; rollback step mandatory, `writable_paths` enforced |
| **MUST** | Autonomy modes reconciled with v1's 5 (`observe/recommend/sandbox/approved/continuous`) — either mapped onto the policy engine or an ADR records the justified divergence |
| **MUST** | `evals.yaml` gains `type` field with the closed 11-type vocabulary (unit/golden/integration/adversarial/holdout/regression/economy/security/compatibility/performance/e2e); `knowledge check` validates it |
| **SHOULD** | `tests/labs/matrix.yaml` declares technology × case → fixture/eval; a test verifies declared coverage (declarative, not 192 real cases — YAGNI decision) |
| **COULD** | Rollback beyond runbook semantics — a `task rollback` verb reversing `writable_paths` writes via recorded hashes |

---

## Success Criteria

Measurable outcomes:

- [ ] `apiforge perf memory search --subject <s>` returns only runs whose declared subject matches — zero results on no match, never inferred
- [ ] A verdict where |delta| < measured noise floor reports `inconclusive` with the floor value named
- [ ] `apiforge perf suggest` output validates as `ActionPlan` contract JSON and contains no execution side effects (no files written outside evidence)
- [ ] `index build` manifest lists 12 index files; each new kind is populated only from already-extracted facts
- [ ] A self-healing runbook step reaching `authorize` records a `policy_decision` in the ledger; `destructive` class without approval ends `denied`, never executed
- [ ] `knowledge check` rejects an eval whose `type` is outside the 11-value closed set
- [ ] The lab matrix test fails when a declared cell lacks its fixture/eval pointer
- [ ] `pytest`, `ruff`, `mypy`, `check_release.py` all green

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Memory round-trip | Two PerformanceRuns stored for subject `orders` | `perf memory search --subject orders` | Both runs returned, ordered; `--subject billing` returns empty |
| AT-002 | Noise floor inconclusive | 3 repeated baseline runs with ±2% variance; candidate +1.5% | `perf verdict` | `inconclusive` — delta inside the measured floor |
| AT-003 | Suggest never mutates | A case with a perf finding | `perf suggest --case` | ActionPlan JSON emitted; repo bytes unchanged except evidence receipt |
| AT-004 | Index derivation | A case with `data.redis.command` + `infra.*` facts | `index build` | `databases.jsonl` and `iac.jsonl` populated from those facts |
| AT-005 | Self-healing deny | Runbook step class `destructive`, no approval | `autonomy run` | Step `denied` with missing requirements named; nothing executed |
| AT-006 | Eval type gate | evals.yaml with `type: vibes` | `knowledge check` | `AF-KNOW-*` refusal naming the invalid type |
| AT-007 | Matrix coverage | matrix.yaml cell without fixture path | lab matrix test | Test fails naming the cell |
| AT-008 | Autonomy reconcile | `autonomy set --mode recommend` | CLI | Mode persisted and policy mapping recorded — or refused with `AF-AUTONOMY-MODE-UNKNOWN` if ADR keeps 3 modes |

---

## Out of Scope

Explicitly NOT included:

- Re-implementing anything the v1.1 work already delivered (spec forbids it).
- Eval executors that call a model — evals stay declarative data.
- Real per-cell lab fixtures — the matrix is declared; empty cells are named, not fabricated.
- Actual fault injection — chaos scenarios stay declared data for external tooling.
- Applying `suggest_fix` output — application stays behind the existing mutation path + policy gate.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Local-first, deterministic — no network, no model calls | Memory store is a local append-only file; noise floor is measured, never assumed |
| Technical | Facts immutable + provenance; `absent`/`unresolved` named, never filled | Index derivation cites fact_ids; empty kinds emit explicit empty files |
| Technical | `run` is the only family executing binaries | `suggest_fix`/heal pipeline emit plans; execution goes through existing policy-gated verbs |
| Process | Release gate must stay green: code↔doc parity, mirror sync, catalog schema | Every new verb/code needs docs + tests in the same commit |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/perf/`, `src/apiforge/index/`, `src/apiforge/autonomy/`, `src/apiforge/knowledge/`, `tests/labs/` | Extends existing modules; CLI+dispatch+MCP parity per verb |
| **KB Domains** | `knowledge/performance-methodology`, `knowledge/resilience`, `knowledge/data-access-patterns`, `knowledge/observability` | Pack evals gain the `type` field; agentspec KB has no platform-domain match |
| **IaC Impact** | None | All changes are local tooling; no infrastructure |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Facts already emitted carry enough signal for the 8 derived index kinds | Some index kinds degrade to near-empty files — still honest (absence named) | [ ] |
| A-002 | The 3 implemented autonomy modes can express v1's 5 via policy mapping, or the divergence is ADR-defensible | Otherwise a mode-vocabulary migration touches dispatch + runbooks + docs | [ ] |
| A-003 | PerformanceRun payloads are stable enough to key the memory store by subject/tool | Memory indexing keys shift — migration of runs.jsonl needed | [ ] |
| A-004 | `writable_paths` + recorded input hashes suffice as the rollback mechanism | True content rollback needs snapshotting writes — scope grows | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | 9 literal gaps enumerated with file-level evidence |
| Users | 2 | Operator + evaluator personas named; thin but sufficient for an internal tool |
| Goals | 3 | MoSCoW'd, each tied to a verifiable behavior |
| Success | 3 | Numeric/testable criteria per gap |
| Scope | 3 | Explicit in/out including YAGNI removals |
| **Total** | **14/15** | |

**Minimum to proceed: 12/15 — PASS**

---

## Open Questions

None blocking — the autonomy-mode reconciliation (map 5→3 vs migrate to 5) is the one decision the Design phase must resolve with an ADR or the mapping table.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-22 | define-agent | Initial version — extracted from BRAINSTORM_API_FORGE_V1_CLOSURE.md |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_API_FORGE_V1_CLOSURE.md`
