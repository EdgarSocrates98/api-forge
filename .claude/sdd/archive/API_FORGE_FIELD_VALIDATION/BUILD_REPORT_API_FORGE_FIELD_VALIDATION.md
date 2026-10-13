# BUILD REPORT: API Forge Field Validation + System Graph Inference

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_FIELD_VALIDATION |
| **Date** | 2026-09-28 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_API_FORGE_FIELD_VALIDATION.md](../features/DEFINE_API_FORGE_FIELD_VALIDATION.md) |
| **DESIGN** | [DESIGN_API_FORGE_FIELD_VALIDATION.md](../features/DESIGN_API_FORGE_FIELD_VALIDATION.md) |
| **Status** | ✅ Shipped |
| **Branch** | `sdd/new-forge` (uncommitted) |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 38/38 manifest entries (1 partially deferred: gRPC stubs, see Deviations) |
| **Files Created** | 29 (13 src, 6 tests, 5 docs/field, 11 docs/sdd incl. evidence, 1 report) |
| **Lines of Code** | ~1,530 src + ~740 tests |
| **Tests Passing** | targeted 170 passed / 1 skipped; full suite 1284 passed, 1 skipped, 1 failed (pre-existing, see Issues #6) |
| **Agents Used** | 1 (direct) — see Autonomous Decisions #1 |

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Notes |
|---|------|-------|--------|-------|
| 1 | `contracts/field.py` | (direct) | ✅ | Corpus, FieldRun, FieldReport, enums |
| 2–9 | `field/{errors,store,corpus,record,annotate,report,export,__init__}.py` | (direct) | ✅ | Join-never-collect; Wilson CI |
| 10–11 | `cli_field.py` + registration in `cli.py` | (direct) | ✅ | `apiforge field record\|annotate\|verify\|report\|export` |
| 12–13 | MCP parity (`mcp/tools.py`, TOOLS list) | (direct) | ✅ | `field_record/annotate/verify/report`, `workspace_graph`; surface derives from TOOLS |
| 14 | `adapters/http_targets.py` | (direct) | ✅ | requests/httpx/axios/fetch/RestTemplate/WebClient/Go net/http |
| 15–16 | `workspace/inference/{__init__,match}.py` | (direct) | ✅ | HTTP + topic matching, ambiguity cap 0.45 |
| 17–19 | `RelationKind`, `graph.py`, `service.py`, `application/workspace.py`, `cli_workspace.py` | (direct) | ✅ | `workspace graph [--infer --run-id]`, audited ledger row |
| 20 | `docs/catalog-contract.md` | (direct) | ✅ | 8 `AF-FIELD-*` + 3 `AF-WORKSPACE-INFER-*` |
| 21–24 | `docs/field/{corpus.yaml,hypothesis.md,README.md,ground-truth/otel-demo-relations.yaml}` | (direct) | ✅ | Ground truth is a draft (UNPINNED) |
| 25 | `.gitignore` | (direct) | ✅ | `docs/field/repos.local.yaml` |
| 26–36 | tests | (direct) | ✅ | Fixtures built in `tests/field/support.py` instead of static fixture dirs |
| 37 | `docs/sdd/API_FORGE_FIELD_VALIDATION/*` | (direct) | ✅ | Profile `critical` from `sdd classify` (risk high) |
| 38 | Routing: `CLAUDE.md`, `.claude/skills/api-forge-sdd/SKILL.md`, `README.md` | (direct) | ✅ | |

---

## Agent Contributions

| Agent | Files | Specialization Applied |
|-------|-------|------------------------|
| (direct) | all | DESIGN patterns + repo conventions (`EconomyError`, `cli_economy.py`, `_call`) |

---

## Verification Results

### Lint Check

`ruff check src tests/field tests/workspace` → All checks passed. `ruff format --check` → 462 files already formatted.

### Type Check

`mypy src` → Success: no issues found in 452 source files.

### Tests

| Test | Covers | Result |
|------|--------|--------|
| `tests/field/test_record.py` | AT-001, AT-002, AT-003, AT-006, AT-010, time window, corpus validation, repo template | ✅ |
| `tests/field/test_annotate_report.py` | AT-004, AT-005, AT-007, AT-008, AT-009, AT-015, Wilson values | ✅ |
| `tests/field/test_export_parity.py` | AT-016, CLI↔MCP refusal parity (code/field/unlock), report payload parity | ✅ |
| `tests/workspace/test_inference.py` | AT-011, AT-012, AT-013, AT-014, extractor variants, CLI audit → contamination e2e | ✅ |
| `tests/mcp/test_tools.py` | TOOLS set updated with 5 new verbs | ✅ |
| Full suite | regression | ⚠️ 1284 passed, 1 failed: release gate flags pre-existing untracked `.claude/agents/README.md` orphan mirror |

---

## Issues Encountered

| # | Issue | Resolution |
|---|-------|------------|
| 1 | Ledger rows carry no timestamp → DESIGN D2 window check against ledger impossible | Window and `time_to_evidence` use `economy_checkpoint.updated_at` instead (Deviation 1) |
| 2 | RestTemplate `postForObject` produced method `POSTFOROBJECT` | Map method names by HTTP-verb prefix; test updated |
| 3 | Two wrong test expectations (Wilson upper bound, scenario minimum) | Fixed tests; code was right (Wilson(8,30) = 0.1418–0.4445) |
| 4 | Python-scripted edits wrote CRLF on Windows | Normalized all touched files to LF |
| 5 | `pytest -n` unavailable (no xdist) | Full suite run serially |
| 6 | `test_release_gate_accepts_complete_repository` fails: `agent mirror drift: .claude/agents/README.md (orphan)` | Not introduced: file was untracked before this session and was not touched. Owner decides: delete, commit as mirror, or exempt |
| 7 | `sdd check` evidence hash mismatch (CRLF in pytest output) | Normalized evidence to LF, hashes via `text_sha256`; `sdd check` ok |

---

## Autonomous Decisions

| # | Decision Point | Options Considered | Chose | Rationale |
|---|----------------|--------------------|-------|-----------|
| 1 | Delegate files to @python-developer/@test-generator/@code-documenter | Delegate vs direct | Direct | Tightly coupled contracts across 13 src files; repo-specific conventions (refusal shape, `_call`, ledger) easier to keep consistent in one thread |
| 2 | Source of `time_to_evidence` and window check | Ledger rows (no timestamp) vs checkpoint `updated_at` vs null | Checkpoint `updated_at` | Only persisted timestamp per run; null + `evidence_timestamp_missing` when absent |
| 3 | Unknown run id | Always null vs refuse | Refuse `AF-FIELD-RUN-MISSING` only when neither run dir nor ledger rows exist | A typo must not create a silently empty record; partial evidence still records with nulls (AT-010) |
| 4 | Where inference is reachable | CLI flag only vs flag + MCP | Both (`workspace graph --infer`, `workspace_graph(infer=True)`) | Parity rule; both paths write the same audited ledger row |
| 5 | Inference without `--run-id` | Refuse vs allow + unresolved | Allow + `AF-WORKSPACE-INFER-UNATTRIBUTED` | Exploration outside a field run is legitimate; the gap is visible, not hidden |
| 6 | `mark_cycle_started` rewrites `corpus.yaml` | Preserve comments (ruamel) vs `yaml.safe_dump` | `safe_dump` | No new dependency; corpus template has no comments |
| 7 | Topic producer/consumer role | Per-fact vs per-file operation | Per-file operation facts (`data.streaming.operation`) | Existing streaming facts do not link topic to operation; same-file co-occurrence is the smallest honest signal |
| 8 | SQS/SNS/EventBridge destinations | Include vs defer | Defer | Out of DESIGN scope; streaming brokers only |
| 9 | Test fixtures | Static dirs vs builders | Builders in `tests/field/support.py` and inline mini repos | Timestamps and ledger rows vary per test |
| 10 | `field export` over MCP | Add vs CLI-only | CLI-only | DESIGN lists four MCP field tools; export writes files into the repo tree |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| D2 window/`time_to_evidence` from checkpoint, not ledger | Ledger rows have no timestamps | Runs without checkpoint → `time_to_evidence` null + unresolved |
| gRPC stub extraction not implemented | Scope held to HTTP + topics; no fixture evidence yet | OpenTelemetry Demo is mostly gRPC → recall gate (≥0.60) likely fails until measured; recorded in ground-truth file and ship deviations |
| Ground-truth relations are a draft, commit UNPINNED | Demo not cloned in this build | Must be pinned and re-checked before tuning inference |
| `docs/field/corpus.yaml` has zero tasks and no own repos | Owner has not named repos | Cycle cannot start until tasks are registered |

---

## Unresolved (carried to ship)

- Corpus repos (own + OSS beyond OTel Demo) unnamed.
- Arazzo 1.1 / OpenAPI 3.2.1 / Overlay 1.1 / AsyncAPI 3.1 versions unverified (no primary source).
- gRPC inference recall on OTel Demo.

---

## Next Step

`/ship .claude/sdd/features/DEFINE_API_FORGE_FIELD_VALIDATION.md`

---

*Shipped and archived 2026-09-28.*
