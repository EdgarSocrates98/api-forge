# DEFINE: API Forge Economy — Economy Evals (Onda 6)

> A canonical task × profile matrix with separate quality, evidence, cost, context and latency axes, plus the gate, replay, ROI, information-gain and quality-floor machinery that keeps future economy changes honest.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_EVALS |
| **Date** | 2026-09-28 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 14/15 |
| **Source** | `.claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_EVALS.md` |

---

## Problem Statement

Each economy wave has its own eval, but nothing runs the three profiles over the same canonical API tasks with correctness as an explicit axis, nothing blocks an optimization that regresses safety, stored runs cannot be re-evaluated under a new policy, the value of extra agents is unmeasured, and routing lets low-quality candidates compete on cost.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Maintainer | Changes economy policy | No proof a change keeps quality and safety |
| Operator | Chooses a profile | No comparable per-profile numbers |
| Router | Picks candidates | Cost and quality mixed |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | G1: `evals economy-matrix`: ≥ 15 canonical tasks (OpenAPI additive/breaking variants, gRPC compatible/breaking) × economy/balanced/deep; per run separate axes: quality (verdict correct + safety invariant), evidence (deterministic change ids), cost (calls, fanout, trimmed roles), context (role bytes), latency (ms, informational) (§72–75) |
| **MUST** | G2: holdout cases reported and gated separately; contract mutants must flip compatible → breaking (mutation score) (§73, §76) |
| **MUST** | G3: `evals gate --baseline A --candidate B [--max-quality-regression 0]` → `EvaluationGate/v1` ship/reject; any safety regression rejects (§76) |
| **MUST** | G4: `evals replay --root R [--profile P]` → `ReplayReport/v1`: stored decisions re-planned under current policy; removed risk-required roles must be 0 (§77–78) |
| **SHOULD** | G5: `economy roi --root R` → `RoleROI/v1` per non-primary capability: calls, facts added, unresolved added, outcome changed (§79) |
| **SHOULD** | G6: information gain `low|medium|high` recorded in the economy block with reason; low gain explains an L3 skip (§80) |
| **SHOULD** | G7: `ScorecardRoutingPolicy.quality_floor` (opt-in): below floor excluded; champions ordered by observed cost (§34–35) |

---

## Success Criteria

- [ ] 16 tasks × 3 profiles = 48 runs: quality axis 1.0 in every profile; safety regressions 0.
- [ ] Cost axis monotone: mean calls economy ≤ balanced ≤ deep.
- [ ] Mutation score 1.0 on ≥ 8 mutants; holdout cases pass.
- [ ] Gate: identical report → ship; report with one flipped verdict → reject.
- [ ] Replay over stored runs: 0 removed risk-required roles.
- [ ] Quality floor: §35 example ranks B before A and excludes C.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Matrix | corpus | `evals economy-matrix` | 48 rows, axes separate, gates pass |
| AT-002 | Mutation | compatible task | mutant applied | verdict breaking |
| AT-003 | Gate ship | same report twice | `evals gate` | `ship` |
| AT-004 | Gate reject | candidate with a wrong verdict | `evals gate` | `reject`, reason names the case |
| AT-005 | Replay | stored runs | `evals replay` | per-run diff, `removed_required_roles` empty |
| AT-006 | ROI | run with reviewer | `economy roi` | reviewer row with calls and outcome_changed |
| AT-007 | Info gain | agreeing artifacts, no unresolved | run | `information_gain: low` |
| AT-008 | Quality floor | A(0.98,10) B(0.96,3) C(0.70,1), floor 0.95 | assess | order B, A; C excluded |
| AT-009 | Invalid report | malformed file | gate | `AF-EVALS-GATE-INVALID` |

---

## Out of Scope

- LLM-judged answer quality; monetary cost without explicit pricing; external real-API corpus.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Offline, fake adapter only | Quality = deterministic verdict + safety |
| Technical | Defaults unchanged (floor opt-in) | Existing routing tests stable |
| Technical | AF codes cataloged | `AF-EVALS-GATE-INVALID`, `AF-REPLAY-*` |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/evals/{matrix,gate,replay}.py`, `economy/roi.py`, `runtime/information_gain.py`, scorecard routing | Additive |
| **KB Domains** | testing | — |
| **IaC Impact** | None | — |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | `diff_contracts` flags required removal, path removal, enum narrowing as breaking | Mutants not detected | [ ] build |
| A-002 | Stored runs keep `routing.json` with the decision | Replay impossible | [x] RunStore.save_routing |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | |
| Users | 3 | |
| Goals | 3 | |
| Success | 3 | |
| Scope | 2 | quality limited to deterministic verdicts |
| **Total** | **14/15** | |

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | define-agent | Initial version |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_API_FORGE_ECONOMY_EVALS.md`
