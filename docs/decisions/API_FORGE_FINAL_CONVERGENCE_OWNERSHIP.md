# API Forge — Final Runtime Convergence Ownership Matrix

Date: 2026-10-06 (America/Sao_Paulo)
Branch: `codex/evo-final-runtime-convergence`
Base: `0bd496b6214ae68f8df59f5a95cce111da914caf` (`main`)

This matrix is the Phase-0 audit required by the final-runtime-convergence
brief. Each row names the current implementations, the single canonical owner,
where runtime authority lives, and what happens to the parallel path. No row
may create a third owner; where a second path exists today it is either
converged or explicitly documented as a different axis.

## Matrix

| Concern | Current implementations | Canonical owner | Runtime authority | Legacy fate |
|---|---|---|---|---|
| Recovery decision | `runtime/scheduler._govern_recovery` → `governance/recovery.decide_recovery` stored in `InvocationResult.recovery`; **and** `runtime/supervisor` re-calls `decide_recovery` post-flight (~L1361) | `governance/recovery` policy evaluated once at the scheduler (first point holding failure class + attempt + policy) | `InvocationResult.recovery` | Supervisor must consume the stored decision; the second `decide_recovery` call is removed in Phase 2 |
| Recovery action execution | `retry` executed inside `run_bounded`; `fallback` partially via `sequential_failover`; `replan`/`escalate`/`stop` collapse into run status only | `scheduler` = retry; `supervisor` = replan/fallback/escalate/stop orchestration | the `RecoveryDecision` attached to the failing `InvocationResult` | New: per-decision `RecoveryReceipt` persisted under run storage (Phase 3) |
| Model routing | `runtime/model_router.route_model` + `route_model_shadow` (used by `cli_route` and MCP only); `route_model_shadow` already records through `governance/control_plane.evaluate_route` | `runtime/model_router` = candidate evaluation; `governance/control_plane` = route lifecycle/mode | legacy route (capability routing in supervisor) keeps governing | Phase 4 wires `route_model_shadow` into `execute_run`; no ACTIVE promotion without the §35 evidence gate |
| Promotion (route lifecycle) | `governance/control_plane.promote`/`demote` over `control_plane.yaml` + append-only `modes.jsonl` overlay | `governance/control_plane` | n/a — lifecycle, not runtime dispatch | Unchanged; Phase 5 adds canonical transition receipts |
| Promotion (routing-evidence gate) | `runtime/promotion.decide_promotion`/`is_active` — evidence coverage gate for capability-routing decisions | `runtime/promotion` | `PromotionGate.state` blocks/permits `execute_run` | Kept — different axis (per-decision evidence gate, not route lifecycle); naming overlap documented |
| Shadow (model route) | `route_model_shadow` → `evaluate_route(mode=shadow)` → `ShadowRecord` in `control-plane/shadow.jsonl` | `governance/control_plane` (receipt store) | never governs in shadow | Extended in Phase 4 with run-context receipt linkage |
| Shadow (capability challenger) | `runtime/shadow.decide` deterministic sampling; supervisor `_shadow` executes the sampled challenger | `runtime/shadow` (sampling) + supervisor (execution) | challenger artifact never enters run artifacts | Phase 9 adds champion/challenger comparison receipt over observable fields |
| Trust admission | `trust/plane.trust_unit`/`external_unit`, `trust/propagation.propagate` — contracts and transforms exist; runtime does **not** annotate tool/model outputs entering agent context; `RoleContextPlan.trust_floor` not enforced at admission | `trust/plane` + `trust/propagation` (annotation/propagation); admission enforced at the context-construction point in `runtime/supervisor` | admission decision recorded per context unit | Phase 6 adds the TrustUnit → propagation → admission path; data never gains instruction authority |
| Tool auth | `trust/tools.authorize` + `rules/tool_risk.yaml`; supervisor `_authorized_invoke` consults it per invocation | `trust/tools` | deny-by-default `ToolAuthorization` per call | Unchanged for declared tools |
| MCP target auth | `mcp/gateway.apiforge_call` → `authorize(target=True)`; today existence + `allowed_targets=["*"]` yields `risk_classes=("read_only",)` regardless of the target's real `ToolRiskProfile` | `trust/tools` (decision) + `mcp/gateway` (enforcement point) | target authorization per `apiforge_call` | Phase 7: look up the target's declared risk profile; unknown profile → DENY |
| Memory conflict | `memory/conflicts.detect_memory_conflicts` (detection/outcome) + `memory/store.query_memory` (admission enforcement) | `memory/conflicts` = outcome; `memory/store` = admission | `query_memory` applies admission | Phase 1: destructive+contradiction → `quarantine` before preference; conflict receipt preserved |
| Token truth | `economy/token_ledger`, `economy/run_ledger.token_coverage`, `agentops/inspect` | `economy/*_ledger` (records) + `agentops` (projection) | observed/estimated/unresolved basis per row | Phase 10: `cost_coverage` gains explicit `basis="cost_vector"`; timestamps gate critical-path |
| Loop detection | `governance/loop.check_loop` fed by strategy fingerprints recorded per run | `governance/loop` | blocks repeated strategy at run start | Replan/fallback must mint a **new** strategy fingerprint and re-enter loop detection (Phase 3) |
| Control plane (decision) | `governance/control_plane` — route modes, shadow ledger, promote/demote, fallback selection | `governance/control_plane` | `evaluate_route` decides who governs each evaluation | Phase 5: adapters from runtime-side helpers; deprecate before any removal |
| Control plane (execution) | `runtime/control.ControlPlane` — per-run step state machine, call budgets, leases | `runtime/control` | run/step lifecycle | Out of scope — execution plane, not decision plane; documented to prevent confusion |

## Naming boundary (prevents a third owner)

Two concepts share the word "promotion". They are different axes and stay
separate:

- `governance.control_plane.promote` — **route lifecycle** (shadow → assisted
  → active) over declared routes.
- `runtime.promotion.decide_promotion` — **per-decision evidence gate**
  (does this routing decision have the evidence to run locally).

Likewise `runtime.shadow` samples capability *challengers* while
`governance.control_plane` owns *route-mode* shadow receipts. Phase 5 keeps
both and documents the split rather than merging them — merging would create
a third abstraction, which the brief forbids.

## Unresolved

- `rules/control_plane.yaml` still declares `route: recovery` as
  `mode: shadow` with `legacy: supervisor-default-retry`; after Phase 2 the
  scheduler is the de-facto authority, so the route declaration needs a
  correction during Phase 5 convergence work.
- `sdd check` currently reports `AF-SDD-UPSTREAM-STALE` for
  `API_FORGE_STEP11_CONTEXT_QUALITY` (`architecture.md` upstream hash drift)
  — a pre-existing baseline defect, repaired by `apiforge sdd stamp` in this
  phase.
