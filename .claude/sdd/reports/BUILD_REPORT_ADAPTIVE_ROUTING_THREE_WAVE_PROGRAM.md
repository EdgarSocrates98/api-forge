# BUILD REPORT: Adaptive Routing Three-Wave Program

> Relatório incremental das três ondas de evolução do roteamento determinístico.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | `ADAPTIVE_ROUTING_THREE_WAVE_PROGRAM` |
| **Date** | 2026-09-24 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_ADAPTIVE_ROUTING_THREE_WAVE_PROGRAM.md](../features/DEFINE_ADAPTIVE_ROUTING_THREE_WAVE_PROGRAM.md) |
| **DESIGN** | [DESIGN_ADAPTIVE_ROUTING_THREE_WAVE_PROGRAM.md](../features/DESIGN_ADAPTIVE_ROUTING_THREE_WAVE_PROGRAM.md) |
| **Status** | In Progress — Wave 2 complete |

## Wave Status

| Wave | Scope | Status | Commit |
|------|-------|--------|--------|
| 1 | `RoutingPlan`, papéis explícitos e execução compatível | ✅ Complete | `c3424df` |
| 2 | scorecards multidimensionais, frescor e eval adversarial | ✅ Complete | pending in this build turn |
| 3 | expertise packs e múltiplas implementações | ⏳ Pending | — |

## Wave 1 Implemented

- Added the versioned `RoutingPlan` contract with primary, fallback, parallel,
  reviewer, critic and referee roles.
- Added deterministic plan derivation and `routing-plan.json` persistence while
  keeping `routing.json` and `fallback_order` backward-compatible.
- Added explicit execution mode and fallback budget to routing policy.
- Extended capability metadata for future families, implementations and packs.
- Added auditable ControlPlane `skip` transitions and terminal semantics that
  include intentionally skipped steps.
- Updated the supervisor to start only initial roles and mark unused fallbacks
  explicitly after a successful primary.

## Wave 2 Implemented

- Added scorecard dimensions, observed token metrics and explicit freshness
  metadata while retaining legacy scalar fields.
- Excluded stale and unresolved signal observations from routing ranking and
  blocked quality promotion when freshness cannot support the claim.
- Required evidence receipts for observed scorecard signals.
- Added an explicit adversarial eval kind and a four-kind adaptive routing gate;
  the legacy three-kind default remains available for existing suites.

## Verification So Far

```text
pytest --basetemp .pytest-run -q tests/runtime/test_routing.py \
  tests/runtime/test_routing_plan.py tests/runtime/test_supervisor.py \
  tests/runtime/test_control_plane.py tests/runtime/test_runtime.py
20 passed

ruff check <Wave 1 files>
All checks passed

spec-linter DEFINE
VERDICT: PASS

spec-linter DESIGN
VERDICT: PASS
```

## Acceptance Coverage

| ID | Scenario | Wave | Status |
|----|----------|------|--------|
| AT-001 | Existing routing decision remains readable | 1 | ✅ |
| AT-002 | Plan role assignment is deterministic | 1 | ✅ |
| AT-003 | Duplicate role membership is refused | 1 | ✅ |
| AT-004 | Unused fallback is auditable and skipped | 1 | ✅ |
| AT-005 | Stale scorecard cannot promote quality | 2 | ✅ |
| AT-006 | Adversarial eval kind is enforceable | 2 | ✅ |
| AT-007 | Missing expertise pack produces an actionable refusal | 3 | ⏳ |
| AT-008 | Shared family selects multiple implementations | 3 | ⏳ |

## Deferred Scope

The previously deferred high-level autonomous commands, complete repository-type
inference, `apiforge here`, remote updates, symlinks, host overwrite sync,
task-level precedence, distributed workspace debate and total host parity remain
after ship.

## Next Step

Continue directly with Wave 2. Do not ship or open a duplicate PR until Wave 3
and final verification are complete.
