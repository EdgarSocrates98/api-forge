# ModelRouteShadowReceipt/v1

§33/§29 run-scoped proof that the candidate model router was evaluated inside
`execute_run()` **without governing**. `route_model_shadow` already appends the
§29 `ShadowRecord` to the control-plane ledger
(`.apiforge/control-plane/shadow.jsonl`); this receipt binds that observation
to the run artifacts so the shadow verdict is auditable next to the work it
shadowed.

| Field | Meaning |
|---|---|
| `route` | Always `model_routing` — the decision-plane route this receipt answers |
| `mode` / `governing` | Echo of the `RouteDecision` verdict; while `rules/control_plane.yaml` keeps the route in `shadow`, `mode` is `shadow` and `governing` is `legacy` |
| `inputs` | The `ModelRouteInputs/v1` actually evaluated — only declared signals (`model_route_*` spec inputs, spec risk, risk-complexity complexity, call budget, the `AgentArtifact/v1` structured-output contract); undeclared fields stay `null` |
| `legacy_decision` | `{"selected": <adapter name>, "source": "declared_adapter"}` — the incumbent the candidate is compared against |
| `candidate` | The full `ModelRouteDecision/v1` (`selected`, `ranked`, `code`, `unresolved`) — `null` when the router/policy could not run |
| `control` | The `RouteDecision/v1` dump from `evaluate_route` |
| `code` | Router refusal (`AF-ROUTE-NO-ELIGIBLE-MODEL`), policy failure (`AF-ROUTE-POLICY-INVALID`) or evaluation-store failure (`AF-ROUTE-EVALUATIONS-INVALID`, `AF-PATH-OUTSIDE-ROOT`) |
| `policy_id` / `policy_version` / `policy_hash` | §86 anchor to `rules/model_router.yaml`: declared `version` plus `sha256:` content hash |
| `invalid_inputs` | `model_route_*` spec values rejected by validation — surfaced, never guessed |
| `unresolved` | Union of candidate `unresolved`, invalid input names and refusal codes — feeds `RunGovernanceContext.unresolved` |
| `recorded_at` | The run timestamp |

## Where it lives

- `model-route-shadow.json` inside the run directory;
- `model_route_shadow` trajectory event with the full receipt payload;
- `summary.json` and the `execute_run` return payload under
  `model_route_shadow`.

## Declared inputs

`TaskSpec.inputs` may declare `model_route_task_class`,
`model_route_reasoning_needs` (`none|light|deep`), `model_route_context_size`,
`model_route_max_latency_ms`, `model_route_max_cost`,
`model_route_needs_tool_support`, `model_route_needs_structured_output`,
`model_route_allow_challenger` and `model_route_evaluations` (a
`ModelEvaluation` JSONL inside the project root — outside paths refuse with
`AF-PATH-OUTSIDE-ROOT`). Anything not declared lands in `unresolved`; nothing
is inferred from task text.
