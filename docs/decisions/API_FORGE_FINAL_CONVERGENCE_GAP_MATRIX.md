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
