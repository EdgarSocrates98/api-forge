# API Forge — Evo Convergence Gap Matrix

Baseline: `daae355a78664befabbc4321eeefa5c049ba37cb`

The matrix distinguishes what is already real from what this wave must
integrate. `DEFERRED_EXTERNAL` is not a silent skip; it is a boundary that
requires provider credentials or an external receipt.

| Area | Real state | Classification | Wave action |
|---|---|---|---|
| deterministic control plane | present across SDD, routing, economy and evidence | KEEP | protect and add convergence receipts |
| case/provenance/evidence | present; case loaded before analysis | KEEP | record each wave and preserve unresolved |
| AgentOps context metrics | names diverge from Context Quality | FIX | canonical metric aliases and integration regression |
| AgentOps decision gates | boolean aggregation over tri-state contract | FIX | count allow/review/block independently |
| AgentOps model metrics | token rows used as model-call count | FIX | correlate by `model_call_id`; separate token entries/provider calls/latency |
| runtime governance context | no small canonical run-scoped context object | EXTEND | add ID/ref-only `RunGovernanceContext` and persist a digest |
| governor / gain / stop | primitives exist; execution path uses legacy heuristics | INTEGRATE | shadow-to-assisted activation in `execute_run` with conservative precedence |
| recovery / loops | primitives exist; generic scheduler is still the main path | INTEGRATE | classify failure and fingerprint strategies before recovery |
| trust / tool authorization | standalone trust plane; not mandatory for every gateway/tool dispatch | INTEGRATE | enforce default-deny authorization at the actual compact gateway boundary |
| economy | ledgers and profiles exist | KEEP + INTEGRATE | reconcile governance ceilings with the most restrictive budget |
| model routing | candidate/scorecard router exists; risk and budget influence are incomplete | EXTEND | risk policy, maturity, budget envelope and challenger metadata |
| retrieval L0-L4 | ladder exists; L2 is sibling expansion and L3 hash similarity | REFACTOR_SMALL | real bounded graph traversal, honest feature-similarity naming, candidate provenance and normalized sufficiency |
| context quality | static metrics exist | EXTEND | utilization naming, required-evidence recall semantics, counterfactual eval |
| memory retrieval | deterministic ranking exists; all terms are mandatory | FIX | OR candidate generation and configurable coverage before ranking |
| memory poisoning/quarantine | governed persistence and quarantine exist | KEEP | add cross-task leakage/conflict coverage |
| observability | local spans/OTLP/correlation exist | EXTEND | decision/evidence links and model latency semantics |
| MCP | local SDK is 1.30.0; docs claim 2025-11-25 | FIX/EXTEND | adopt SDK range that contains 2026-07-28, expose compatibility honestly, add structural conformance |
| Forge Protocol | v1 facade exists; A2A delivery intentionally external | KEEP + DEFERRED_EXTERNAL | preserve v1; experimental adapter only if offline contract is provable |
| knowledge packs | freshness/impact graph exists; agent→pack carrier absent | EXTEND | declare packs in agent source and sync mirrors |
| executable lab | 8 covered, 5 declared gaps | EXTEND | add deterministic latency/auth/rate/event/pagination cases where evidence is local |
| eval plane | trace/security/memory/frontier/live architecture exists | EXTEND | trajectory gates, counterfactual context and red-team cases |
| supply chain | ranges/vendor audit; untracked `uv.lock` exists | EXTEND | evaluate universal uv lock + SBOM/audit job without duplicate lock strategy |
| CI | validate/windows/wheel/OTel plus PR host jobs exist | EXTEND | separate cost class jobs and lock verification |
| docs/outcome | previous brief reports historical date/claims | FIX | generated/current evidence-backed outcome brief and updated architecture/contracts |
| cloud/provider/live traffic | no safe local proof | DEFERRED_EXTERNAL | preserve receipts and unresolved state |

## Convergence strategy

`adapter → shadow → assisted → active → legacy removal` is the default. A
phase may remain `REVIEW` or `DEFERRED_EXTERNAL` when its required evidence is
not local. No implementation will promote a fixture, hash similarity score,
or local probe into a production/provider claim.

