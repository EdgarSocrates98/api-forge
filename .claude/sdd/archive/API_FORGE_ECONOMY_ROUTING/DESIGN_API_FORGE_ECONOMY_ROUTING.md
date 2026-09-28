# DESIGN: API Forge Economy — Economic Routing (Onda 3)

> Technical design for implementing API_FORGE_ECONOMY_ROUTING

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_ROUTING |
| **Date** | 2026-09-27 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_ECONOMY_ROUTING.md](./DEFINE_API_FORGE_ECONOMY_ROUTING.md) |
| **Status** | ✅ Shipped |
| **Confidence** | 0.85 (codebase pattern for assessments; staged supervisor execution is new, not a KB pattern) |

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ SURFACES  runtime run|resume|debate --profile P · MCP same · sdd classify      │
│           evals economy-routing                                                │
└───────────────┬──────────────────────────────────────────────┬───────────────┘
                ▼                                              ▼
┌────────────────────────────────────────┐      ┌───────────────────────────────┐
│ runtime/economy.py                      │      │ sdd/risk.py                    │
│  resolve_profile(flag, manifest, policy)│      │  classify(diff, paths, text)   │
│  risk_floor(risk_complexity, graph)     │      │  → micro|low|medium|high       │
│  build_economy_plan(...) → EconomyPlan  │      │  → SDD profile                 │
│  trim(plan_roles, required_roles)       │      │ sdd check: PROFILE-BELOW-RISK  │
│  deterministic_proof(root, spec)        │      └───────────────────────────────┘
│  next_level(artifacts, plan) → ladder   │
└──────┬──────────────────────┬───────────┘
       │ RoutingDecision.economy
       ▼                      ▼
 runtime/routing.py       runtime/supervisor.py (staged)
 route_capabilities()      L0/L1 deterministic_proof? ──yes──► STOP (0 agent calls)
 build_routing_plan()        │no
  └ apply trims              L2 primary + risk-floor roles (concurrent, as today)
    never drops required     │ trigger(low confidence | unresolved | conflict)?
                             L3 optional reviewers (from verification reserve)
                             │ material disagreement & ceiling ≥ L4?
                             L4 debate room (max_rounds = envelope)
                             │ critical unresolved
                             L5 human gate (existing REVIEW/approval)
                     budget exhausted at any stage ⇒ AF-BUDGET-EXHAUSTED, unresolved
```

Layering: `contracts` ← `runtime/economy` ← `runtime/routing` ← `runtime/supervisor` ← surfaces. `sdd/risk` depends only on contracts and `contract_intel`.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `contracts/economy.py` (+) | `BudgetEnvelope/v1`, `EconomyPlan/v1`, `LadderStep/v1`, `RiskClassification/v1` | pydantic `VersionedContract` |
| `contracts/routing.py` | `RoutingDecision.economy: EconomyPlan \| None = None` (additive) | pydantic |
| `contracts/workspace.py` | `ProjectManifest.economy_profile: Literal[...] \| None = None` (additive) | pydantic |
| `rules/economy_profiles.yaml` | Default limits per profile + risk floors + ladder triggers | YAML package data |
| `runtime/economy.py` | Profile resolution, escalation, envelope, trims, deterministic proof, ladder decisions | pure functions |
| `runtime/routing.py` | `route_capabilities(..., economy=...)` stores plan; `build_routing_plan` applies trims | existing |
| `runtime/supervisor.py` | `effective_policy`; staged execution; reserve; stop; exhaustion | existing, contained edits |
| `sdd/risk.py` + `sdd/profiles.yaml` | Deterministic classifier, `micro` profile, below-risk check | pure functions |
| `evals/economy_routing.py` | Corpus runner vs baseline (economy disabled) with fake adapter | stdlib + asyncio |

---

## Key Decisions

### Decision 1: Staged execution — risk floor runs first, optional roles only on trigger

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-27 |

**Context:** The supervisor invokes primary, parallel, reviewers, critic and referee concurrently. A ladder needs sequencing, but risk-required roles must never be delayed or dropped.

**Choice:** Stage L2 invokes `primary` + every role in `required_roles` concurrently (identical to today for required roles). Roles the plan kept but that risk does not require (`optional_reviewers`) are invoked at L3 only when a trigger fires: `min(confidence) < policy.low_confidence`, any artifact `unresolved`, or >1 distinct recommendation. Debate (L4) is opened only if `should_open_room` fires **and** the ladder ceiling ≥ L4 **or** risk forces it. L5 remains the existing human gate.

**Rationale:** Preserves safety semantics exactly for required roles; savings come only from optional roles, parallel slots, challengers and fallbacks.

**Alternatives Rejected:**
1. Fully sequential ladder (primary alone, then reviewers) — rejected: delays risk-required review and changes current behavior for high risk.
2. No staging, only trims — rejected: cannot express "escalate on uncertainty".

**Consequences:**
- Low-risk runs make fewer calls; high-risk runs unchanged in role coverage.
- Two `run_bounded` calls instead of one when escalating (same control plane run).

---

### Decision 2: `effective_policy` is the single enforcement point

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-27 |

**Context:** `policy.max_calls` is read in 4 places; debate rounds in `debate/service.py`.

**Choice:** At run start compute `effective_policy = policy.model_copy(update={"max_calls": min(policy.max_calls, spec.budgets.max_calls, envelope.provider_calls), "max_rounds": min(policy.max_rounds, envelope.debate_rounds or 1)})` and use it everywhere `policy` was used after routing. Investigation stages (L2 + fallbacks) are capped at `investigation_calls = max_calls − reserve_calls`; L3 verification draws from `reserve_calls = ceil(max_calls × verification_share)`.

**Rationale:** One place to reason about; existing `run_bounded`/ControlPlane semantics unchanged.

**Alternatives Rejected:**
1. Threading envelope through every call site — rejected: larger diff in a 35K module.

**Consequences:** `ControlPlane.create(max_calls=effective.max_calls)`; exhaustion surfaces through existing `run_bounded` returning fewer results → mapped to `AF-BUDGET-EXHAUSTED`.

---

### Decision 3: Profile is preference, risk is a floor; escalate-only

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-27 |

**Context:** DEFINE G2/G3.

**Choice:** `requested = flag or manifest.economy_profile or policy.default` (source recorded). `floor` from `rules/economy_profiles.yaml`: complexity `critical` or risk ∈ {irreversible, destructive, external_mutation} or graph impact band `bounded` with gate `blocked` → `deep`; complexity `complex` or risk `sensitive` → `balanced`; else `economy`. `effective = max(requested, floor)` by order economy < balanced < deep. When `effective > requested` → `escalation_reason` + diagnostic `AF-ECONOMY-ESCALATED`.

**Rationale:** Economy never means accepting a worse answer.

**Alternatives Rejected:** Risk-derived only; downgrade on user request — both rejected in brainstorm.

**Consequences:** High/critical always deep (SC3).

---

### Decision 4: L0/L1 deterministic proof = latest deterministic task run covering `expected_proofs`

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-27 |

**Context:** A-003. `taskspec/runner.py` records deterministic recipe runs (dispatch verbs, no agents) in `.apiforge/tasks/<id>/runs/*.json`.

**Choice:** `deterministic_proof(root, spec)` reads runs newest-first, skips agentic runs (`schema`/`run_id` of `AgenticRun`), takes the newest deterministic run; **L0** = every step `ran` and every `spec.expected_proofs` entry appears among the run's recorded outputs/evidence refs (and `spec.expected_proofs` non-empty); **L1** = some but not all proofs present (recorded, execution continues). On L0 the supervisor persists the run with `final_status="REVIEW"`, `economy.stopped_at="L0"`, 0 invocations — acceptance still requires an independent verdict (unchanged repo rule).

**Rationale:** Reuses real deterministic evidence; no model call; stop does not bypass acceptance.

**Alternatives Rejected:**
1. New `deterministic_proof` field set by hosts — rejected: self-declared, not evidence.

**Consequences:** Exact output keys of deterministic runs verified in build; if a proof id cannot be located, result is L1 (never a false stop).

---

### Decision 5: Exhaustion is an explicit economy status, run status stays in its closed vocabulary

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-27 |

**Context:** `AgenticRun.final_status` is a closed vocabulary used across runtime/TUI.

**Choice:** On exhaustion (or ceiling reached with unresolved at non-critical risk): run `final_status="REVIEW"`, gap `AF-BUDGET-EXHAUSTED: field=profile; unlock=rerun with --profile balanced|deep or raise TaskSpec budgets` (or `AF-ECONOMY-CEILING`), and the returned payload/summary carry `economy: {status: "unresolved", stopped_at, calls_used, reserve_left, code}`. Never a silent lower-quality result.

**Rationale:** No breaking change to run states; the unresolved state is explicit and cataloged.

**Alternatives Rejected:** Adding `UNRESOLVED` to `final_status` — rejected: ripples through TUI/experience/replay.

**Consequences:** Hosts read `economy.status`.

---

### Decision 6: Risk-adaptive SDD persists `risk_class` in `intent.md` frontmatter

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-27 |

**Context:** DEFINE Q2.

**Choice:** `apiforge sdd classify` prints `RiskClassification/v1` and, with `--write <feature dir>`, sets `risk_class:` + `risk_signals:` in `intent.md` (hash cascade re-stamped by the user via `sdd stamp`). `sdd check` refuses `AF-SDD-PROFILE-BELOW-RISK` when any artifact's `profile` rank < required rank for `risk_class` (micro=0 → micro, low=1 → quick, medium=2 → standard, high=3 → critical|migration).

**Rationale:** Frontmatter already carries phase metadata and is hashed by the cascade.

**Alternatives Rejected:** `evidence/risk.json` — rejected: not visible to `sdd check` profile logic without extra lookup.

**Consequences:** Existing features without `risk_class` are unaffected.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/economy.py` | Modify | Add `BudgetEnvelope`, `LadderStep`, `EconomyPlan`, `RiskClassification` | @python-developer | None |
| 2 | `src/apiforge/contracts/routing.py` | Modify | `RoutingDecision.economy` optional | @python-developer | 1 |
| 3 | `src/apiforge/contracts/workspace.py` | Modify | `ProjectManifest.economy_profile` optional | @python-developer | None |
| 4 | `src/apiforge/contracts/{registry,__init__}.py` | Modify | Register/export new contracts | @python-developer | 1 |
| 5 | `src/apiforge/rules/economy_profiles.yaml` | Create | Limits, floors, triggers | @api-agentic-orchestrator | None |
| 6 | `src/apiforge/runtime/economy.py` | Create | resolve/floor/plan/trim/proof/ladder | @api-agentic-orchestrator | 1, 5 |
| 7 | `src/apiforge/runtime/routing.py` | Modify | Attach plan; apply trims in `build_routing_plan` | @api-agentic-orchestrator | 6 |
| 8 | `src/apiforge/runtime/supervisor.py` | Modify | effective_policy, staged L0–L5, reserve, exhaustion, economy block | @api-agentic-orchestrator | 6, 7 |
| 9 | `src/apiforge/runtime/runner.py` | Modify | Pass `profile` through run/resume/debate | @python-developer | 8 |
| 10 | `src/apiforge/cli.py` (runtime cmds) + `src/apiforge/mcp/tools.py` | Modify | `--profile` flag/param | @python-developer | 9 |
| 11 | `src/apiforge/sdd/risk.py` | Create | `classify`, rank helpers | @python-developer | 1 |
| 12 | `src/apiforge/sdd/profiles.yaml` + sdd check module | Modify | `micro` profile; `AF-SDD-PROFILE-BELOW-RISK` | @api-release-guardian | 11 |
| 13 | `src/apiforge/cli.py` (`sdd classify`, `evals economy-routing`) | Modify | Surfaces | @python-developer | 11, 14 |
| 14 | `src/apiforge/evals/economy_routing.py` | Create | Corpus runner + gates | @api-verification-engineer | 8 |
| 15 | `evals/corpus/economy-routing/*.yaml` (15) + `README.md` | Create | Ground truth | @api-test-strategist | fixtures |
| 16 | `docs/catalog-contract.md` | Modify | `AF-BUDGET-EXHAUSTED`, `AF-ECONOMY-PROFILE-INVALID`, `AF-ECONOMY-ESCALATED`, `AF-ECONOMY-CEILING`, `AF-SDD-PROFILE-BELOW-RISK`, `AF-SDD-RISK-UNRESOLVED` | @api-release-guardian | all |
| 17 | `docs/contracts/{BudgetEnvelope,EconomyPlan,LadderStep,RiskClassification}-v1.md` | Create | Release gate | @api-release-guardian | 1 |
| 18 | `tests/runtime/test_economy_plan.py` | Create | resolve/floor/trim/proof unit | @test-generator | 6 |
| 19 | `tests/runtime/test_economy_supervisor.py` | Create | AT-001..010 via fake adapter | @test-generator | 8 |
| 20 | `tests/contracts/test_economy_routing_contracts.py` | Create | AT-015 compatibility | @test-generator | 1–3 |
| 21 | `tests/sdd/test_risk_classify.py` | Create | AT-013/014, SC7 | @test-generator | 11, 12 |
| 22 | `tests/evals/test_economy_routing_eval.py` | Create | AT-012 gate logic | @test-generator | 14 |
| 23 | `docs/sdd/API_FORGE_ECONOMY_ROUTING/*.md` | Create | SDD chain (profile `standard`, `risk_class: medium`) | @api-release-guardian | all |
| 24 | `.claude/skills/api-forge-sdd/SKILL.md` + agentic skill mirrors | Modify | Route `--profile` and `sdd classify` | @api-agentic-orchestrator | 10, 13 |
| 25 | `README.md` | Modify | New flags/commands | (general) | 10, 13 |

**Total Files:** 25 entries (~45 physical incl. 15 corpus cases)

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @api-agentic-orchestrator | 5–8, 24 | Owns runtime, TaskSpec, fan-out, budgets, handoffs, gates |
| @python-developer | 1–4, 9–11, 13 | Contracts and surfaces |
| @api-verification-engineer | 14 | Independent gate over runs |
| @api-test-strategist | 15 | Ground truth per risk × profile |
| @test-generator | 18–22 | pytest per acceptance test |
| @api-release-guardian | 12, 16, 17, 23 | SDD gates, catalog, release evidence |
| (general) | 25 | Docs |

---

## Code Patterns

### Pattern 1: Contracts

```python
Profile = Literal["economy", "balanced", "deep"]
LadderLevel = Literal["L0", "L1", "L2", "L3", "L4", "L5"]


class BudgetEnvelope(VersionedContract):
    profile: Profile
    provider_calls: int = Field(ge=1)
    fanout: int = Field(ge=0)
    fallbacks: int = Field(ge=0)
    debate_rounds: int = Field(ge=0)
    challenger_slots: int = Field(ge=0)
    verification_share: float = Field(ge=0.0, le=0.5)
    ladder_ceiling: LadderLevel
    on_exhaustion: Literal["unresolved"] = "unresolved"
    silent_downgrade: Literal[False] = False


class EconomyPlan(VersionedContract):
    schema: Literal["apiforge/economy-plan/v1"] = "apiforge/economy-plan/v1"  # type: ignore[assignment]
    requested: Profile
    requested_source: Literal["flag", "manifest", "policy"]
    floor: Profile
    effective: Profile
    escalation_reason: str | None = None
    envelope: BudgetEnvelope
    minimum_roles: tuple[str, ...] = ()
    trimmed_roles: tuple[str, ...] = ()
    stop_when: tuple[str, ...] = ("deterministic_proof", "no_unresolved_critical")
    diagnostics: tuple[str, ...] = ()
```

### Pattern 2: Profile limits (YAML)

```yaml
version: 1
default_profile: balanced
order: [economy, balanced, deep]
profiles:
  economy:  {provider_calls: 4,  fanout: 0, fallbacks: 0, debate_rounds: 0, challenger_slots: 0, verification_share: 0.25, ladder_ceiling: L3}
  balanced: {provider_calls: 8,  fanout: 1, fallbacks: 1, debate_rounds: 1, challenger_slots: 1, verification_share: 0.25, ladder_ceiling: L4}
  deep:     {provider_calls: 20, fanout: 2, fallbacks: 2, debate_rounds: 2, challenger_slots: 2, verification_share: 0.30, ladder_ceiling: L5}
floors:
  deep:     {complexity: [critical], risk: [irreversible, destructive, external_mutation], gate: [blocked]}
  balanced: {complexity: [complex], risk: [sensitive]}
triggers:
  low_confidence: 0.7
```

### Pattern 3: Trim that can never remove a required role

```python
def trim(plan: RoutingPlan, economy: EconomyPlan) -> RoutingPlan:
    required = set(economy.minimum_roles)
    env = economy.envelope
    parallel = plan.parallel[: env.fanout]
    fallbacks = plan.fallbacks[: env.fallbacks]
    challengers = plan.challenger_order[: env.challenger_slots]
    trimmed = tuple(
        sorted(
            set(plan.parallel) - set(parallel)
            | set(plan.fallbacks) - set(fallbacks)
            | set(plan.challenger_order) - set(challengers)
        )
    )
    kept = plan.model_copy(
        update={
            "parallel": parallel,
            "fallbacks": fallbacks,
            "challenger_order": challengers,
            "challenger_slots": min(plan.challenger_slots, env.challenger_slots),
            "max_fallbacks": min(plan.max_fallbacks, env.fallbacks),
        }
    )
    assert required <= _role_kinds(kept)
    return kept, trimmed
```

(`_role_kinds` returns the role kinds present — reviewer/critic/referee — so the invariant is checked on kinds, which is what `required_roles` names.)

---

## Data Flow

```text
1. runtime run --profile economy <task>
2. load TaskSpec, AgenticPolicy, routing policy, economy_profiles.yaml, ProjectManifest (optional)
3. route_capabilities → risk_complexity, graph_impact (existing)
4. build_economy_plan(requested, source, assessments) → EconomyPlan (floor, effective, envelope, minimum_roles)
5. build_routing_plan(decision) → trim(plan, economy) → persisted routing + economy block
6. supervisor: effective_policy; deterministic_proof? → STOP(L0)
7. L2 invoke primary + required roles (investigation pool)
8. triggers? L3 optional reviewers (reserve)   · fallbacks per envelope
9. should_open_room & ceiling ≥ L4 → debate room (max_rounds from envelope) else ceiling unresolved
10. human gate / REVIEW (existing) · economy summary persisted (summary.json + return payload)
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| Model adapters (fake in CI) | Existing `ModelAdapter.invoke` | Existing |
| Local task store | `.apiforge/tasks/<id>/runs` read for proof | N/A |
| contract_intel | `analyze_contract` for `sdd classify --baseline/--candidate` | N/A |

---

## Testing Strategy

Targeted tests per task; full suite (`--basetemp` outside repo) + `sdd check` + release gate once at the end.

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | resolve, floor, envelope, trim invariant, proof, ladder | 18, 20, 21 | pytest | all branches of `runtime/economy.py`, `sdd/risk.py` |
| Integration | supervisor with fake adapter | 19 | pytest + asyncio | AT-001..010 |
| Eval | corpus 15 cases vs baseline | 22 + `evals economy-routing` | pytest + CLI | SC1–SC6 |
| Regression | existing `tests/runtime`, `tests/contracts`, `tests/evals` routing gates | existing | pytest | unchanged |

| AT | Test |
|----|------|
| AT-001..003, AT-011 | `test_economy_plan.py` + CLI smoke in `test_economy_supervisor.py` |
| AT-004, AT-005 | `test_economy_plan.py` (trim) + supervisor call counts |
| AT-006..010 | `test_economy_supervisor.py` |
| AT-012 | `test_economy_routing_eval.py` |
| AT-013, AT-014 | `test_risk_classify.py` |
| AT-015 | `test_economy_routing_contracts.py` |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| `AF-ECONOMY-PROFILE-INVALID` | Refusal (field `profile`), exit 2 | No |
| `AF-ECONOMY-ESCALATED` | Diagnostic in `EconomyPlan.diagnostics`, not a refusal | No |
| `AF-BUDGET-EXHAUSTED` | Run REVIEW + gap; `economy.status=unresolved` | No (rerun with higher profile) |
| `AF-ECONOMY-CEILING` | Ladder wanted a level above ceiling at non-forced risk; unresolved | No |
| `AF-SDD-PROFILE-BELOW-RISK` | `sdd check` refusal with field `profile`, unlock raise profile | No |
| `AF-SDD-RISK-UNRESOLVED` | `sdd classify` signals insufficient → class `medium` minimum, diagnostic | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `--profile` | str | (manifest → `balanced`) | Requested economy profile |
| `ProjectManifest.economy_profile` | str | null | Project default |
| `economy_profiles.yaml: profiles.*` | map | see Pattern 2 | Limits per profile |
| `economy_profiles.yaml: floors` | map | see Pattern 2 | Risk floors |
| `economy_profiles.yaml: triggers.low_confidence` | float | 0.7 | L3 escalation threshold |

---

## Security Considerations

- Risk floors are data in packaged YAML; a user flag can only raise the profile's floor requirement, never lower it (escalate-only enforced in code, tested).
- `trim` asserts the required-role invariant; violation is a programming error that fails the run as BLOCKED, never proceeds silently.
- L0 stop never produces ACCEPTED: acceptance remains a separate identity/verdict.
- No new I/O beyond reading local task runs.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | None new; persisted artifacts |
| Metrics | `economy` block in `summary.json` + run payload: calls_used, reserve_left, stopped_at, trimmed_roles; attribution rows via existing economy ledger (`source: envelope`) |
| Tracing | `decision_id` / `run_id` unchanged; `EconomyPlan` stored with routing artifacts |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-27 | design-agent | Initial version; resolves DEFINE Q1 (Pattern 2) and Q2 (Decision 6); A-001..A-003 validated against code |
| 1.1 | 2026-09-27 | ship-agent | Shipped and archived |

---

## Next Step

**Ready for:** `/agentspec:workflow:ship .claude/sdd/features/DEFINE_API_FORGE_ECONOMY_ROUTING.md`
