# API Forge — Runtime Convergence Hardening II Outcome Brief

Date: 2026-10-05  
Branch: `codex/evo-hardening2-convergence`  
BASE_SHA: `eb6bab9483e611a3884e8db870b196b5818ee979`  
FINAL_SHA: `319384d` — final implementation/release state; this brief publishes as follow-up docs-only commit.

## STATUS

`RELEASE_CANDIDATE_LOCAL` — local proof complete; external gates unresolved by policy.

## OBJECTIVE

Execute `prompt_evo_hardening2.md` through governed waves, canonical owners,
runtime integration, tests, evals, observability, economy, documentation and
evidence. Preserve every unresolved boundary.

## BEFORE → AFTER

```text
BEFORE
current-only loop -> retry before recovery -> zero-filled token gaps
stale ranking basis -> shadow route regression -> partial target authority
memory freshness implicit -> 13/13 lab cells -> 151 MCP tools undocumented
AgentOps projection only -> release gate blind to new runtime codes

AFTER
persisted trajectory -> pre-retry recovery decision -> explicit coverage state
effective score provenance -> task-class shadow receipt -> role/target default-deny
freshness/runtime/conflict gates -> 21/21 executable lab cells -> 152 cataloged tools
cross-ledger timeline -> release parity gate -> local receipt with external limits
```

## P0_FIXES

| Area | Result | Proof |
|---|---|---|
| Truthfulness | token/model-call gaps remain `unresolved` or `partial`; no zero-fill | AgentOps focused tests + eval |
| Loop | persisted strategy history; repeated strategy blocked before invocation | loop/store/supervisor tests |
| Recovery | failure class + recovery action precede retry; bounded fallback/refusal | recovery/scheduler tests |
| Retrieval | ranking, sufficiency and graph contribution share effective score basis | knowledge tests + retrieval eval |

## RUNTIME_CONVERGENCE

Canonical circuit:

```text
context → trust admission → quality → role authority → governance
→ routing → tool authorization → runtime → evidence/economy/OTel
→ AgentOps → gain/stop → recovery → checkpoint/Forge Protocol
```

Ownership remains explicit in `API_FORGE_HARDENING2_OWNERSHIP.md`. Existing
modules remain adapters/projections when not canonical owners.

## LOOP

`RunStore.strategy_history()` reads append-only `strategy_selected` events.
Supervisor records strategy before control-plane/invocation. Repeated
trajectory invokes configured policy (`stop` by default), emitting
`AF-GOV-LOOP-DETECTED` before another strategy attempt.

## RECOVERY

Scheduler delegates failure classification and action to governance before
retry. Schema failures replan without retry. Tool failures retry within bound,
then fallback. Runtime ceiling emits `AF-GOV-RECOVERY-EXHAUSTED`.

## MODEL_ROUTING

Task-class scorecards select shadow candidates. Shadow receipts remain
`governing=legacy`; no implicit promotion. Missing scorecards remain explicit
unresolved signals. Model-routing eval: `3/3`.

## CONTROL_PLANE

Lifecycle remains `shadow → assisted → active`; append-only mode overlay,
shadow records, explicit fallback triggers, approval gate for active promotion,
fail-closed fallback when route lacks fallback. Active promotion remains an
explicit policy event, never a fixture inference.

## TRUST

Trust propagation preserves union taint and weakest-source trust. Only
evidence-backed governed verification removes declared removable taints;
instruction authority never widens from `none`. Tool output remains data-only
until authorized and verified.

## TOOL_AUTH

Authorization now carries role, effective subject, delegated scope, target and
known-target set. Unknown MCP targets emit `AF-MCP-TOOL-UNKNOWN`; undeclared
targets emit `AF-TOOL-AUTHZ-DENIED`. Gateway, target and inner domain gates
remain active.

## CONTEXT

Required evidence stays in recall denominator when missing. `selected_evidence_utilization`
separates admission from utilization. Context-quality eval remains passing with
unresolved useful-fact metrics preserved.

## RETRIEVAL

Hybrid and rerank paths persist `effective_score`; adaptive sufficiency uses
same score. L4 uses actual graph-depth provenance. Retrieval eval: `1/1`.

## MEMORY

Freshness, expiry, explicit runtime constraints, taint admission, risk-aware
stale handling and deterministic conflict outcomes now govern retrieval.
Destructive conflicts exclude pair and remain `unresolved`. Memory eval:
`9/9`; hardening proof passes.

## AGENTOPS

`RunInspection` exposes model-call, token, cost and trace coverage. Timeline
merges run ledger, spans and token ledger; missing timestamp/order evidence
stays visible. MCP/CLI projections added. AgentOps eval: `4/4`.

## ECONOMY

Unknown spend never becomes zero. MCP audit/benchmark measure bounded response
bytes and estimated tokens, without production latency or monetary claims.
Context capsule, knowledge selection, evidence gate and verification planning
remain economy boundaries. Provider pricing stays unresolved without a declared
pricing receipt.

## MCP

Legacy FastMCP and modern local proof remain separate eras. Modern proof order:

```text
server/discover → tools/list → tools/call
```

Modern local adapter is stateless and offline. MCP surface: `152` tools.
Audit: findings `0`, accepted overlap `1`. Benchmark: `10/10` samples.
Optional SDK handshake, HTTP transport and provider deployment remain external.

Research inputs:

- [MCP 2026-07-28 release notes](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [MCP specification changelog](https://modelcontextprotocol.io/specification/draft/changelog)
- [OpenTelemetry GenAI observability](https://opentelemetry.io/blog/2026/genai-observability/)

## FORGE_PROTOCOL

Forge Protocol v1 remains canonical local contract. A2A remains adapter-only;
no external interop capability promoted from local fixtures.

## LAB

Runtime Convergence Lab catalog: `21/21`, `0` unresolved catalog cells.
Scenarios cover recovery, loop, shadow routing, authorization denial, memory
stale/conflict, context missing evidence and challenger comparison. Lab proves
deterministic local behavior only.

## SUPPLY_CHAIN

Supply audit: `ok=true`, `failed=0`, `unpinned=[]`, vendor parity PASS,
corpus `29/195`, MCP surface lock `152`. Release gate PASS. New runtime/MCP
codes are cataloged; undocumented-code parity failure was found by full suite
and fixed in `f109c23`.

## TESTS

| Gate | Result |
|---|---|
| Full pytest after final fix | `1751 passed, 2 skipped` |
| Ruff check | PASS |
| Ruff format check | PASS |
| mypy strict | PASS |
| uv lock check | PASS |
| release gate | PASS |
| skills validation | PASS |
| agent mirrors | PASS; drift `[]` |
| capabilities | PASS; `21/21` |
| hardening2 SDD check | PASS; no unresolved/refused |
| platform runtime proof | PASS; six local verticals |
| security adversarial eval | `9/9`, no escaped cases |
| control-plane eval | `3/3` |
| memory eval | `9/9` |
| context-quality eval | PASS; unresolved metrics retained |
| retrieval eval | `1/1` |
| model-routing eval | `3/3` |
| AgentOps eval | `4/4` |
| Lab catalog | `21/21` |

## CI

Local release receipt complete. GitHub CI, runner health, provider freshness,
deployment safety and PR mutation remain read-only/external boundaries.

## EXTERNAL_GATES

`UNRESOLVED` by evidence policy:

- external CVE/advisory database freshness;
- `pip check` outside current uv interpreter;
- optional FastMCP SDK handshake and HTTP transport;
- live provider/database/broker behavior;
- deployment and production SLO receipts;
- external CI runner health.

## REGRESSIONS

Initial final-suite run exposed release-catalog parity gap for modern MCP and
runtime loop-history codes. Catalog fixed; focused proof and second full suite
pass. No remaining known regression.

## DEFERRED

No new runtime/kernel/provider integration. No external mutation. Active model
promotion, live MCP transport, cloud posture and production performance await
independent receipts and policy gates.

## NEXT

Run external provider/CI/security gates when credentials, receipts and policy
approvals exist. Keep local evidence immutable and rerun SDD/release gates on
any promotion.

## OPEN

```text
OPEN-1  CVE/advisory freshness             external receipt required
OPEN-2  optional MCP SDK/HTTP behavior      environment + protocol receipt required
OPEN-3  provider/deployment/SLO claims      independent production evidence required
OPEN-4  monetary cost accuracy              declared provider pricing required
```

## COMMITS

| Wave | Commit | Scope |
|---|---|---|
| phase 0 | `b2c01f8` | baseline, gap matrix, ownership, SDD |
| P0 truthfulness | `49da337` | unresolved AgentOps token semantics |
| P0 context | `9757e74` | required evidence recall/utilization |
| P0 loop | `640a1da` | persisted strategy history and pre-invocation gate |
| P0 recovery | `80c98cf` | governed retry/recovery ordering |
| P0 retrieval | `51addc3` | effective ranking and graph provenance |
| P1 routing | `7368ddf` | task-class shadow routing |
| P1 authority | `6953b8f` | role/delegation/MCP target authorization |
| P1 memory | `f420e41` | freshness/runtime/conflict hardening |
| P1 MCP | `f6477f1` | modern local protocol proof |
| P1 Lab | `73b3106` | 21 executable scenario cells |
| P1 AgentOps | `9e8f505` | coverage timeline and waste evidence |
| release evidence | `8990a01` | release receipts and SDD closure |
| release parity | `f109c23` | catalog parity for new AF codes |
| source normalization | `319384d` | official Ruff formatting across converged sources |

## GAPS

No local gate remains failed. External gates remain explicit, bounded and
unresolved. No claim promoted without independent evidence.
