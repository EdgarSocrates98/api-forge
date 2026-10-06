# API Forge — Final Runtime Convergence Gap Matrix

Baseline: `docs/decisions/API_FORGE_FINAL_CONVERGENCE_BASELINE.md`
Ownership: `docs/decisions/API_FORGE_FINAL_CONVERGENCE_OWNERSHIP.md`

Audit of `main` @ `0bd496b` against the final-runtime-convergence brief.
Classifications: `FIX` = real defect, `CONVERGE` = parallel implementations
to unify, `INTEGRATE` = exists but not in the normal runtime path,
`HARDEN` = works but semantics need tightening, `KEEP` = preserve as-is.

| # | Concern | Exists | Runtime integrated | Observed defect / gap | Classification | Phase action |
|---|---|---:|---:|---|---|---|
| 1 | Memory conflict semantics | yes | yes | `detect_memory_conflicts` returns `prefer_a`/`prefer_b` for `risk=destructive` while `query_memory` excludes both records — outcome contradicts the result set | FIX | destructive+contradiction → `quarantine` before preference; audit trail preserved; coherence tests |
| 2 | Recovery decision | yes | yes | supervisor re-runs `decide_recovery` post-flight after the scheduler already stored `InvocationResult.recovery` — dual authority | CONVERGE | supervisor consumes the stored decision; single evaluation per failure |
| 3 | Recovery action execution | partial | partial | `replan`/`fallback`/`escalate`/`stop` decisions do not alter runtime behavior; no per-decision receipt | INTEGRATE | execute each action through its owner; persist `RecoveryReceipt` with `action_executed` |
| 4 | Model router in normal runtime | yes | no | `route_model_shadow` only reachable via CLI/MCP; `execute_run` never produces a model-route shadow receipt | INTEGRATE | derive `ModelRouteInputs` from declared run inputs only; shadow receipt inside `execute_run`; legacy governs |
| 5 | Decision control plane | yes | partial | route lifecycle in `governance/control_plane`; runtime helpers (`runtime/promotion`, `runtime/shadow`) overlap in naming; `control_plane.yaml` declares `recovery` as `shadow`/`legacy: supervisor-default-retry` — stale vs scheduler authority | CONVERGE | migration map + adapters; canonical transition receipts; correct the stale recovery route row |
| 6 | Trust / taint path | contracts | partial | tool/model/external outputs enter agent context without `TrustUnit`; `RoleContextPlan.trust_floor` not enforced at admission | INTEGRATE | annotate → propagate → admit; verified evidence never gains instruction authority |
| 7 | MCP target authorization | yes | yes | `authorize(target=True)` returns `risk_classes=("read_only",)` for any registry target; `allowed_targets=["*"]` authorizes security-impacting tools by existence only | FIX | look up the target's real `ToolRiskProfile`; unknown profile → DENY; risk-class grant check per subject |
| 8 | MCP real SDK proof | contract-shape proof | n/a | `ModernMcpServer/Client` prove contract shape only; no real-SDK `tools/list`/`tools/call` evidence | DEFERRED_EXTERNAL | if the `mcp` extra is installed run the SDK proof; else classify and do not block release |
| 9 | Champion/challenger comparison | sampling + execution | partial | challenger runs but no canonical comparison receipt over observable fields; challenger implicitly interchangeable with fallback | HARDEN | `ChallengerComparison` receipt: quality/latency/tokens/cost/evidence/correctness fields only |
| 10 | AgentOps semantics | yes | yes | `cost_coverage` measures `CostVector` presence, not monetary pricing (name lies); ledger rows carry no timestamps; no critical-path derivation gated on timestamp coverage | HARDEN | `basis="cost_vector"`; optional timestamp on `RunLedgerEntry`; critical path unresolved without coverage |
| 11 | Lab / evals / replay | yes | yes | no behavioral scenario for destructive memory conflict, replan, fallback, model-route shadow, taint admission, MCP risk denial, challenger comparison; security evals lack the five listed threat cases | EXTEND | add only gap-tied scenarios; replay captures loop/recovery/model-shadow/tool-authz/trust events |
| 12 | Release proof | yes | yes | no convergence outcome brief; baseline SDD drift (`AF-SDD-UPSTREAM-STALE` on `STEP11_CONTEXT_QUALITY`) | FIX + EXTEND | re-stamp SDD; outcome brief; full local gate evidence |

## Explicitly NOT gaps (audit result, kept)

- `evaluate_route`/`promote`/`demote` already enforce shadow → assisted →
  active with evidence + approval; no third lifecycle needed.
- `trust/propagation.propagate` already unions taint and never widens
  instruction authority — Phase 6 consumes it rather than rebuilding it.
- `token_ledger`/`run_ledger` already separate observed/estimated/unresolved;
  AgentOps already refuses to zero-fill — Phase 10 adjusts naming, not truth.
- `runtime/control.ControlPlane` is the execution plane (steps/calls), a
  different concern than the decision plane — documented, not merged.

## Unresolved at Phase-0 close

- Full-suite pytest number pending in this environment (run in progress;
  `pytest-of-edgar` basetemp was unwritable — local `.pytest_tmp` used).
- `next-step` refuses the stale persisted case (`AF-ROUTING-NO-ROUTE` on the
  historical fixture findings) — recorded; the wave proceeds on the audited
  source path, not on the stale case.

## Phase progress

- **Phase 1 (row 1) — DONE locally.** `MemoryConflict` now carries
  `preferred_memory_id`/`conflicting_memory_id`/`admission_effect`;
  destructive+contradiction yields `quarantine`/`exclude_both` before any
  preference is computed, and `query_memory` filters on `admission_effect`
  so outcome and result set are coherent by construction. Commit `dee0d2b`.
- **Phase 2 (row 2) — DONE locally.** `classify_failure` moved to
  `governance/recovery` as the single surface; the supervisor consumes
  `InvocationResult.recovery` and only classifies post-invocation errors.
  Commit `f25e9bb`.
- **Phase 3 (row 3) — DONE locally.** `RecoveryReceipt/v1` added; the
  supervisor executes each terminal decision once — `retry` (supervisor-side)
  runs one accounted `recovery` call, `replan` re-routes excluding failed
  capabilities through `ControlPlane.add_steps` + strategy loop check,
  `fallback` consumes `RoutingDecision.fallback_order` bounded by
  `max_fallbacks`, `escalate` raises the `recovery_escalation` human-gate
  reason (declared in `agentic_runtime.yaml`), `stop` is terminal.
  Receipts persist in `recovery-receipts.json`, the governance context and
  summary; `resume_existing_run` runs the same executor; depth is bounded
  at one (`AF-GOV-RECOVERY-DEPTH` skipped receipts).
- **Phase 4 (row 4) — DONE locally.** `execute_run` now evaluates the §33
  candidate router through `route_model_shadow` on every governed run.
  `ModelRouteInputs` derives only from declared run data — `model_route_*`
  spec inputs, spec risk, the risk-complexity complexity, the remaining call
  budget and the `AgentArtifact/v1` structured-output contract; undeclared
  fields stay `None` and land in `unresolved`. Scorecards load only from a
  declared `model_route_evaluations` JSONL confined to the project root
  (`AF-PATH-OUTSIDE-ROOT`, `AF-ROUTE-EVALUATIONS-INVALID`). The typed
  `ModelRouteShadowReceipt/v1` persists in `model-route-shadow.json`, a
  `model_route_shadow` trajectory event, `summary.json` and the return
  payload; the §29 `ShadowRecord` lands in the control-plane ledger.
  `governing` stays `legacy` — the declared adapter remains authoritative.
  Commit `7990659`.
- **Phase 5 (row 5) — DONE locally.** `governance.control_plane` confirmed as
  the sole route-lifecycle authority; the overlap with `runtime.promotion`,
  `runtime.shadow`, `runtime.scorecard_shadow` and `runtime.control` was
  nominal, not duplicated decision authority — boundaries documented in
  `docs/decisions/API_FORGE_CONTROL_PLANE_MIGRATION_MAP.md` and module
  docstrings instead of deleting code (§31). Every promote/demote attempt
  now emits a canonical `RouteTransitionReceipt/v1` into
  `control-plane/transitions.jsonl`. The stale `recovery` row was corrected:
  `legacy: scheduler-canonical-recovery` names the post-Phase-2 incumbent.
  Commit `235235a`.
- **Phase 6 (row 6) — DONE locally.** Trust admission is wired into
  `plan_roles`: every admitted capsule ref carries its annotated
  `TrustUnit` (`RoleContext.trust_units` records it per role) and
  run-produced artifacts enter downstream roles as `model_generated`
  first-party data — `instruction_authority=none` throughout, and
  verification still cannot turn data into instruction. `RoleContextPolicy`
  gained `trust_floor` and `denied_taints`; `admit_refs` enforces both with
  `AF-TRUST-FLOOR`/`AF-TRUST-TAINT-DENIED` notes in `plan.unresolved`. The
  shipped policy denies `prompt_injection`, `instruction_laundering` and
  `malicious_artifact` on every role and declares `trust_floor: observed`
  for reviewer/critic/referee over external refs. Commit pending.
