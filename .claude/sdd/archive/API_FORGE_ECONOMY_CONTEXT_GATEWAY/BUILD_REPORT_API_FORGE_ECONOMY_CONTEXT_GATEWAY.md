# BUILD REPORT: API Forge Economy — Context Gateway (P0)

> Implementation report for API_FORGE_ECONOMY_CONTEXT_GATEWAY

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_CONTEXT_GATEWAY |
| **Date** | 2026-09-27 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_API_FORGE_ECONOMY_CONTEXT_GATEWAY.md](../features/DEFINE_API_FORGE_ECONOMY_CONTEXT_GATEWAY.md) |
| **DESIGN** | [DESIGN_API_FORGE_ECONOMY_CONTEXT_GATEWAY.md](../features/DESIGN_API_FORGE_ECONOMY_CONTEXT_GATEWAY.md) |
| **Status** | ✅ Shipped |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 30/30 manifest entries |
| **Files Created** | 49 new (incl. 12 corpus cases, fixture, 7 contract docs, 10 SDD docs) + 14 modified |
| **Lines of Code** | ~1,600 new in `src/` (gateway, ledger, eval, contracts, CLI) |
| **Build Time** | 1 session |
| **Tests Passing** | 1055/1056 full suite (1 skipped); the 1 failure is a pre-existing orphan file, see Blockers |
| **Agents Used** | 0 delegated (see Autonomous Decisions #1) |

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Duration | Notes |
|---|------|-------|--------|----------|-------|
| 1–4 | Contracts `ContextRef/CapsuleBudget/CapsuleRefusal/ContextCapsule`, `CostVector/LedgerRef/RunLedgerEntry`, registry, exports | (direct) | ✅ Complete | - | 7 contracts registered |
| 5–10 | `context/gateway/` canonical, errors, refs, dedup, levels, capsule | (direct) | ✅ Complete | - | Selection from case graph |
| 11 | `economy/run_ledger.py` append/stats/explain | (direct) | ✅ Complete | - | Superset rows, `payload_bytes: 0` |
| 12–16 | App facade, CLI (`context capsule/expand`, `economy stats/explain`, `evals economy`), MCP tools | (direct) | ✅ Complete | - | CLI↔MCP parity tested |
| 17–19 | `evals/economy.py`, 12-case corpus, `baseline.json` | (direct) | ✅ Complete | - | Gates pass |
| 20 | AF catalog (9 codes) | (direct) | ✅ Complete | - | |
| 21–27 | Tests (contracts, canonical, refs, capsule, ledger, eval, MCP) | (direct) | ✅ Complete | - | 55 targeted |
| 28 | SDD chain `docs/sdd/API_FORGE_ECONOMY_CONTEXT_GATEWAY` | (direct) | ✅ Complete | - | `sdd check` ok |
| 29 | `api-forge-context` skill + 3 host mirrors | (direct) | ✅ Complete | - | Identical copies |
| 30 | README verbs | (direct) | ✅ Complete | - | |
| + | `docs/contracts/*-v1.md` for 7 contracts | (direct) | ✅ Complete | - | Required by release gate, missing from DESIGN manifest |

---

## Agent Contributions

| Agent | Files | Specialization Applied |
|-------|-------|------------------------|
| (direct) | all | DESIGN patterns + KB pydantic/testing; repo conventions (`VersionedContract`, `_run` refusals, `_call` MCP) |

---

## Files Created

| File | Verified | Notes |
| ---- | -------- | ----- |
| `src/apiforge/contracts/economy.py` | ✅ | CostVector, LedgerRef, RunLedgerEntry |
| `src/apiforge/context/gateway/{__init__,canonical,errors,refs,dedup,levels,capsule}.py` | ✅ | Gateway |
| `src/apiforge/economy/run_ledger.py` | ✅ | Attribution |
| `src/apiforge/evals/economy.py` | ✅ | Benchmark |
| `src/apiforge/cli_economy.py` | ✅ | stats/explain |
| `evals/corpus/economy/*.yaml` (12), `baseline.json`, `README.md` | ✅ | Ground truth |
| `tests/fixtures/economy_payments/**` | ✅ | New fixture (deviation) |
| `tests/context/*`, `tests/contracts/test_context_capsule.py`, `tests/economy/test_run_ledger.py`, `tests/evals/test_economy_eval.py`, `tests/mcp/test_economy_context_tools.py` | ✅ | |
| `docs/contracts/{ContextCapsule,ContextRef,CapsuleBudget,CapsuleRefusal,CostVector,LedgerRef,RunLedgerEntry}-v1.md` | ✅ | |
| `docs/sdd/API_FORGE_ECONOMY_CONTEXT_GATEWAY/*` | ✅ | 10 phases + evidence |

Modified: `contracts/{context,registry,__init__}.py`, `application/context.py`, `cli.py`, `cli_context.py`, `mcp/tools.py`, `tests/mcp/test_tools.py`, `docs/catalog-contract.md`, `README.md`, 4× `api-forge-context/SKILL.md`.

---

## Verification Results

### Lint Check

```text
ruff check src tests      -> All checks passed!
ruff format --check src tests -> 711 files already formatted
```

**Status:** ✅ Pass

### Type Check

```text
mypy src/apiforge (strict) -> Success: no issues found in 379 source files
```

**Status:** ✅ Pass

### Tests

```text
Full suite (run once, at the end): 1055 passed, 1 skipped, 1 failed
  FAILED tests/scripts/test_check_release.py::test_release_gate_accepts_complete_repository
    -> only remaining item: "agent mirror drift: .claude/agents/README.md (orphan)"
Targeted feature tests: 55 passed, 1 skipped
apiforge sdd check --root docs/sdd -> ok: true, refused: [], unresolved: []
apiforge evals economy -> passed: true, median_reduction 0.477
```

**Status:** ✅ Feature green | ❌ 1 pre-existing repo failure (not introduced by this feature)

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | Case graph keys one route fact per `(method, path)`; FastAPI fixture had two `POST /orders` handlers | Also match `code.route` facts directly; provenance `fact-match:code.route:<id>` | small |
| 2 | Absolute `scope.root` made capsules machine-dependent | Capsule scope root is `.`; fingerprint paths root-relative | small |
| 3 | Partial capsule exceeded its own budget (refusal bytes) | Fixed 320-byte refusal reserve | small |
| 4 | Java brace matching fooled by `{payment_id}` inside annotations | Strip string literals/`//` comments before counting braces | small |
| 5 | `fastapi_orders` mounts routes under `/v1` while `orders-v1.yaml` declares `/orders` (real drift) | Capsule now emits `unresolved: code-route-missing:<op>`; corpus uses `fastapi_orders_complete` + `orders-v1-complete` | small |
| 6 | Pytest temp dir under system Temp denied; under repo, `test_create_refuses_non_git` sees a git repo | Full suite ran with `--basetemp` in the session scratchpad (outside the repo) | none |
| 7 | Release gate requires `docs/contracts/<Name>-v1.md` per contract | Added 7 docs | small |
| 8 | Python `write_text` produced CRLF on Windows | Normalized all touched files to LF | none |

---

## Autonomous Decisions

| # | Decision Point | Options Considered | Chose | Rationale |
|---|----------------|--------------------|-------|-----------|
| 1 | Delegate files to manifest agents | Per-file subagents vs direct | Direct | Tightly coupled modules; delegation would multiply context cost without new capability |
| 2 | Graph source for L2 | Workspace graph vs case graph | Case graph (`build_graph` → `.apiforge/ctx/graph/<case>`) | Only the case graph has operation → route fact → finding edges |
| 3 | `run_id` default | Random per call vs deterministic | `run-<capsule hash tail>` | Keeps capsule byte-identical (SC4); repeated identical builds accumulate real spend under one run |
| 4 | Ledger double counting | Rows with bytes vs `payload_bytes: 0` | `payload_bytes: 0` attribution rows | Verb row already records transport bytes; `economy report` totals unchanged (AT-009) |
| 5 | Benchmark capsule charge | Capsule only vs capsule + expansion | Capsule + full expansion of every ref | Conservative; no credit for refs an agent might skip |
| 6 | L3 vs L4 meaning | — | L3 pointers only; L4 inlines code `excerpt` | Clear, measurable difference inside the budget |
| 7 | New `envelope` ledger source | Force envelope into `graph` vs dedicated source | `envelope` | SC6 needs 100% attribution without mislabeling framing bytes |
| 8 | Extra refusal codes | Reuse vs new | `AF-CONTEXT-TARGET-INVALID`, `AF-CTX-REF-INVALID`, `AF-EVALS-ECONOMY-BASELINE-{MISSING,STALE}` | Distinct fields/unlocks; all cataloged |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| New fixture `tests/fixtures/economy_payments` (FastAPI + Spring, DTOs, tests) | Existing fixtures have no DTOs/tests, so dedup (AT-008) and test selection could not be exercised | 6 of 12 cases use it; `conftest.py` keeps its tests out of collection |
| Corpus has no gRPC case | `analyze` builds the case graph from OpenAPI only | gRPC capsules unresolved; recorded in `ship.md` |
| L1 fingerprint from `case.json`, not `ContextService` | `ContextService` has no operation-level data; it is used only for the degraded (no case) path | None functionally |
| `docs/contracts/*-v1.md` added | Release gate requirement not in manifest | +7 docs |

---

## Blockers (if any)

| Blocker | Required Action | Owner |
|---------|-----------------|-------|
| `tests/scripts/test_check_release.py` fails on `.claude/agents/README.md (orphan)` — file was untracked before this build | Commit it with its mirrors, or remove it | Repository owner |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|----|----------|--------|----------|
| AT-001 | Capsule happy path | ✅ Pass | `test_capsule_selects_operation_schemas_handler_and_tests` |
| AT-002 | Expand verified | ✅ Pass | `test_expand_returns_verified_content`, `test_put_then_get_round_trips_with_verification` |
| AT-003 | Hash tampered | ✅ Pass | `test_tampered_object_is_refused_without_content` |
| AT-004 | Ref missing | ✅ Pass | `test_missing_object_is_refused`, CLI `test_cli_refusals_keep_code_field_and_unlock` |
| AT-005 | Budget exhausted | ✅ Pass | `test_budget_exhaustion_returns_whole_refs_and_refusal` |
| AT-006 | Graph unavailable | ✅ Pass | `test_missing_case_degrades_explicitly`, `test_degraded_capsule_exits_zero_with_explicit_status` |
| AT-007 | Canonical | ✅ Pass | `test_capsule_is_byte_identical_across_builds`, `test_crlf_and_lf_content_share_one_uri`, eval `deterministic` 12/12 |
| AT-008 | Dedup | ✅ Pass | `test_schema_is_carried_once_and_code_model_as_delta` |
| AT-009 | Legacy ledger | ✅ Pass | `test_attribution_rows_leave_legacy_report_unchanged`, `test_stats_reads_legacy_rows_into_their_own_bucket`, existing `tests/economy/test_report.py` |
| AT-010 | Tokens unresolved | ✅ Pass | `test_tokens_stay_unresolved_without_observed_usage` |
| AT-011 | Explain | ✅ Pass | `test_explain_names_the_rule_behind_each_ref` |
| AT-012 | Benchmark | ✅ Pass | `tests/evals/test_economy_eval.py` + `apiforge evals economy` (exit 1 on gate failure) |
| AT-013 | MCP parity | ✅ Pass | `test_capsule_payload_is_identical_on_cli_and_mcp`, `test_expand_stats_and_explain_round_trip` |

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| SC1 baseline recorded | 12/12 | 12/12 (`evals/corpus/economy/baseline.json`) | ✅ |
| SC2 recall ≥ baseline | 12/12 | 12/12 at 1.0 | ✅ |
| SC3 median reduction | ≥ 40% | 47.7% (min 39.1%, max 55.4%), charging full expansion | ✅ |
| SC4 byte-identical | 100% | 100% | ✅ |
| SC5 tokens only observed | 100% unresolved without transcript | yes | ✅ |
| SC6 bytes attributed to a source | 100% | yes (`envelope` covers framing) | ✅ |
| SC7 new AF codes cataloged | ≥ 4 | 9 | ✅ |
| SC8 full suite + sdd check | green | sdd check ok; suite 1 pre-existing failure | ⚠️ |

Per-case minimum (39.1%, `fastapi-payments-create`) is below 40%; the gate is on the median as defined in DEFINE.

---

## Final Status

### Overall: ✅ COMPLETE (with one pre-existing repository blocker)

**Completion Checklist:**

- [x] All tasks from manifest completed
- [x] All verification checks pass (lint, types, feature tests, sdd check, economy eval)
- [ ] All tests pass — 1 pre-existing release-gate failure (orphan `.claude/agents/README.md`)
- [x] No blocking issues introduced by this feature
- [x] Acceptance tests verified
- [x] Ready for /ship once the orphan file is resolved

---

## Next Step

**If Complete:** `/agentspec:workflow:ship .claude/sdd/features/DEFINE_API_FORGE_ECONOMY_CONTEXT_GATEWAY.md`
