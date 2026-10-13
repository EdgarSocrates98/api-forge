# API Forge Catalog Foundation, Routing and Spring Boot Adapter Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the single-file rule catalog into a multi-area, data-driven catalog with deterministic routing (`next-step`), add `detail_level` economics to the core output path, and land the first non-Python language adapter — Java/Spring Boot via tree-sitter — with a parity lab (`orders-spring`) proving the same API-IR and judge rules work unchanged.

**Architecture:** `apiforge.rules.catalog` becomes a directory loader: every `catalog/*.yaml` file declares `area`, `catalog_version` and `rules[]` under a closed schema; `routing.yaml` maps (phase, dominant finding area) → `recommended_agent`. `apiforge.next_step` composes over findings — it never reads artifacts. A generic `detail_level` projector (`summary|normal|full`) lives in `apiforge.core` and is applied at the CLI/MCP boundary, so economics is measured, not claimed. The language adapter contract is generalized: `CodeInventory` (facts `code.route`, diagnostics, `input_hashes`) is produced by `extract_fastapi` today and by `extract_spring` next — the judge, diff, case persistence and sandbox consume it unchanged. Java extraction uses tree-sitter (ADR-006): no toolchain of the target project, no code execution, one mechanism for every future language.

**Tech Stack:** Python 3.12, Pydantic 2, Typer, PyYAML, pytest, Ruff, mypy, Hatchling, **tree-sitter + tree-sitter-java** (new runtime dependencies — pinned versions at least 7 days old, wheels only; ADR-006 records the trade-off vs a native parser subprocess).

**Spec:** `docs/specs/2026-09-21-api-forge-agentic-platform.md` (§3 roteamento como dado, §4 catálogo, §6 economia, §8 adapters, §9 labs) — this plan delivers sequence items 3 and 5, reordered so Java ships before Go per the operator's call ("a inicial é java").

**Depends on:** plan 1 (`Fact`, `Finding`, `Diagnostic`, `SourceRef`, `extract_fastapi`, `judge_api_model`, `analyze_project`) and plan 2 (`sdd`, `policy`, `sandbox`, `evidence`).

## Global Constraints

- Routing is data, not judgment: `next-step` reads `routing.yaml`; nobody picks a coordinator by inspection.
- Every refusal names an `AF-*` code, `field`, `unlock`.
- Catalog schema is closed: unknown keys refuse; `expected_gain` is refused by schema everywhere; `runtime_scope` is an optional declared range — when present and the detected runtime is out of range the rule is skipped, never silently applied.
- `detail_level` changes representation, never content: `summary` is a projection of `normal`, `full` adds raw payloads; the projector must not drop refusal codes or fact_ids.
- The Spring extractor never executes Java, never requires Maven/Gradle/JDK, and emits `unresolved` diagnostics for anything it cannot resolve statically — never infers.
- Every file the extractor scans contributes to `input_hashes`, parsed or not.
- Catalogs ship as package data; production modules stay below ~300 lines.
- TDD and one commit per task; `.superpowers` ledger outside Git.

## Review Focus

- `load_catalog` must merge all `catalog/*.yaml` deterministically (sorted filenames), reject duplicate rule ids across files, and keep `rules/<file>.yaml` self-describing (`area`, `retrieved`, `reference`).
- `routing.yaml` keys are closed vocabulary: phase names from `apiforge.sdd.PHASES`, areas from the catalog itself — the gate test cross-checks both directions.
- `detail_level` must be applied *after* the deterministic pipeline, at serialization time — facts/findings objects are untouched.
- The tree-sitter grammar handles `@RestController`/`@Controller` + class-level `@RequestMapping` prefix + method-level `@GetMapping`/`@PostMapping`/`@PutMapping`/`@DeleteMapping`/`@PatchMapping`/`@RequestMapping(method=…)`, `RouterFunction` beans, and JAX-RS `@Path`/`@GET`…; annotation arguments that are not string literals emit `unresolved`.
- Trailing-slash semantics and duplicate-route retention are identical to the FastAPI extractor — the parity test locks this.
- `mvn`/`gradle`/`javac` must never be invoked; the adapter works on a bare checkout.

---

## Task 1: Multi-area catalog loader

**Files:**
- Modify: `src/apiforge/rules/catalog.py`
- Create: `src/apiforge/rules/catalog/rest.yaml`, `security.yaml`, `testing.yaml`, `perf.yaml`, `breaking.yaml`, `gateway.yaml` (skeletons: metadata + `rules: []`)
- Create: `tests/rules/test_catalog.py`

**Interfaces:**
- Produces: `load_catalog() -> dict[str, RuleMeta]` merging every `catalog/*.yaml` in sorted order; `RuleMeta` gains `area: str`, optional `runtime_scope: str | None`; `load_areas() -> tuple[str, ...]`.
- Refusals: `AF-CATALOG-DUPLICATE-RULE` (same id in two files), `AF-CATALOG-SCHEMA` (unknown key, missing field, `expected_gain` present), `AF-CATALOG-AREA-MISSING`.

- [ ] **Step 1: Write failing tests**

```python
def test_catalog_merges_all_area_files() -> None:
    catalog = load_catalog()
    assert catalog["AF-CONTRACT-001"].area == "CONTRACT"
    assert "REST" in load_areas()


def test_expected_gain_is_refused(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="AF-CATALOG-SCHEMA"):
        load_catalog_text("rules: [{id: X-1, expected_gain: '2x'}]")


def test_duplicate_rule_id_across_files_refused() -> None:
    # two in-memory documents carrying AF-CONTRACT-001
    ...
```

- [ ] **Step 2: Verify failure** — `pytest tests/rules/test_catalog.py` fails: single-file loader exists but no area merge/schema.
- [ ] **Step 3: Implement** the directory loader + closed schema; migrate `contract.yaml` unchanged; add skeleton area files.
- [ ] **Step 4: Run focused tests, lint, mypy; report; commit.**

## Task 2: Routing catalog and `next-step`

**Files:**
- Create: `src/apiforge/rules/catalog/routing.yaml`
- Create: `src/apiforge/application/next_step.py`
- Modify: `src/apiforge/cli.py`, `src/apiforge/cli_governance.py` (or a `verbs` group)
- Create: `tests/rules/test_routing.py`, `tests/e2e/test_next_step.py`

**Interfaces:**
- `routing.yaml`: `routes:` list of `{phase, dominant_area, recommended_agent, rationale}`; phase ∈ `PHASES`, area ∈ `load_areas()`; unmatched → `AF-ROUTING-NO-ROUTE` refusal (named, never a guess).
- `next_step(findings: tuple[Finding, ...], phase: str) -> NextStep` — counts findings by area, picks dominant, consults the catalog; returns `{recommended_agent, dominant_area, finding_count, rationale}`.
- CLI: `apiforge next-step --findings findings.json --phase analyze` (reads an artifact the case already produced — composition, not extraction).

- [ ] **Step 1: Failing tests** — known area routes to the declared agent; empty findings → `AF-ROUTING-NO-FINDINGS`; unknown phase → refusal; tie between areas → deterministic order (severity rank then rule_id), not first-seen.
- [ ] **Step 2: Implement; verify; commit.**

## Task 3: `detail_level` projection in core

**Files:**
- Create: `src/apiforge/core/detail.py`
- Modify: `src/apiforge/cli.py`, `src/apiforge/cli_governance.py` (add `--detail-level` to JSON-producing commands)
- Create: `tests/core/test_detail.py`

**Interfaces:**
- `apply_detail_level(payload: JsonValue, level: str) -> JsonValue`; levels `summary|normal|full`; default `normal` (current behavior — zero regression).
- `summary` keeps `id`/`code`/`severity`/`status`/`count` fields and drops bodies/snippets; `full` is byte-identical to today plus `source.snippet` where the producer has it.
- Invariants tested: refusal codes and `fact_id`s survive `summary`; `summary(payload)` is a strict subset projection (keys removed, never altered).

- [ ] **Step 1: Failing tests** incl. byte-size ordering `len(summary) < len(normal) ≤ len(full)` on the findings fixture.
- [ ] **Step 2: Implement; wire `--detail-level`; commit.**

## Task 4: ADR-006 (tree-sitter) + generalized `CodeInventory`

**Files:**
- Create: `docs/decisions/ADR-006-tree-sitter-language-adapters.md`
- Create: `src/apiforge/adapters/inventory.py` (`CodeInventory` base contract)
- Modify: `src/apiforge/adapters/fastapi/models.py` (subclass/alias — no behavior change)
- Modify: `pyproject.toml` — add `tree-sitter`, `tree-sitter-java` (pinned, ≥7 days old)
- Create: `tests/adapters/test_inventory_contract.py`

**Interfaces:**
- `CodeInventory`: `framework: str`, `facts: tuple[Fact, ...]` (kind `code.route`), `diagnostics: tuple[Diagnostic, ...]`, `input_hashes` — the shape `build_api_model`, `judge_api_model`, `sandbox_apply` and `analyze_project` already consume.
- ADR records: one mechanism for N languages, no target toolchain, offline; cost = native wheel dependency.

- [ ] **Step 1: Contract test** asserting `FastApiInventory` satisfies `CodeInventory` structurally (RED on missing base type).
- [ ] **Step 2: Implement; install deps; verify FastAPI suite unchanged; commit.**

## Task 5: Spring Boot extractor (tree-sitter)

**Files:**
- Create: `src/apiforge/adapters/spring/scan.py`, `src/apiforge/adapters/spring/extractor.py`, `src/apiforge/adapters/spring/models.py` (if needed beyond `CodeInventory`)
- Create: `tests/adapters/spring/test_extractor.py`
- Create: `tests/fixtures/spring_orders/` (Java sources only — no build files required)

**Interfaces:**
- `extract_spring(project_root: Path) -> CodeInventory`.
- Detects: `@RestController`/`@Controller` classes; class-level `@RequestMapping` prefix (literal only); method-level `@GetMapping`/`@PostMapping`/`@PutMapping`/`@DeleteMapping`/`@PatchMapping` and `@RequestMapping(method = RequestMethod.GET, path/value = "…")`; `RouterFunction` beans → `code.route` with `via: router-function` when method+path literals resolve, else `unresolved`.
- Refusals-as-data: non-literal annotation args, `SpEL`, composed meta-annotations → diagnostic `AF-SPRING-UNRESOLVED-ROUTE`; unparseable file → `AF-SPRING-PARSE` diagnostic, still hashed.
- No `javac`, no classpath resolution — imports are matched by simple name, as in the FastAPI extractor.

- [ ] **Step 1: Fixture `spring_orders`** — `OrderController` (`/orders` + GET/POST/`{id}`/DELETE), a `RouterFunction` variant, and one dynamic-path case for `unresolved`.
- [ ] **Step 2: Failing extractor tests** (route facts with method+path+handler+source, diagnostics, `input_hashes` covers every `.java`).
- [ ] **Step 3: Implement two-pass scan (tree-sitter query → facts), keeping extractor ≤300 lines (split `scan.py`/`extractor.py` like the FastAPI adapter).**
- [ ] **Step 4: Verify, lint, mypy; report; commit.**

## Task 6: `orders-spring` parity lab + `analyze --framework`

**Files:**
- Create: `tests/labs/orders-spring/` (equivalent API to `fastapi_orders`, incl. one deliberate defect variant dir)
- Modify: `src/apiforge/application/analyze.py`, `src/apiforge/cli.py` (`--framework fastapi|spring|auto`, default `auto` detects `pom.xml`/`build.gradle` vs `pyproject`/`*.py` heuristics — declared, never guessed silently)
- Create: `tests/e2e/test_spring_parity.py`

**Interfaces:**
- `analyze_project(contract, project, baseline, out_dir, framework="auto")`.
- Parity: same OpenAPI contract judged against `orders-fastapi` and `orders-spring` produces identical findings modulo `source.path`/`fact_id` — the parity test diffs findings after normalizing provenance.

- [ ] **Step 1: Failing parity + framework-detection tests** (auto on a dir with neither marker → `AF-INPUT-FRAMEWORK-UNKNOWN`, not a guess).
- [ ] **Step 2: Implement; verify; commit.**

## Task 7: Docs and release-gate extension

**Files:**
- Modify: `README.md` (adapter matrix, `next-step`, `--detail-level`, `--framework`)
- Modify: `scripts/check_release.py`, `tests/scripts/test_check_release.py`
- Modify: `docs/security/threat-model-mvp.md` (tree-sitter parser input as new hostile-input class)
- Optionally: `docs/routing-contract.md` if routing codes grow beyond `AF-ROUTING-*` (they must then be added to the parity check)

**Gate additions:** `AF-CATALOG-*`/`AF-ROUTING-*`/`AF-SPRING-*` parity vs docs (extend `_check_code_parity`); `routing.yaml` phases ⊆ `PHASES` and areas ⊆ `load_areas()`; `orders-spring` lab present; `tree-sitter` import only inside `apiforge.adapters.spring`.

- [ ] **Step 1: Extend gate tests (RED).**
- [ ] **Step 2: Implement docs + gate; run full acceptance; commit.**

## Final acceptance

```bash
python -m pip install -e '.[dev]'
pytest -q
ruff check . && ruff format --check .
mypy src/apiforge
python scripts/check_release.py
apiforge next-step --findings .apiforge/acceptance/findings.json --phase analyze
apiforge analyze --contract tests/fixtures/openapi/orders-v1.yaml \
  --project tests/labs/orders-spring --framework spring --out-dir .apiforge/spring-case
apiforge analyze --contract tests/fixtures/openapi/orders-v1.yaml \
  --project tests/fixtures/fastapi_orders --out-dir .apiforge/fastapi-case
```

Accept: all checks pass; Spring and FastAPI findings match modulo provenance; `next-step` names an agent from `routing.yaml`; `summary` payload is strictly smaller than `normal`; `git status` clean.
