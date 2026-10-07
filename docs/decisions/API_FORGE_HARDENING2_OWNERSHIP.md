# API Forge — Canonical Ownership Matrix

This matrix is the phase-0 authority map. Legacy modules may remain as
adapters or projections, but a new decision must be emitted by the canonical
owner below.

| Concern | Legacy / parallel surface | Canonical owner for this wave | Authority transition |
|---|---|---|---|
| governor, gain, stop | `runtime/policy.py`, supervisor heuristics | `governance/*` + `RunGovernanceContext` | preserve adapters; decisions carry policy/evidence refs |
| recovery | scheduler retry loop | `governance/recovery.py` | recovery classifies and decides; scheduler only executes decision |
| loop | post-flight supervisor call | `governance/loop.py` + `RunStore` trajectory | history-aware check before another strategy attempt |
| model route | routing plan, promotion, scorecard helpers | `runtime/model_router.py` under Decision Control Plane | shadow first; active requires explicit promotion evidence |
| promotion/demotion/fallback | `runtime/promotion.py`, shadow helpers | `governance/control_plane.py` | one decision receipt; legacy fields remain read-compatible |
| role/tool auth | orchestrator-only `_authorized_invoke` | `trust/tools.py` and MCP target gate | effective authority is subject + delegated scope + target profile |
| trust/taint | standalone trust checks | `trust/propagation.py` at context admission | tool/model data remains data-only until verified |
| context quality | metric projections | `context/quality.py` | recall denominator is declared required evidence |
| retrieval | `knowledge/retrieval.py`, adaptive levels | `knowledge/levels.py` | level-specific effective score + provenance |
| memory | store and retrieval projections | `memory/retrieval.py` + `memory/security.py` | freshness/runtime compatibility gates eligibility |
| AgentOps | report projections | `agentops/inspect.py` | observed/partial/unresolved state is never replaced by zero |
| MCP protocol | legacy server surface | `mcp/server.py` + `mcp/gateway.py` | era-specific modern proof, inner gates retained |
| lab/evals | catalog-only scenarios | `labs/catalog.py` + `evals/*` | behavioral local fixtures prove the route, not production |
| release evidence | CI-only claims | local release receipt + SDD ship evidence | local evidence is canonical; provider freshness external |

