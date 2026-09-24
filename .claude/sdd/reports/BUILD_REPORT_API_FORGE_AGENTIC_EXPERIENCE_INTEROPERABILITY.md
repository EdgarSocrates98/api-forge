# BUILD REPORT: API Forge Agentic Experience and Interoperability

> Implementation report for the TUI-first deferred evolution program.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_AGENTIC_EXPERIENCE_INTEROPERABILITY |
| **Date** | 2026-09-23 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_API_FORGE_AGENTIC_EXPERIENCE_INTEROPERABILITY.md](../features/DEFINE_API_FORGE_AGENTIC_EXPERIENCE_INTEROPERABILITY.md) |
| **DESIGN** | [DESIGN_API_FORGE_AGENTIC_EXPERIENCE_INTEROPERABILITY.md](../features/DESIGN_API_FORGE_AGENTIC_EXPERIENCE_INTEROPERABILITY.md) |
| **Status** | Complete |

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 34/34 manifest tasks, plus CLI and receipt enhancements |
| **Files Created/Modified** | 93 worktree files including the preceding kernel closure and vendor hygiene changes |
| **Tests Passing** | 866 passed, 1 skipped |
| **Agents Used** | Direct build with the DESIGN assignments and KB patterns |
| **Build Time** | Interactive session; not instrumented |

## Task Execution

| # | Task | Agent | Status | Notes |
|---|------|-------|--------|-------|
| 1 | Evidence, experience, knowledge, host, compatibility and debate contracts | (direct) | ✅ Complete | Pydantic v1 contracts are additive and closed |
| 2 | Canonical application projection | (direct) | ✅ Complete | JSON, CLI, Rich and TUI consume the same snapshot |
| 3 | Textual UX and Rich/JSON fallback | (direct) | ✅ Complete | Execution-first screen, governance/evidence/debate navigation and eight key flows |
| 4 | Knowledge freshness and read-only receipt verification | (direct) | ✅ Complete | Fresh, stale, unresolved and unknown states are explicit |
| 5 | Four-host capability negotiation | (direct) | ✅ Complete | Static fallback plus `.apiforge/hosts/*.json` declarations |
| 6 | Observed Python compatibility matrix | (direct) | ✅ Complete | Allowlisted local interpreter receipts; no neighboring-version inference |
| 7 | Modular CLI and adaptive debate | (direct) | ✅ Complete | `experience`, TUI, freshness, matrix and negotiation commands; bounded replay/dissent/budget |
| 8 | Fixtures, parity, eval and release gates | (direct) | ✅ Complete | Unit, integration, holdout and mutation declarations are executable offline |

## Implemented Surface

- `apiforge tui TASK` opens optional Textual UX; `--fallback` emits the same
  canonical projection with `AF-TUI-UNAVAILABLE` when visual dependencies are
  unavailable.
- `apiforge experience status|doctor|review TASK` is a modular command group;
  legacy top-level aliases remain unchanged.
- `apiforge knowledge freshness`, `apiforge agentops negotiate` and
  `apiforge migration matrix` expose receipt-backed freshness, host intersection
  and observed compatibility cells.
- `VersionedContract` was intentionally not changed globally because existing
  planning contracts enumerate declared fields. Evidence Levels were added to
  artifact/run/verification contracts and all new interoperability contracts,
  with legacy Knowledge Packs remaining `unknown` unless metadata is declared.

## Verification Results

### Lint and type checks

```text
ruff check .                         All checks passed
mypy src/apiforge                    Success: no issues found in 326 source files
vendor_caveman.py --check            vendor/ OK -- 127 arquivos conferem com o manifest
git diff --check                     exit 0; CRLF normalization warnings only
```

### Tests

```text
pytest -q                            866 passed, 1 skipped in 46.34s
```

The optional Textual installation was validated locally at `textual==8.2.8`
and `rich==14.3.4`; the base install remains headless-compatible.

### SDD and specification gates

```text
spec-linter DEFINE                    VERDICT: PASS (no findings)
spec-linter DESIGN                    VERDICT: PASS (no findings)
apiforge sdd check --root docs/sdd    ok=true, unresolved=[]
```

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|----|----------|--------|----------|
| AT-001 | Inicialização TUI | ✅ Pass | Textual app, execution-first composition and TUI tests |
| AT-002 | Fallback headless | ✅ Pass | Fallback parity test and explicit `AF-TUI-UNAVAILABLE` |
| AT-003 | Execução e resume | ✅ Pass | Runtime experience and resume regression suite |
| AT-004 | Governança na TUI | ✅ Pass | Application cancel facade, ControlPlane path and governance panel |
| AT-005 | Evidence Levels | ✅ Pass | Shared evidence contracts plus artifact/run/verification coverage |
| AT-006 | Knowledge Pack fresco | ✅ Pass | Hash/window/receipt freshness tests |
| AT-007 | Knowledge Pack stale | ✅ Pass | Missing receipt, expired timestamp and hash mismatch tests |
| AT-008 | Host capability negotiation | ✅ Pass | Four-host intersection and local declaration tests |
| AT-009 | Python compatibility matrix | ✅ Pass | Two local interpreter observations and unresolved-cell assertions |
| AT-010 | CLI modular parity | ✅ Pass | `experience status` equals legacy `status` payload |
| AT-011 | Debate adaptativo | ✅ Pass | Bounded plan, quorum, replay id, dissent and fake-adapter tests |
| AT-012 | Debate sem prova | ✅ Pass | Existing evidence/quorum refusal plus adaptive budget refusal |
| AT-013 | Slice quality gate | ✅ Pass | Runtime gate covers golden, holdout and mutation cases |
| AT-014 | Compatibilidade | ✅ Pass | Full legacy suite remains green; migrations are additive |

## Data Quality Results

| Check | Result | Details |
|-------|--------|---------|
| Source authority | ✅ | Existing loader contract preserved |
| Freshness | ✅ | `fresh`, `stale`, `unresolved`, `unknown` are distinct |
| Provenance | ✅ | Source hashes, receipt refs and evidence refs are retained |
| Completeness | ✅ | Missing external receipts never become success |

## Issues and Autonomous Decisions

| # | Decision | Chosen resolution |
|---|----------|-------------------|
| 1 | Optional Textual dependency | Keep Textual/Rich isolated behind `.[tui]`; base CLI remains usable |
| 2 | Evidence field placement | Avoid a global base-model field because it would change legacy planning semantics; add explicit levels to relevant/new contracts |
| 3 | Host integration boundary | Use local declarations and static fallback; no provider or host SDK calls from core |
| 4 | Python matrix scope | Record actual interpreter receipts and leave unexecuted versions unresolved |
| 5 | External freshness | Verify receipts only; no automatic network refresh or pack mutation |
| 6 | CLI migration | Add a modular facade and preserve expert aliases to avoid command drift |

## Known Unresolved Gaps

- Knowledge Packs without newly declared freshness metadata remain `unknown` and
  need source-owner receipts before they can be called fresh.
- Real host negotiation still depends on host-owned declarations/receipts; the
  core does not claim live parity for Codex, Claude, Devin or Copilot.
- Python versions not actually executed in the declared environment remain
  `unresolved`; local proof is not CI or production support.
- Real provider-backed multi-model debate adapters remain outside the offline
  core; fake/local adapters cover the mandatory deterministic evaluation path.

## Final Status

### Overall: ✅ COMPLETE

- [x] Manifest tasks implemented
- [x] Focused and full tests pass
- [x] Ruff, mypy, vendor, SDD and spec gates pass
- [x] Acceptance tests recorded
- [x] Documentation updated
- [x] Ready for `/ship`

## Next Step

**Ready for:** `/ship .claude/sdd/features/DEFINE_API_FORGE_AGENTIC_EXPERIENCE_INTEROPERABILITY.md`
