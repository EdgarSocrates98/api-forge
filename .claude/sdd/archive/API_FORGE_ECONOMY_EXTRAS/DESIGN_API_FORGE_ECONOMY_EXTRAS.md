# DESIGN: API Forge Economy — Verification, Retrieval, Evidence and Providers (Onda 7)

> Seven deterministic, read-only modules behind verbs; nothing executes tests, calls a model or fetches the network.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_EXTRAS |
| **Date** | 2026-09-28 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_ECONOMY_EXTRAS.md](./DEFINE_API_FORGE_ECONOMY_EXTRAS.md) |
| **Status** | ✅ Shipped |

---

## Architecture Overview

```text
verify plan --changed F.. [--risk R]
   risk → ladder (micro V1 · low V2 · medium V4 · high V5; breaking contract ≥ V4)
   tests ← cached capsule test refs whose deps hold F  ∪  test files mentioning symbols defined in F
          ∪ tests importing F's module   → VerificationPlan/v1 {level, tests[{path, reasons}], commands, skipped_levels}
knowledge search --query Q [--tier n]
   rules/query_expansion.yaml → expanded terms → passages (## sections of selected-or-all packs)
   score = 3·heading hits + body hits + 2·(pack selected by trigger) − stale penalty → tiers 3 / 5 / rest
evidence resolve evidence://{operation|fact|finding|rule}/<id>
   case graph → node props + one-hop neighbors as evidence:// refs + ctx:// of the source slice
economy doctor [--root]  → EconomyDoctor/v1 findings (cache off, deep default, no capsule usage,
   pretty output only, stale packs, no transcript tokens, escalation-heavy runs, shared cache unset)
economy providers / economy tier --capability C --risk R [--family F]
   rules/providers.yaml ProviderCapability/v1 · TierDecision/v1 T0–T3 (no evidence → no downgrade)
agentops prompt --capability C --task T → PromptEnvelope/v1 {prefix, prefix_sha256, suffix}
   supervisor sets AgentRequest.prompt_prefix_sha256 per capability
workspace locality --target <repo> [--transitive] → LocalityPlan/v1 tiers
```

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `contracts/economy_extras.py` | VerificationPlan, SelectedTest, RetrievalResult, Passage, EvidenceNode, EconomyDoctor, DoctorFinding, ProviderCapability, TierDecision, PromptEnvelope, LocalityPlan | pydantic |
| `verification/selection.py` | Ladder + test selection | cache store, ast/regex |
| `knowledge/retrieval.py` + `rules/query_expansion.yaml` | Expansion, ranking, tiers | regex |
| `evidence/resolve.py` | `evidence://` resolver | case graph |
| `economy/doctor.py` | Economy diagnostics | ledger, policies, packs |
| `economy/providers.py` + `rules/providers.yaml` | Descriptors + tiering | YAML, scorecards |
| `runtime/prompting.py` | Stable prefix envelope | canonical JSON |
| `workspace/locality.py` | Locality tiers | workspace graph |
| CLI/MCP + `evals/extras.py` | Surfaces + gates | typer |

---

## Key Decisions

### Decision 1: Ladder floor from risk, never below

| Risk | Level | Command shape |
|------|-------|---------------|
| micro | V1 contract | `apiforge diff contract` / schema validation only |
| low | V2 targeted unit | `pytest <selected>` |
| medium | V4 impacted regression | `pytest <selected> <module dirs>` |
| high | V5 full suite | `pytest` |

A breaking contract verdict (when base/candidate contracts are passed) raises the level to ≥ V4. Empty selection at V2/V4 escalates to V5 with reason `no-impacted-tests-found` — never "nothing to run".

### Decision 2: Retrieval signals are explicit

Every passage carries `signals {heading_hits, body_hits, selected_pack, stale}` and `score`; ties by pack then heading. Tier 1 = top 3, tier 2 = top 5, tier 3 = up to 20; `next_tier` says whether more exists.

### Decision 3: `evidence://` is one hop

Resolver returns the node and neighbor refs only. `operation` ↔ `fact` (implemented_by), `finding` → `fact` (backed_by), `finding` → `rule` (violates).

### Decision 4: Tiers are decisions with reasons

T0 when the capability has a deterministic implementation declared in `providers.yaml` (`deterministic_capabilities`); T3 when risk is high/critical; T1 only if a fresh scorecard for the family passes the quality floor with a T1 provider; otherwise T2 with `no benchmark evidence for a cheaper tier`.

### Decision 5: Prefix excludes anything run-specific

Prefix = canonical JSON of `{protocol: AGENT_PROTOCOL.md sha256 or "unavailable", capability, output_contract, expertise: [pack@version]}`; no timestamps, run ids or paths.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `contracts/economy_extras.py` + registry | Create | Contracts | @python-developer | — |
| 2 | `verification/selection.py` | Create | G1 | @python-developer | 1 |
| 3 | `knowledge/retrieval.py`, `rules/query_expansion.yaml` | Create | G2 | @python-developer | 1 |
| 4 | `evidence/resolve.py` | Create | G3 | @python-developer | 1 |
| 5 | `economy/doctor.py` | Create | G4 | @python-developer | 1 |
| 6 | `economy/providers.py`, `rules/providers.yaml` | Create | G5 | @python-developer | 1 |
| 7 | `runtime/prompting.py`, `runtime/adapters.py`, `runtime/supervisor.py` | Create/Modify | G6 | @python-developer | 1 |
| 8 | `workspace/locality.py` | Create | G7 | @python-developer | 1 |
| 9 | `cli_extras.py`, `cli.py`, `mcp/tools.py` | Create/Modify | Surfaces | @python-developer | 2–8 |
| 10 | `evals/extras.py`, corpus, tests, docs, SDD | Create | G8 | @test-generator | all |

---

## Agent Assignment Rationale

Executed inline.

---

## Code Patterns

```python
LADDER = {"micro": "V1", "low": "V2", "medium": "V4", "high": "V5"}
```

---

## Data Flow

Each verb reads local artifacts (case, cache entries, packs, ledger, rules) and returns a contract; none writes outside `.apiforge/` (ctx store for evidence slices only).

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| None | offline | — |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit + integration | all seven parts | `tests/economy/test_economy_extras.py` | pytest | AT-001–010 |
| Parity | CLI == MCP | same | CliRunner | new verbs |
| Eval | corpus | `evals economy-extras` | CLI | DEFINE criteria |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Unknown risk | `AF-VERIFY-RISK-INVALID` | No |
| Bad evidence ref / missing node | `AF-EVIDENCE-REF-INVALID` / `AF-EVIDENCE-NOT-FOUND` | No |
| Unknown provider/capability | `AF-PROVIDER-UNKNOWN` | No |
| Unknown workspace repo | `AF-WORKSPACE-TARGET-UNKNOWN` | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `rules/query_expansion.yaml` | YAML | shipped | Synonym groups |
| `rules/providers.yaml` | YAML | shipped | Provider descriptors, tier map, deterministic capabilities |

---

## Security Considerations

- Read-only; `verify plan` prints commands, never runs them.

---

## Observability

- Every result names its reasons (selection reasons, ranking signals, tier reason, doctor unlocks).

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | design-agent | Initial version |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_API_FORGE_ECONOMY_EXTRAS.md`
