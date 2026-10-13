# BUILD REPORT: API Forge Economy — Cache & Incremental Intelligence (Onda 2)

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_CACHE_INCREMENTAL |
| **Date** | 2026-09-28 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_API_FORGE_ECONOMY_CACHE_INCREMENTAL.md](./DEFINE_API_FORGE_ECONOMY_CACHE_INCREMENTAL.md) |
| **DESIGN** | [DESIGN_API_FORGE_ECONOMY_CACHE_INCREMENTAL.md](./DESIGN_API_FORGE_ECONOMY_CACHE_INCREMENTAL.md) |
| **Status** | ✅ Shipped |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 13/13 |
| **Files Created** | 24 |
| **Files Modified** | 16 |
| **Tests** | 141 passed, 1 skipped (targeted) |
| **Eval** | `evals cache` 10/10 cases, all 6 gates pass |

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Notes |
|---|------|-------|--------|-------|
| 1 | `contracts/cache.py` + registry | (direct) | ✅ | CacheDep/CacheEntry/CacheDecision/DeltaSlice |
| 2 | `rules/cache_policies.yaml` + `cache/policy.py` | (direct) | ✅ | 8 layers; 4 enabled |
| 3 | `cache/{freshness,store,errors}.py` | (direct) | ✅ | local + opt-in shared tier |
| 4 | `gateway/selection_cache.py` | (direct) | ✅ | span / pointer / neighborhood / symbol probes |
| 5 | `levels.py` L2 content key + L3 impact memo | (direct) | ✅ | fixes case_id-only graph key |
| 6 | `capsule.py` L4 lookup + ledger `cache_hits` | (direct) | ✅ | `on_decision` callback |
| 7 | `context/delta.py` | (direct) | ✅ | argv git; contract subtree + $ref closure diff |
| 8 | CLI (`cache`, `context delta|gc`, `--no-cache`, `evals cache`) | (direct) | ✅ | |
| 9 | MCP parity (4 tools + capsule flags) | (direct) | ✅ | |
| 10 | `evals/cache.py` + 10-case corpus | (direct) | ✅ | |
| 11 | Tests | (direct) | ✅ | 3 new modules |
| 12 | Docs + catalog + release prefixes + skill mirrors | (direct) | ✅ | AF-CACHE/AF-DELTA gated |
| 13 | SDD chain `docs/sdd/API_FORGE_ECONOMY_CACHE_INCREMENTAL` | (direct) | ✅ | `sdd check` ok |

---

## Agent Contributions

| Agent | Files | Specialization Applied |
|-------|-------|------------------------|
| (direct) | 40 | Small coupled surface; executed inline per DESIGN rationale |

---

## Files Created

| File | Lines | Agent | Verified | Notes |
|------|-------|-------|----------|-------|
| `src/apiforge/contracts/cache.py` | ~110 | (direct) | ✅ | |
| `src/apiforge/cache/{__init__,errors,policy,freshness,store}.py` | ~560 | (direct) | ✅ | |
| `src/apiforge/rules/cache_policies.yaml` | 17 | (direct) | ✅ | |
| `src/apiforge/context/gateway/selection_cache.py` | ~360 | (direct) | ✅ | |
| `src/apiforge/context/delta.py` | ~300 | (direct) | ✅ | |
| `src/apiforge/application/cache.py`, `src/apiforge/cli_cache.py` | ~190 | (direct) | ✅ | |
| `src/apiforge/evals/cache.py`, `evals/corpus/economy-cache/*` | ~210 + 11 | (direct) | ✅ | |
| `tests/cache/test_cache_store.py`, `tests/context/test_capsule_cache.py`, `tests/mcp/test_cache_tools.py` | ~370 | (direct) | ✅ | |
| `docs/contracts/{CacheDep,CacheEntry,CacheDecision,DeltaSlice}-v1.md` | — | (direct) | ✅ | |

---

## Verification Results

### Lint Check

```text
ruff check + ruff format on all touched files: clean
```

### Type Check

```text
mypy src/apiforge: Success: no issues found in 393 source files
```

### Tests

| Test | Result |
|------|--------|
| `tests/cache` | ✅ 9 |
| `tests/context` (incl. `test_capsule_cache.py`) | ✅ |
| `tests/mcp/test_cache_tools.py`, `test_tools.py`, `test_economy_context_tools.py` | ✅ |
| `tests/economy`, `tests/contracts` | ✅ |
| **Total targeted** | **141 passed, 1 skipped** |

Full suite deferred to the end of the program (all waves), per project practice.

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | Import cycle cache ↔ gateway package | `cache/errors.py` + local hashing in `store.py` | small |
| 2 | Whole-file deps invalidated every capsule on any contract/models edit | Span deps for code slices, JSON-pointer deps for contract operation + schemas | precision 1.0 |
| 3 | Mention-based symbol scan too coarse (Java field types) | Model *definitions* outside the recorded span + handler mentions in test files only | precision 1.0 |
| 4 | `diff_contracts` does not classify `operationId` | Delta compares operation subtree + `$ref` closure directly | test added |
| 5 | Shell heredocs mangled backslash escapes | Edits with backslashes done via editor tool | none |

---

## Autonomous Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Cache the selection, not the capsule | Fingerprint embeds case id; recomposition keeps bytes identical |
| 2 | Keep `context delta` file-level | Pre-change planning must over- rather than under-approximate; cache probes are the precise layer |
| 3 | `described_by` edges excluded from neighborhood | Contract node id embeds whole-file hash; pointer deps cover contract evidence |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| `CacheDep` gained `span` and `pointers` | Precision gate failed with whole-file deps | Contract doc updated |
| Delta contract diff not via `openapi.diff` | Unclassified fields (operationId) produced empty deltas | More complete, still deterministic |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|----|----------|--------|----------|
| AT-001 | Warm hit | ✅ | `test_warm_rebuild_is_a_hit_with_identical_bytes` |
| AT-002 | Graph freshness | ✅ | `test_graph_key_follows_case_content_not_case_id` |
| AT-003 | Precise invalidation | ✅ | `test_handler_edit_invalidates_only_its_operation`, `test_delta_invalidate_drops_only_dependent_selections` |
| AT-004 | Stale critical | ✅ | `test_freshness_states_cover_fresh_invalidated_and_both_stale_policies` |
| AT-005 | Stale harmless | ✅ | same |
| AT-006 | Delta git | ✅ | `test_delta_from_git_classifies_contract_edit` |
| AT-007 | Delta no git | ✅ | `test_delta_refusals_carry_field_and_unlock` |
| AT-008 | Corrupt entry | ✅ | `test_store_round_trip_invalidate_and_corrupt_reads_recompute`, `test_tampered_object_is_never_returned` |
| AT-009 | Shared tier | ✅ | `test_shared_tier_serves_a_second_root_and_copies_locally` |
| AT-010 | gc | ✅ | `test_gc_reports_by_default_and_deletes_only_with_apply` |
| AT-011 | L8 disabled | ✅ | `test_disabled_and_unknown_layers_refuse_with_field_and_unlock` |

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Warm hit rate | 1.0 | 1.0 (10/10 cases) | ✅ |
| Stale reuse | 0 | 0 | ✅ |
| Invalidation precision / recall | 1.0 / 1.0 | 1.0 / 1.0 | ✅ |
| Hit latency on the small fixture | lower | ~30% lower per capsule | ✅ (fixture is tiny; savings scale with project size) |

---

## Final Status

### Overall: ✅ COMPLETE

**Completion Checklist:**

- [x] All tasks from manifest completed
- [x] All verification checks pass (targeted)
- [x] Acceptance tests verified
- [x] Build report generated
- [ ] Full suite — deferred to program end

---

## Next Step

**Ready for:** `/ship .claude/sdd/features/DEFINE_API_FORGE_ECONOMY_CACHE_INCREMENTAL.md`
