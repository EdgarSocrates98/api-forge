# BUILD REPORT: Field Integrity Hardening

> Implementation report for Field Integrity Hardening

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | FIELD_INTEGRITY_HARDENING |
| **Date** | 2026-09-28 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_FIELD_INTEGRITY_HARDENING.md](../features/DEFINE_FIELD_INTEGRITY_HARDENING.md) |
| **DESIGN** | [DESIGN_FIELD_INTEGRITY_HARDENING.md](../features/DESIGN_FIELD_INTEGRITY_HARDENING.md) |
| **Status** | ✅ Shipped |
| **Branch** | `sdd/field-integrity` (stacked on `sdd/agent-roster` @ `7dc0322`; field code identical to `origin/main`) |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 23/23 manifest entries (file 10 `field/__init__.py` needed no change) |
| **Files Created** | 5 source/test + 10 SDD artifacts + 1 evidence |
| **Lines of Code** | +573 new files; +416 / −103 in 17 modified files |
| **Build Time** | ~1 session |
| **Tests Passing** | 70 passed / 1 skipped (targeted: `tests/field`, `tests/workspace/test_inference.py`, `tests/mcp/test_tools.py`) |
| **Agents Used** | 0 delegated (all direct, see Autonomous Decision 1) |

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Notes |
|---|------|-------|--------|-------|
| 1 | `contracts/field.py`: ActorRef, VerificationReceipt, FieldCycleIdentity, CoverageGate; FieldRun/Report v2; max_runs 40 | (direct) | ✅ Complete | |
| 2 | `field/errors.py`: 4 AF codes | (direct) | ✅ Complete | |
| 3 | `field/actors.py` | (direct) | ✅ Complete | |
| 4 | `field/identity.py` | (direct) | ✅ Complete | git HEAD read only at seal |
| 5 | `field/readiness.py` | (direct) | ✅ Complete | + `utc_now` clock seam |
| 6 | `field/record.py` | (direct) | ✅ Complete | |
| 7 | `field/annotate.py` | (direct) | ✅ Complete | |
| 8 | `field/report.py` | (direct) | ✅ Complete | |
| 9 | `field/export.py` | (direct) | ✅ Complete | |
| 10 | `field/__init__.py` | (direct) | ✅ No change | public API unchanged |
| 11 | `cli_field.py` | (direct) | ✅ Complete | `--executor`, `--verifier` |
| 12 | `mcp/tools.py` | (direct) | ✅ Complete | `executor`, `verifier` params |
| 13 | `workspace/inference/match.py` | (direct) | ✅ Complete | |
| 14 | `docs/field/corpus.yaml` | (direct) | ✅ Complete | `max_runs: 40` |
| 15 | `docs/field/README.md` | (direct) | ✅ Complete | seal, actors, receipt, statuses |
| 16 | `docs/catalog-contract.md` | (direct) | ✅ Complete | 4 codes |
| 17 | `tests/field/support.py` (+ new `conftest.py`) | (direct) | ✅ Complete | |
| 18 | `tests/field/test_integrity.py` | (direct) | ✅ Complete | 26 tests |
| 19 | `tests/field/test_annotate_report.py` | (direct) | ✅ Complete | |
| 20 | `tests/field/test_record.py` | (direct) | ✅ Complete | |
| 21 | `tests/field/test_export_parity.py` | (direct) | ✅ Complete | +2 refusal parity cases |
| 22 | `tests/workspace/test_inference.py` | (direct) | ✅ Complete | |
| 23 | `docs/sdd/API_FORGE_FIELD_INTEGRITY_HARDENING/` | (direct) | ✅ Complete (through benchmark) | `ship.md` at `/ship` |

---

## Agent Contributions

| Agent | Files | Specialization Applied |
|-------|-------|------------------------|
| (direct) | all | DESIGN patterns + repo conventions (`FieldError`, `VersionedContract`, `write_json`, CLI `_run` / MCP `_call`) |

---

## Files Created

| File | Lines | Agent | Verified | Notes |
| ---- | ----- | ----- | -------- | ----- |
| `src/apiforge/field/actors.py` | 31 | (direct) | ✅ | |
| `src/apiforge/field/identity.py` | 118 | (direct) | ✅ | |
| `src/apiforge/field/readiness.py` | 99 | (direct) | ✅ | |
| `tests/field/test_integrity.py` | 316 | (direct) | ✅ | |
| `tests/field/conftest.py` | 9 | (direct) | ✅ | autouse fixed clock |
| `docs/sdd/API_FORGE_FIELD_INTEGRITY_HARDENING/{discover,intent,contract,architecture,plan,build,verify,secure,benchmark}.md` | — | (direct) | ✅ | stamped hash cascade |
| `docs/sdd/API_FORGE_FIELD_INTEGRITY_HARDENING/evidence/field-tests.txt` | 3 | (direct) | ✅ | |

---

## Verification Results

### Lint Check

```text
ruff check (changed modules + tests): All checks passed!
ruff format: 5 files reformatted, then clean
```

**Status:** ✅ Pass

### Type Check

```text
mypy src/apiforge/field src/apiforge/contracts/field.py src/apiforge/cli_field.py
     src/apiforge/workspace/inference/match.py src/apiforge/mcp/tools.py
Success: no issues found in 15 source files
```

**Status:** ✅ Pass

### Tests

```text
pytest tests/field tests/workspace/test_inference.py tests/mcp/test_tools.py -q
70 passed, 1 skipped in 5.41s
```

**Status:** ✅ 70/70 Pass (1 pre-existing skip). Full suite deferred to `/ship` per project policy (targeted per task, full once before ship).

Full suite at ship: `1 failed, 1344 passed, 1 skipped`. The single failure is `tests/scripts/test_check_release.py::test_release_gate_accepts_complete_repository` flagging the untracked `.claude/agents/README.md` orphan mirror, present before this feature (same pre-existing deviation as `API_FORGE_FIELD_VALIDATION`). Evidence: `docs/sdd/API_FORGE_FIELD_INTEGRITY_HARDENING/evidence/full-suite.txt`.

### SDD gate

```text
apiforge sdd check --root docs/sdd
ok: true after /ship wrote ship.md with stamped evidence hashes
```

---

## Issues Encountered

| # | Issue | Resolution |
|---|-------|------------|
| 1 | Clock time bomb: fixtures use fixed dates (cycle seals at 2026-10-02); CLI/MCP parity tests use the real clock, so after 2026-10-30 every sealed test cycle would be `expired` and `field record` refused | Added `readiness.utc_now()` seam used by `cycle_state` and `verify`; `tests/field/conftest.py` pins it to `NOW` (autouse). Explicit `now=` params kept for direct calls |
| 2 | CRLF test wrote `\r\r\n` on Windows because `write_text` already emits CRLF | Test normalizes to LF first, then checks both LF and CRLF variants; production hashing was correct |
| 3 | Initial max-runs test was self-contradictory: 40 runs without coverage is already `expired`, so the "new baseline beyond max_runs" branch was unreachable there | Rewrote as `test_ready_cycle_at_max_runs_refuses_new_baseline`: ready at 40 runs refuses a new baseline, allows re-recording an existing task |
| 4 | mypy: parenthesized multi-line `schema` literal made `# type: ignore[assignment]` land on the wrong line | Collapsed to single line, matching `BenchmarkIdentity` style |

---

## Autonomous Decisions

| # | Decision Point | Options Considered | Chose | Rationale |
|---|----------------|--------------------|-------|-----------|
| 1 | Delegate to @python-developer / @test-generator / @code-documenter vs build directly | Delegate per manifest vs direct | Direct | Small, tightly coupled change set across contracts, harness and tests; delegation would split shared invariants (digest fields, error codes) across contexts |
| 2 | Branch base | new branch from `origin/main` vs stacked on `sdd/agent-roster` | Stacked `sdd/field-integrity` on `7dc0322` | `sdd/agent-roster` is pushed but unmerged; field code is byte-identical to `origin/main`, catalog already carries the roster section → avoids a docs conflict |
| 3 | Clock seam for CLI/MCP paths | explicit `now` only vs module-level `utc_now` | Both | Explicit param for unit tests, monkeypatchable seam for CLI/MCP parity tests without adding a hidden CLI flag |
| 4 | Keep `# noqa: S603/S607` on git subprocess | keep vs drop | Dropped (ruff `--fix` removed as unused) | Repo ruff config does not enable bandit rules; other `src` modules call `subprocess` without them |
| 5 | Mutated-cycle refusal component for an appended task | `tasks_sha256` vs first differing component | First differing (`corpus_sha256`) | `first_difference` order is deterministic; corpus hash covers tasks, so any task edit reports `cycle.corpus_sha256` |
| 6 | Human id in refusal tests | realistic name vs neutral token | `human:operator-name` | Avoid real personal names in test data |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| `readiness.utc_now()` seam + `tests/field/conftest.py` (not in manifest) | Issue 1 (time bomb) | Tests deterministic regardless of wall clock |
| `compute_identity(..., git_commit=None)` keyword; git read only in `seal` | Avoid a subprocess on every field command | `ensure_cycle` stays pure file hashing |
| HTTP route refs: all matching routes of the callee (Pattern 7 tracked "best score") | Within one callee the score depends only on `call.method`, so every matching route has the same score | Same result, simpler code |
| `verify` imports the `readiness` module (not names) | So the monkeypatched `utc_now` is honored | None |
| `field/__init__.py` unchanged | Public API names unchanged | None |

---

## Blockers (if any)

None.

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|----|----------|--------|----------|
| AT-001 | Seal on first record | ✅ Pass | `test_first_record_seals_cycle` |
| AT-002 | Hypothesis tampered | ✅ Pass | `test_hypothesis_edit_is_mutation`, `test_mutation_blocks_every_command` |
| AT-003 | Corpus backdated / start moved | ✅ Pass | `test_backdated_task_is_mutation`, `test_moved_cycle_start_is_mutation`, `test_gate_edit_is_mutation` |
| AT-004 | Lock deleted | ✅ Pass | `test_missing_lock_is_mutation`, `test_lock_without_cycle_start_is_mutation` |
| AT-005 | CRLF checkout | ✅ Pass | `test_crlf_hypothesis_is_not_mutation` |
| AT-006 | Stale verification | ✅ Pass | `test_annotate_after_verify_is_stale`, `test_rerecord_with_other_runs_is_stale` |
| AT-007 | Re-verify clears stale | ✅ Pass | `test_reverify_clears_stale` |
| AT-008 | Self verification | ✅ Pass | `test_self_verification_refused` |
| AT-009 | Human anonymized id | ✅ Pass | `test_invalid_actor_refused` (6 cases, verify + record) |
| AT-010 | Early stop | ✅ Pass | `test_early_stop_stays_collecting` |
| AT-011 | Ready | ✅ Pass | `test_full_coverage_is_ready` |
| AT-012 | Expired by runs | ✅ Pass | `test_expired_by_runs` |
| AT-013 | Expired by weeks | ✅ Pass | `test_expired_by_weeks` |
| AT-014 | Record after expiry | ✅ Pass | `test_record_after_expiry_refused`, `test_ready_cycle_at_max_runs_refuses_new_baseline` |
| AT-015 | HTTP provenance | ✅ Pass | `test_http_call_infers_edge_with_provenance` (callee `payment-service:` ref) |
| AT-016 | Export | ✅ Pass | `test_export_carries_cycle_status_and_identity` |
| AT-017 | MCP parity | ✅ Pass | `test_cli_and_mcp_refusals_match` (+ NOT-INDEPENDENT, ACTOR-INVALID), `test_cli_and_mcp_report_payloads_match` |

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Report determinism | byte-identical for same records + clock | `test_report_is_byte_deterministic` passes | ✅ |
| Default workspace graph | unchanged without `--infer` | `test_default_graph_has_no_inferred_edges` passes | ✅ |

---

## Next Step

Run the full suite once, then `/agentspec:workflow:ship .claude/sdd/features/DEFINE_FIELD_INTEGRITY_HARDENING.md` (writes `docs/sdd/.../ship.md` and closes the `apiforge sdd check` gap).
