# BUILD REPORT: Intelligent Capability Routing Follow-ups

> Implementation report for the evidence-gated Wave 0 foundation.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | INTELLIGENT_CAPABILITY_ROUTING_FOLLOWUPS |
| **Date** | 2026-09-24 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_INTELLIGENT_CAPABILITY_ROUTING_FOLLOWUPS.md](../features/DEFINE_INTELLIGENT_CAPABILITY_ROUTING_FOLLOWUPS.md) |
| **DESIGN** | [DESIGN_INTELLIGENT_CAPABILITY_ROUTING_FOLLOWUPS.md](../features/DESIGN_INTELLIGENT_CAPABILITY_ROUTING_FOLLOWUPS.md) |
| **Status** | ✅ Shipped |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 22/22 manifest tasks |
| **Files Created** | 15 implementation/test/contract-doc files |
| **Files Modified** | 9 manifest files, plus SDD status metadata |
| **Lines Added or Created** | Approximately 800 implementation/docs/test lines |
| **Build Time** | Not timed |
| **Tests Passing** | 908/909 passed; 1 skipped |
| **Agents Used** | 0 delegated; 4 specialist patterns applied directly |

The build is intentionally limited to Wave 0. Knowledge Packs/provider
freshness, adaptive complexity/DAG, optimizer/bandit, full CLI/TUI/matrix and
external GitHub governance remain sealed future waves.

---

## Task Execution with Agent Attribution

No delegation/Task surface was available in this session. The assignments
below therefore record the matched specialist pattern applied directly by the
build agent, not a claim of delegated execution.

| # | Task | Agent | Status | Duration | Notes |
|---|------|-------|--------|----------|-------|
| 1 | Define closed evolution, coverage and promotion contracts | `@genai-architect` (direct) | ✅ Complete | - | Wave 0 state machine and safety invariants |
| 2 | Add evidence references and knowledge observation primitives | `@data-quality-analyst` (direct) | ✅ Complete | - | Unknown/limitation states preserved |
| 3 | Add canonical exports, registry and runtime persistence | `@python-developer` (direct) | ✅ Complete | - | Append-only RunStore snapshots and events |
| 4 | Implement evidence coverage and promotion policy | `@data-quality-analyst` / `@genai-architect` (direct) | ✅ Complete | - | No external calls or mutation authority |
| 5 | Integrate gate with execute/resume supervisor paths | `@genai-architect` (direct) | ✅ Complete | - | Non-active modes stop before adapter invocation |
| 6 | Add fixtures, contract/eval/runtime tests and docs | `@test-generator` (direct) | ✅ Complete | - | Focused tests: 27 passed |
| 7 | Update YAML policy and AF catalog | `(direct)` | ✅ Complete | - | New refusals are cataloged |

**Agent Key:** specialist names identify the DESIGN assignment and patterns
used; `(direct)` identifies build-agent execution without delegation.

---

## Agent Contributions

| Agent | Files | Specialization Applied |
|-------|-------|------------------------|
| `@genai-architect` (direct) | `routing_evolution.py`, `promotion.py`, `supervisor.py`, related docs | Evidence-gated state transitions, fallback and authority boundary |
| `@data-quality-analyst` (direct) | evidence/knowledge contracts, `evidence_coverage.py`, `evidence_gate.py` | Explicit coverage, missing evidence and limitation semantics |
| `@python-developer` (direct) | exports, registry, routing and RunStore | Existing immutable Pydantic and deterministic runtime patterns |
| `@test-generator` (direct) | new tests and `evolution_cases.yaml` | Contract, unit, integration and golden/holdout/mutation-shaped coverage |
| `(direct)` | YAML/catalog and release-required docs | Existing API Forge conventions; no exact specialist needed |

---

## Files Created

| File | Lines | Agent | Verified | Notes |
| ---- | ----- | ----- | -------- | ----- |
| `src/apiforge/contracts/routing_evolution.py` | 105 | `@genai-architect` | ✅ | Closed Wave 0 contracts |
| `src/apiforge/evals/evidence_coverage.py` | 41 | `@data-quality-analyst` | ✅ | Pure deterministic evaluator |
| `src/apiforge/runtime/evidence_gate.py` | 22 | `@data-quality-analyst` | ✅ | Runtime coverage boundary |
| `src/apiforge/runtime/promotion.py` | 102 | `@genai-architect` | ✅ | Policy loader and promotion state machine |
| `docs/contracts/EvidenceCoverage-v1.md` | 18 | `@data-quality-analyst` | ✅ | Contract documentation |
| `docs/contracts/RoutingEvolution-v1.md` | 17 | `@genai-architect` | ✅ | Contract documentation |
| `docs/contracts/PromotionGate-v1.md` | 22 | `@genai-architect` | ✅ | Contract documentation |
| `docs/contracts/EvidenceRef-v1.md` | 15 | `(direct)` | ✅ | Added to satisfy release contract-doc gate |
| `docs/contracts/EvolutionPolicy-v1.md` | 19 | `(direct)` | ✅ | Added to satisfy release contract-doc gate |
| `tests/contracts/test_routing_evolution.py` | 57 | `@test-generator` | ✅ | Closed fields and illegal transitions |
| `tests/evals/test_evidence_coverage.py` | 30 | `@test-generator` | ✅ | Complete/partial/missing/unresolved |
| `tests/runtime/test_evidence_gate.py` | 12 | `@test-generator` | ✅ | Limitation preservation |
| `tests/runtime/test_promotion.py` | 65 | `@test-generator` | ✅ | All Wave 0 modes and rollback |
| `tests/runtime/test_routing_modes.py` | 45 | `@test-generator` | ✅ | Persistence and supervisor integration |
| `tests/fixtures/agentic_runtime/evolution_cases.yaml` | 25 | `@test-generator` | ✅ | Golden/holdout/mutation-shaped cases |

---

## Verification Results

### Lint Check

```text
uv run ruff check .
All checks passed!
```

**Status:** ✅ Pass

### Type Check

```text
uv run mypy
Success: no issues found in 335 source files
```

**Status:** ✅ Pass

### Tests

```text
Focused Wave 0 tests: 27 passed.
Full suite with external temporary base: 908 passed, 1 skipped.
Release/environment subset with external temporary base: 16 passed.
```

**Status:** ✅ 908/909 passed; 1 intentionally skipped

Additional gates:

- `uv run python scripts/check_release.py` — `API Forge release gate: PASS`
- AgentSpec DESIGN spec-linter — `VERDICT: PASS` with no findings

The full suite was run with a temporary root outside the repository because
Windows ACL/parent-repository behavior caused false failures when pytest used
an in-repository temporary directory. The same sandbox, worktree and release
tests passed 16/16 outside that directory.

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | Ruff detected import ordering, unnecessary generators and a tuple literal | Applied focused source fixes; reran Ruff | Minimal |
| 2 | Initial contract test assertions matched the wrong Pydantic validation message | Corrected assertions to the emitted invariant message | Minimal |
| 3 | Release gate required docs for newly registered `EvidenceRef/v1` and `EvolutionPolicy/v1` | Added the two canonical contract pages | Minimal |
| 4 | In-repository Windows pytest temp root failed two sandbox cases due ACL/parent repo state | Re-ran with external temp root; all 16 environment-sensitive tests passed | Environment-only |

---

## Autonomous Decisions

| # | Decision Point | Options Considered | Chose | Rationale |
|---|----------------|-------------------|-------|-----------|
| 1 | Evidence required before supervisor execution | Use existing route evidence only; require explicit route receipt too | Require `task_spec` and `routing_decision` | Smallest auditable proof that binds the task to the route being executed |
| 2 | Rollback reference in Wave 0 | Make rollback optional; bind a deterministic local reference | Bind `{run_id}:static-routing` | Preserves the static route as an explicit reversible fallback without inventing an external artifact |
| 3 | Behavior for `replay`, `shadow` and `external-read` in active supervisor | Invoke adapters and label later; stop before active invocation | Stop and return `REVIEW`/`BLOCKED` | Prevents observational modes from becoming execution authority |
| 4 | Registry additions discovered during implementation | Leave sibling contracts unexported/unregistered; expose canonical package surface | Export/register all new Wave 0 models | Required for contract discovery, replay and the release gate |
| 5 | Missing release documentation for already registered additive models | Remove registrations; add contract docs | Add docs | Keeps the contract registry/docs invariant intact without reducing typed coverage |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| Two additional contract pages (`EvidenceRef-v1`, `EvolutionPolicy-v1`) were created beyond the 22-row Wave 0 manifest. | The release gate requires a page for every registered contract; both models are additive primitives used by the build. | Documentation-only expansion; no new runtime scope or authority. |
| Supervisor gate uses the existing static route as the rollback reference. | Wave 0 has no external rollback system and the design requires a reversible local fallback. | Keeps behavior deterministic; future waves must replace it with independently verified receipts where appropriate. |

---

## Blockers

| Blocker | Required Action | Owner |
|---------|-----------------|-------|
| None for Wave 0 | Open later waves only through a follow-up DESIGN/ITERATE gate | Maintainer |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|----|----------|--------|----------|
| AT-001 | Promotion evidence gate | ✅ Pass for Wave 0 | `test_promotion.py` covers all modes, missing evidence and rollback; supervisor shadow test proves no invocation |
| AT-002 | Missing or stale context | ⏭️ Future Wave 1 | Knowledge Pack freshness/provider receipts are explicitly sealed out of this build |
| AT-003 | Bounded adaptive DAG | ⏭️ Future Wave 2 | Adaptive planner is a sealed extension point; static route remains the fallback |
| AT-004 | Provider capability boundary | ⏭️ Future Wave 1 | Real provider/model adapters are out of scope; core remains offline |
| AT-005 | Learned-weight safety | ⏭️ Future Wave 3 | Optimizer/bandit and weight promotion are sealed out |
| AT-006 | Evidence Coverage explainability | ✅ Pass | `test_evidence_coverage.py` covers complete, partial, missing and unresolved states |
| AT-007 | Shared operational contracts | ✅ Wave 0 subset | Canonical registry, persisted gate and replay event are covered; full CLI/TUI/matrix projection is Future Wave 4 |
| AT-008 | External GitHub governance boundary | ⏭️ Future Wave 5 | Existing read-only boundary remains unchanged; governance integration is sealed out |

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Deterministic local gate overhead | No external I/O or provider calls | Pure policy/coverage calculation; full suite completed in 47.83s | ✅ |
| Adaptive/online optimization | Disabled in Wave 0 | `adaptive_plan.enabled=false`; no optimizer/bandit code added | ✅ |

---

## Final Status

### Overall: ✅ COMPLETE

**Completion Checklist:**

- [x] All tasks from the Wave 0 manifest completed
- [x] Per-file focused verification passed
- [x] Full test suite passed: 908 passed, 1 skipped
- [x] No blocking issues for Wave 0
- [x] Wave 0 acceptance tests verified; future-wave criteria marked explicitly
- [x] Ready for `/ship`

---

## Next Step

`/ship .claude/sdd/features/DEFINE_INTELLIGENT_CAPABILITY_ROUTING_FOLLOWUPS.md`
