# API Forge — Decision Control Plane Migration Map

Final-runtime-convergence Phase 5. Audit of the modules whose names overlap
with the §28-§32 Decision Control Plane, the canonical owner for each
concern, and the canonical receipt stores.

## Canonical owner

`apiforge.governance.control_plane` is the only authority for the route
lifecycle: `load_routes`, `route_status`/`all_routes` (declared yaml overlaid
with the append-only `modes.jsonl`), `evaluate_route` (shadow/assisted/active
verdicts), `record_shadow`/`shadow_records` (`shadow.jsonl`),
`promote`/`demote` (mode overlay + `RouteTransitionReceipt` in
`transitions.jsonl`), `detect_triggers`/`select_fallback` (§32).

## Concern map

| Concern | Runtime module | Canonical home | Status |
|---|---|---|---|
| Route shadow verdict | `runtime.model_router.route_model_shadow` delegates to `evaluate_route` | `governance.control_plane` | converged — runtime callers delegate, never reimplement |
| Route promotion/demotion | none in runtime | `governance.control_plane.promote`/`demote` | canonical; every attempt emits `RouteTransitionReceipt` |
| Capability-evolution promotion gate | `runtime.promotion` (`PromotionGate`, `EvolutionPolicy`) | stays — different concern (capability adoption, not route lifecycle) | documented, not merged |
| Challenger sampling | `runtime.shadow` (`ShadowDecision`) | stays — economy challenger selection, not a decision-plane route | documented, not merged |
| Scorecard routing shadow | `runtime.scorecard_shadow` | stays — offline capability-routing comparison | documented, not merged |
| Execution plane | `runtime.control.ControlPlane` (steps/calls per run) | stays — execution state, not decision authority | documented, not merged |
| Route-level fallback | `governance.control_plane.select_fallback` | `governance.control_plane` | canonical |
| Invocation-level fallback | `runtime.supervisor` recovery executor | stays — executes `RecoveryDecision` actions | documented, not merged |

## Canonical receipt stores

| Store | Contract | Writer |
|---|---|---|
| `.apiforge/control-plane/shadow.jsonl` | `ShadowRecord/v1` | `evaluate_route` (shadow mode) |
| `.apiforge/control-plane/modes.jsonl` | `ControlPlaneRoute` overlay row | `promote`/`demote` |
| `.apiforge/control-plane/transitions.jsonl` | `RouteTransitionReceipt/v1` | `promote`/`demote` — allowed and refused |
| run dir `recovery-receipts.json` | `RecoveryReceipt/v1` | supervisor recovery executor |
| run dir `model-route-shadow.json` | `ModelRouteShadowReceipt/v1` | `execute_run` §33 shadow hook |

## Lifecycle rule (§31)

No overlapping-named module was deleted: the audit found nominal overlap only,
not duplicated decision authority. Where a future duplicate appears, the path
is adapter → deprecated → removal, in that order. The stale `recovery` route
row (`legacy: supervisor-default-retry`) was corrected to
`scheduler-canonical-recovery` — the incumbent is the scheduler-classified
policy ladder, not a supervisor retry default.
