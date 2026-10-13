# DEFINE: API Forge Economy — Verification, Retrieval, Evidence and Providers (Onda 7)

> Stop defaulting to "everything": targeted verification, locality-first workspaces, an economy doctor, ranked progressive retrieval, one-hop evidence, declared provider tiers and a stable prompt prefix.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_EXTRAS |
| **Date** | 2026-09-28 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 13/15 |
| **Source** | `.claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_EXTRAS.md` |

---

## Problem Statement

After waves 0–6, verification still means "the whole suite", workspaces have no locality order, nothing diagnoses economy misconfiguration, knowledge is delivered by whole pack, evidence chains are not addressable one hop at a time, provider choice is implicit and prompts carry no stable prefix for provider caching.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| CI / maintainer | Verifies changes | Full suites for one-field changes |
| Agent host | Reads knowledge/evidence | Whole packs and chains |
| Operator | Configures economy | No diagnosis; implicit model choice |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | G1: `verify plan --changed F… [--risk R]` → `VerificationPlan/v1`: ladder V0–V5 by risk, selected tests with reasons (cached test refs, symbol/import mentions, delta targets), commands; never executes (§45–46) |
| **MUST** | G2: `knowledge search --query Q [--tier 1|2|3]` → `RetrievalResult/v1`: deterministic query expansion (`rules/query_expansion.yaml`), passage ranking with explicit signals, progressive tiers top-3 → top-5 → rest (§56–58) |
| **MUST** | G3: `evidence resolve evidence://<kind>/<id>` → `EvidenceNode/v1`: node, one-hop neighbors (as further `evidence://` refs), source ctx ref (§60) |
| **MUST** | G4: `economy doctor` (and `apiforge doctor --economy`) → `EconomyDoctor/v1` findings with code, severity, detail, unlock (§55) |
| **SHOULD** | G5: `rules/providers.yaml` + `economy providers` and `economy tier --capability C --risk R` → `ProviderCapability/v1`, `TierDecision/v1` (T0–T3); no benchmark evidence → no downgrade (§61–63) |
| **SHOULD** | G6: `PromptEnvelope/v1` with stable prefix (protocol, capability contract, expertise versions) + dynamic suffix; `AgentRequest.prompt_prefix_sha256`; `agentops prompt` renders it (§81–83) |
| **SHOULD** | G7: `workspace locality --target <repo>` → tiers target → direct → transitive(deferred unless `--transitive`) (§48–49) |
| **SHOULD** | G8: `evals economy-extras` corpus + gates |

---

## Success Criteria

- [ ] Test selection recall 1.0 on corpus cases, selecting fewer tests than the full set where the change is local.
- [ ] Retrieval: expected passage in tier-1 (top 3) for every corpus query; expansion adds ≥ 1 term for ≥ 1 query.
- [ ] `evidence://` resolves finding/fact/rule/operation with one-hop neighbors only.
- [ ] Doctor flags at least: cache disabled, deep default profile, capsule never used, stale packs.
- [ ] Tier: risk high → T3; deterministic capability → T0; no evidence → T2 (no downgrade).
- [ ] Prefix sha identical for the same capability across two tasks; different across capabilities.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Local change | handler file changed, risk low | `verify plan` | V2, only tests mentioning the handler |
| AT-002 | Breaking/high | risk high | `verify plan` | V5 full suite, reason recorded |
| AT-003 | Retrieval | "breaking endpoint" | search | expansion adds compatibility/versioning; expected passage top 3 |
| AT-004 | Progressive | tier 1 | search | 3 passages + `next_tier` hint |
| AT-005 | Evidence | finding id | resolve | finding, backing facts, rule as refs |
| AT-006 | Bad ref | `evidence://nope/x` | resolve | `AF-EVIDENCE-REF-INVALID` |
| AT-007 | Doctor | APIFORGE_CACHE=off | doctor | `AF-ECONOMY-DOCTOR-CACHE-OFF` finding |
| AT-008 | Tier | capability with no scorecard | tier | T2, reason `no benchmark evidence` |
| AT-009 | Prefix | two tasks, same capability | envelope | same prefix sha |
| AT-010 | Locality | workspace with deps | locality | ordered tiers; transitive deferred |

---

## Out of Scope

- Executing tests; embeddings; running local models; provider cache-control headers.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Offline, read-only | Plans, not execution |
| Technical | AF codes cataloged | New `AF-VERIFY-*`, `AF-EVIDENCE-*`, `AF-ECONOMY-DOCTOR-*`, `AF-PROVIDER-*` |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/{verification/selection.py,knowledge/retrieval.py,evidence/resolve.py,economy/doctor.py,economy/providers.py,runtime/prompting.py,workspace/locality.py}` | Additive |
| **KB Domains** | testing | — |
| **IaC Impact** | None | — |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Pack markdown has `##` sections | Coarse passages | [ ] build |
| A-002 | Workspace relations include `depends_on` | Locality flat | [x] `WorkspaceRelation` |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | |
| Users | 3 | |
| Goals | 3 | |
| Success | 2 | breadth across seven parts |
| Scope | 2 | |
| **Total** | **13/15** | |

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | define-agent | Initial version |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_API_FORGE_ECONOMY_EXTRAS.md`
