# API Forge MVP Vertical Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic CLI that reads an existing FastAPI project and an OpenAPI 3.1 document, constructs a provenance-backed API-IR, detects contract/code divergence and breaking contract changes, and emits structured facts and findings.

**Architecture:** A Python 3.12 package separates immutable evidence contracts, OpenAPI ingestion, FastAPI static extraction, API-IR composition, comparison rules, case persistence, and CLI adapters. All analysis is offline and deterministic; no model provider, network call, cloud mutation, code generation, or vector database is included in this increment.

**Tech Stack:** Python 3.12, Pydantic 2, Typer, PyYAML, pytest, Ruff, mypy, Hatchling.

**Spec:** `docs/specs/2026-09-21-api-forge-design.md`

## Global Constraints

- The package name is `apiforge`; the executable is `apiforge`.
- Python 3.12 is the minimum and only CI version in this increment.
- The core must not import an LLM/provider SDK or perform network access.
- Inputs are read-only; outputs are written only beneath an explicit `--out-dir`, defaulting to `.apiforge/`.
- `--out-dir` must not contain or be contained by any input path; case writes refuse `..` traversal and symlink escapes.
- Every fact and finding carries stable IDs and provenance tied to SHA-256 input hashes.
- Unsupported or ambiguous input produces a named diagnostic, never a fabricated conclusion.
- JSON output is deterministic: sorted keys, stable list ordering, UTF-8, trailing newline.
- Keep files focused; production modules should remain below 300 lines unless a reviewer approves a documented exception.
- Use TDD and commit after every task.

## Review Focus

- OpenAPI YAML containing aliases, custom tags or duplicate keys must be rejected safely, without arbitrary object construction; `yaml.safe_load` alone permits aliases and duplicate keys, so Task 4 pins explicit rejection.
- `/orders` and `/orders/` are different routes; matching preserves the trailing slash. Tasks 5 and 8 pin this behavior.
- FastAPI routes assembled through `include_router(prefix=...)` must resolve the effective path; Task 5 pins this behavior.
- Dynamic route declarations that static analysis cannot resolve must emit `unresolved`, not disappear; Task 5 pins this behavior.
- Duplicate method/path operations across files must remain separate facts and produce a conflict finding; Tasks 5 and 8 pin this behavior.
- Re-running against unchanged inputs must produce byte-identical JSON; Tasks 3 and 10 pin this behavior.

---

## Delivery sequence after this plan

This plan is the first independently shippable subproject. Later plans are created only after its interfaces pass review:

1. SDD profiles, policy engine, sandbox/worktree and release evidence — planned in `docs/plans/2026-09-21-api-forge-sdd-policy-sandbox-evidence.md`.
2. FastAPI build/verify workflow and testing/security adapters.
3. Spring Boot adapter and JVM toolchain.
4. Go/Chi adapter and Go toolchain.
5. AWS API Gateway/Lambda, then ECS/Fargate/ALB.
6. Terraform/SAM analysis and guarded execution.
7. MCP, host exporters, context funnel, budgets and AgentOps.
8. Advanced security, performance, observability, migrations and holdout evals.

### Task 1: Bootstrap package and deterministic CLI shell

**Files:**
- Create: `pyproject.toml`
- Create: `src/apiforge/__init__.py`
- Create: `src/apiforge/cli.py`
- Create: `tests/test_cli.py`
- Create: `.gitignore`

**Interfaces:**
- Consumes: none.
- Produces: `apiforge.cli:app`, console command `apiforge`, `apiforge --version`.

- [ ] **Step 1: Write the failing CLI tests**

```python
from typer.testing import CliRunner
from apiforge.cli import app

runner = CliRunner()


def test_version_is_stable() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout == "apiforge 0.1.0\n"


def test_help_lists_mvp_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("discover", "analyze", "model", "diff", "judge"):
        assert command in result.stdout
```

- [ ] **Step 2: Run the tests and verify the import failure**

Run: `python -m pytest tests/test_cli.py -v`  
Expected: FAIL because `apiforge` does not exist.

- [ ] **Step 3: Create package metadata and CLI skeleton**

Use `pyproject.toml` with Hatchling, Python `>=3.12,<3.13`, runtime dependencies `pydantic>=2.9,<3`, `typer>=0.12,<1`, `PyYAML>=6.0.2,<7`, and dev dependencies `pytest>=8,<9`, `ruff>=0.7,<1`, `mypy>=1.13,<2`. Configure the console script as `apiforge = "apiforge.cli:app"`, Ruff line length 100, and strict mypy for `src/apiforge`.

Implement `src/apiforge/__init__.py`:

```python
__version__ = "0.1.0"
```

Implement `src/apiforge/cli.py` with a Typer callback for `--version`. Register `discover`, `analyze`, `judge`, and the groups `model build` and `diff contract` — the command surface named in spec §12, which is binding over abbreviated names — as explicit unavailable commands that exit with code 2 and the exact diagnostic `AF-COMMAND-NOT-AVAILABLE: <command>\n`; Task 10 replaces those bounded diagnostics with the complete application services.

- [ ] **Step 4: Install and run quality checks**

Run: `python -m pip install -e '.[dev]'`  
Run: `python -m pytest tests/test_cli.py -v`  
Run: `ruff check src tests && ruff format --check src tests && mypy src/apiforge`  
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src tests .gitignore
git commit -m "chore: bootstrap apiforge package and cli"
```

### Task 2: Define immutable evidence and diagnostic contracts

**Files:**
- Create: `src/apiforge/core/models.py`
- Create: `src/apiforge/core/ids.py`
- Create: `src/apiforge/core/__init__.py`
- Create: `tests/core/test_models.py`

**Interfaces:**
- Consumes: Pydantic 2.
- Produces: `SourceRef`, `Fact`, `Finding`, `Diagnostic`, `FindingStatus`, `Severity`, `stable_id()`.

- [ ] **Step 1: Write failing contract tests**

```python
import pytest
from pydantic import ValidationError
from apiforge.core.ids import stable_id
from apiforge.core.models import Fact, Finding, FindingStatus, Severity, SourceRef


def test_stable_id_is_order_independent_for_mapping() -> None:
    assert stable_id("fact", {"b": 2, "a": 1}) == stable_id("fact", {"a": 1, "b": 2})


def test_finding_requires_evidence_unless_unresolved() -> None:
    with pytest.raises(ValidationError):
        Finding(
            finding_id="finding:x",
            rule_id="AF-CONTRACT-001",
            status=FindingStatus.CONFIRMED,
            severity=Severity.HIGH,
            title="Missing implementation",
            evidence=[],
        )


def test_models_are_immutable() -> None:
    fact = Fact(
        fact_id="fact:x",
        kind="api.operation",
        source=SourceRef(path="openapi.yaml", sha256="a" * 64),
        measures={"method": "GET"},
    )
    with pytest.raises(ValidationError):
        fact.kind = "changed"  # type: ignore[misc]
```

- [ ] **Step 2: Run tests and verify missing modules**

Run: `pytest tests/core/test_models.py -v`  
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement the contracts**

Use frozen Pydantic models with `extra="forbid"`. `SourceRef` contains `path`, optional line/column, `sha256`, and `extractor`. `Fact` contains `fact_id`, `kind`, `source`, JSON-compatible `measures` and `attrs`. `Finding` contains `finding_id`, `rule_id`, `status`, `severity`, `title`, `detail`, evidence fact IDs, and optional remediation. A model validator rejects confirmed findings with empty evidence. `Diagnostic` contains `code`, `status`, `message`, optional source, and details. Enums must include:

```python
class FindingStatus(StrEnum):
    CONFIRMED = "confirmed"
    UNRESOLVED = "unresolved"
    NOT_APPLICABLE = "not_applicable"


class Severity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

`stable_id(prefix, value)` serializes with sorted keys and compact separators, hashes with SHA-256, and returns `<prefix>:<first-16-hex>`.

Frozen models prevent attribute reassignment only. Coerce nested sequences inside `measures`/`attrs` to tuples (or reject mutable values in a field validator) so stored evidence cannot mutate in place — evidence immutability is an invariant, not a courtesy.

- [ ] **Step 4: Run unit and type checks**

Run: `pytest tests/core/test_models.py -v && mypy src/apiforge/core`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/apiforge/core tests/core
git commit -m "feat: add immutable evidence contracts"
```

### Task 3: Add deterministic artifact hashing and JSON storage

**Files:**
- Create: `src/apiforge/core/io.py`
- Create: `tests/core/test_io.py`

**Interfaces:**
- Consumes: `BaseModel` from Pydantic.
- Produces: `sha256_file(path: Path) -> str`, `write_json(path: Path, value: object) -> None`, `read_json(path: Path) -> object`.

- [ ] **Step 1: Write failing IO tests**

```python
from pathlib import Path
from apiforge.core.io import read_json, sha256_file, write_json


def test_write_json_is_byte_stable(tmp_path: Path) -> None:
    target = tmp_path / "value.json"
    write_json(target, {"z": 1, "a": [2, 1]})
    first = target.read_bytes()
    write_json(target, {"a": [2, 1], "z": 1})
    assert target.read_bytes() == first
    assert first.endswith(b"\n")


def test_sha256_changes_with_content(tmp_path: Path) -> None:
    target = tmp_path / "input"
    target.write_text("one", encoding="utf-8")
    first = sha256_file(target)
    target.write_text("two", encoding="utf-8")
    assert sha256_file(target) != first
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/core/test_io.py -v`  
Expected: FAIL because `apiforge.core.io` is absent.

- [ ] **Step 3: Implement atomic deterministic IO**

`write_json` creates the parent directory, serializes Pydantic models through `model_dump(mode="json")`, sorts mapping keys, uses indent 2 and `ensure_ascii=False`, appends one newline, writes a sibling `.tmp`, then calls `Path.replace`. `read_json` uses UTF-8 and `json.load`. `sha256_file` streams 1 MiB blocks.

- [ ] **Step 4: Run tests twice**

Run: `pytest tests/core/test_io.py -v && pytest tests/core/test_io.py -v`  
Expected: identical PASS results.

- [ ] **Step 5: Commit**

```bash
git add src/apiforge/core/io.py tests/core/test_io.py
git commit -m "feat: add deterministic artifact storage"
```

### Task 4: Load and normalize OpenAPI 3.1 safely

**Files:**
- Create: `src/apiforge/openapi/models.py`
- Create: `src/apiforge/openapi/loader.py`
- Create: `src/apiforge/openapi/__init__.py`
- Create: `tests/openapi/test_loader.py`
- Create: `tests/fixtures/openapi/orders-v1.yaml`
- Create: `tests/fixtures/openapi/unsafe-tag.yaml`
- Create: `tests/fixtures/openapi/aliased.yaml`

**Interfaces:**
- Consumes: `SourceRef`, `Diagnostic`, `sha256_file`.
- Produces: `OpenApiDocument`, `OpenApiOperation`, `load_openapi(path: Path) -> OpenApiDocument`.

- [ ] **Step 1: Add a minimal OpenAPI fixture**

The fixture declares OpenAPI `3.1.0`, `/orders` GET and POST, stable `operationId` values, a required JSON request body for POST, `200`/`201` responses, and component schema `Order`.

- [ ] **Step 2: Write failing loader tests**

```python
from pathlib import Path
import pytest
from apiforge.openapi.loader import OpenApiLoadError, load_openapi

FIXTURES = Path("tests/fixtures/openapi")


def test_loads_operations_in_stable_order() -> None:
    document = load_openapi(FIXTURES / "orders-v1.yaml")
    assert document.version == "3.1.0"
    assert [(op.method, op.path) for op in document.operations] == [
        ("get", "/orders"),
        ("post", "/orders"),
    ]


def test_rejects_unsupported_openapi_version(tmp_path: Path) -> None:
    path = tmp_path / "openapi.yaml"
    path.write_text("openapi: 3.0.3\ninfo: {title: x, version: '1'}\npaths: {}\n", encoding="utf-8")
    with pytest.raises(OpenApiLoadError, match="AF-OPENAPI-UNSUPPORTED-VERSION"):
        load_openapi(path)


def test_safe_loader_rejects_python_tag() -> None:
    with pytest.raises(OpenApiLoadError, match="AF-OPENAPI-INVALID-YAML"):
        load_openapi(FIXTURES / "unsafe-tag.yaml")


def test_rejects_yaml_aliases() -> None:
    with pytest.raises(OpenApiLoadError, match="AF-OPENAPI-INVALID-YAML"):
        load_openapi(FIXTURES / "aliased.yaml")


def test_rejects_duplicate_keys(tmp_path: Path) -> None:
    path = tmp_path / "dup.yaml"
    path.write_text(
        "openapi: 3.1.0\ninfo: {title: x, version: '1'}\npaths: {}\npaths: {}\n",
        encoding="utf-8",
    )
    with pytest.raises(OpenApiLoadError, match="AF-OPENAPI-INVALID-YAML"):
        load_openapi(path)
```

- [ ] **Step 3: Verify failures**

Run: `pytest tests/openapi/test_loader.py -v`  
Expected: FAIL because loader does not exist.

- [ ] **Step 4: Implement safe normalization**

Compose the YAML node tree with a `SafeLoader` subclass that refuses aliases/merge keys, custom tags and duplicate mapping keys — plain `yaml.safe_load` accepts all three silently. Require a mapping root and exact OpenAPI major/minor `3.1`, reject duplicate `(method, normalized_path)` pairs inside the document, and support only standard HTTP methods. Preserve the raw operation object and the raw `components` section as JSON-compatible data (Task 7 resolves local refs against them) but sort operations by path then method. Define a typed `OpenApiLoadError(code, message, path)` whose string begins with its code.

- [ ] **Step 5: Run checks and commit**

Run: `pytest tests/openapi/test_loader.py -v && ruff check src/apiforge/openapi tests/openapi`  
Expected: PASS.

```bash
git add src/apiforge/openapi tests/openapi tests/fixtures/openapi
git commit -m "feat: load and normalize openapi 3.1"
```

### Task 5: Extract FastAPI routes statically

**Files:**
- Create: `src/apiforge/adapters/fastapi/extractor.py`
- Create: `src/apiforge/adapters/fastapi/models.py`
- Create: `src/apiforge/adapters/fastapi/__init__.py`
- Create: `tests/adapters/fastapi/test_extractor.py`
- Create: `tests/fixtures/fastapi_orders/app/main.py`
- Create: `tests/fixtures/fastapi_orders/app/routes/orders.py`

**Interfaces:**
- Consumes: `Fact`, `Diagnostic`, `SourceRef`, `stable_id`, `sha256_file`.
- Produces: `FastApiInventory`, `extract_fastapi(project_root: Path) -> FastApiInventory`.

- [ ] **Step 1: Create the route fixture**

`orders.py` defines `router = APIRouter(prefix="/orders")`, `@router.get("/{order_id}")`, two deliberately duplicated `@router.post("")` handlers, and one decorator whose path is a function call. `main.py` creates `FastAPI()` and calls `app.include_router(router, prefix="/v1")`.

- [ ] **Step 2: Write failing extractor tests**

```python
from pathlib import Path
from apiforge.adapters.fastapi.extractor import extract_fastapi

ROOT = Path("tests/fixtures/fastapi_orders")


def test_resolves_router_and_include_prefixes() -> None:
    inventory = extract_fastapi(ROOT)
    routes = [(f.measures["method"], f.measures["path"]) for f in inventory.facts]
    assert ("get", "/v1/orders/{order_id}") in routes


def test_preserves_duplicate_route_facts() -> None:
    inventory = extract_fastapi(ROOT)
    posts = [f for f in inventory.facts if f.measures == {"method": "post", "path": "/v1/orders"}]
    assert len(posts) == 2
    assert posts[0].fact_id != posts[1].fact_id


def test_dynamic_path_is_named_unresolved() -> None:
    inventory = extract_fastapi(ROOT)
    assert any(d.code == "AF-FASTAPI-DYNAMIC-ROUTE" for d in inventory.diagnostics)
```

- [ ] **Step 3: Verify failures**

Run: `pytest tests/adapters/fastapi/test_extractor.py -v`  
Expected: FAIL because extractor is absent.

- [ ] **Step 4: Implement two-pass AST extraction**

Pass one records `FastAPI`/`APIRouter` assignments, literal router prefixes, decorated functions, method, literal path, function name, source line and file hash. Pass two finds literal `include_router` prefixes and applies them, resolving its argument through intra-project imports so a router defined in `app/routes/orders.py` and included in `app/main.py` binds to the same object. Use only `ast.parse`; never import or execute project code. For unresolved expressions emit `AF-FASTAPI-DYNAMIC-ROUTE`. Include file path and line in route IDs so duplicates remain distinct. Record a hashed source entry for every scanned `*.py` file, including files without routes, so provenance covers the whole project. Path comparison preserves the trailing slash — `/orders` and `/orders/` are distinct routes. Sort facts by path, method, file and line.

- [ ] **Step 5: Run adapter checks and commit**

Run: `pytest tests/adapters/fastapi/test_extractor.py -v && mypy src/apiforge/adapters/fastapi`  
Expected: PASS.

```bash
git add src/apiforge/adapters tests/adapters tests/fixtures/fastapi_orders
git commit -m "feat: extract fastapi routes without execution"
```

### Task 6: Compose the canonical API-IR

**Files:**
- Create: `src/apiforge/api_ir/models.py`
- Create: `src/apiforge/api_ir/builder.py`
- Create: `src/apiforge/api_ir/__init__.py`
- Create: `tests/api_ir/test_builder.py`
- Create: `tests/api_ir/conftest.py`
- Create: `tests/fixtures/fastapi_flat/app/main.py`
- Create: `tests/fixtures/fastapi_flat/app/routes/orders.py`

**Interfaces:**
- Consumes: `OpenApiDocument`, `FastApiInventory`, evidence fact IDs.
- Produces: `ApiModel`, `ApiOperation`, `Projection`, `build_api_model(contract, inventory) -> ApiModel`.

- [ ] **Step 1: Write failing composition tests**

`conftest.py` builds the `openapi_document`/`fastapi_inventory` pair from `tests/fixtures/fastapi_flat`, a project whose routes resolve to `/orders` with no extra include prefix — the Task 5 fixture resolves under `/v1`, so do not reuse it for matching assertions.

```python
def test_operation_keeps_contract_and_code_provenance(openapi_document, fastapi_inventory) -> None:
    model = build_api_model(openapi_document, fastapi_inventory)
    operation = model.operation("post", "/orders")
    assert operation.contract is not None
    assert operation.contract.source.sha256
    assert operation.code_projections
    assert all(item.fact_id for item in operation.code_projections)


def test_model_order_is_stable(openapi_document, fastapi_inventory) -> None:
    first = build_api_model(openapi_document, fastapi_inventory).model_dump_json()
    second = build_api_model(openapi_document, fastapi_inventory).model_dump_json()
    assert first == second
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/api_ir/test_builder.py -v`  
Expected: FAIL because API-IR is absent.

- [ ] **Step 3: Implement immutable API-IR models and builder**

Key operations by normalized lowercase method plus canonical path. Preserve zero, one, or many contract and code projections rather than overwriting duplicates. `ApiModel.operation(method, path)` raises `KeyError` on absence. Store `schema_version="1"`, generator version, input hashes, operations and diagnostics. Sort projections by source path/line and operations by path/method.

- [ ] **Step 4: Run tests and commit**

Run: `pytest tests/api_ir/test_builder.py -v && mypy src/apiforge/api_ir`  
Expected: PASS.

```bash
git add src/apiforge/api_ir tests/api_ir
git commit -m "feat: compose provenance-backed api ir"
```

### Task 7: Detect breaking changes between OpenAPI versions

**Files:**
- Create: `src/apiforge/openapi/diff.py`
- Create: `tests/openapi/test_diff.py`
- Create: `tests/fixtures/openapi/orders-v2-breaking.yaml`

**Interfaces:**
- Consumes: two `OpenApiDocument` objects.
- Produces: `ContractChange`, `ChangeKind`, `diff_contracts(baseline, candidate) -> tuple[ContractChange, ...]`.

- [ ] **Step 1: Define a breaking fixture and failing tests**

The candidate removes GET `/orders`, removes a `200` response, makes an optional request property required, and adds a new optional response property. Keep each fixture delta attributable: the baseline carries the superset (both `200` and `201` on POST, an optional-only request property) so each removed or tightened element maps to exactly one change code.

```python
def test_classifies_breaking_and_non_breaking_changes() -> None:
    changes = diff_contracts(load("orders-v1.yaml"), load("orders-v2-breaking.yaml"))
    observed = {(c.code, c.breaking) for c in changes}
    assert ("AF-BREAKING-OPERATION-REMOVED", True) in observed
    assert ("AF-BREAKING-RESPONSE-REMOVED", True) in observed
    assert ("AF-BREAKING-REQUEST-REQUIRED-ADDED", True) in observed
    assert ("AF-COMPAT-RESPONSE-OPTIONAL-ADDED", False) in observed
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/openapi/test_diff.py -v`  
Expected: FAIL because diff module is absent.

- [ ] **Step 3: Implement the bounded diff engine**

Support operation removal/addition, response status removal/addition, request required-property addition/removal, and response optional-property addition. Resolve local component refs of the exact form `#/components/schemas/<name>`; emit `AF-OPENAPI-REF-UNRESOLVED` for unsupported/external refs instead of guessing. Sort changes by code, path, method and JSON pointer.

- [ ] **Step 4: Run tests and commit**

Run: `pytest tests/openapi/test_diff.py -v`  
Expected: PASS.

```bash
git add src/apiforge/openapi/diff.py tests/openapi/test_diff.py tests/fixtures/openapi/orders-v2-breaking.yaml
git commit -m "feat: classify bounded openapi breaking changes"
```

### Task 8: Judge contract/code divergence through executable rules

**Files:**
- Create: `src/apiforge/rules/catalog.py`
- Create: `src/apiforge/rules/judge.py`
- Create: `src/apiforge/rules/__init__.py`
- Create: `src/apiforge/rules/catalog/contract.yaml`
- Create: `tests/rules/test_judge.py`

**Interfaces:**
- Consumes: `ApiModel` and catalog metadata.
- Produces: `judge_api_model(model: ApiModel) -> tuple[Finding, ...]`.

- [ ] **Step 1: Write failing rule tests**

```python
def test_missing_implementation_is_confirmed(api_model) -> None:
    findings = judge_api_model(api_model)
    finding = next(f for f in findings if f.rule_id == "AF-CONTRACT-001")
    assert finding.status == FindingStatus.CONFIRMED
    assert finding.evidence


def test_duplicate_implementation_is_reported(api_model_with_duplicate_post) -> None:
    findings = judge_api_model(api_model_with_duplicate_post)
    finding = next(f for f in findings if f.rule_id == "AF-CODE-001")
    assert len(finding.evidence) == 2


def test_dynamic_route_yields_unresolved_finding(api_model_with_dynamic_route) -> None:
    findings = judge_api_model(api_model_with_dynamic_route)
    assert any(f.status == FindingStatus.UNRESOLVED for f in findings)
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/rules/test_judge.py -v`  
Expected: FAIL because rules are absent.

- [ ] **Step 3: Implement four rules**

Implement `AF-CONTRACT-001` contract operation missing in code, `AF-CODE-001` duplicate code route, `AF-CODE-002` code route missing from contract, and `AF-CODE-003` unresolved dynamic route. YAML stores ID, title, severity, rationale, remediation and reference metadata; Python contains bounded executable predicates. Ship the catalog as package data inside `apiforge.rules` (Hatchling includes it in the wheel) so the installed CLI works outside the checkout. `AF-CONTRACT-001` reports `confirmed` only when code extraction was complete for the relevant paths; when the inventory carries `AF-FASTAPI-DYNAMIC-ROUTE` or comparable uncertainty, it reports `unresolved` with the blocking diagnostics as evidence — never a fabricated absence. Path comparison preserves the trailing slash. Findings use stable IDs derived from rule ID and evidence IDs. Sort by severity rank, rule ID and finding ID.

- [ ] **Step 4: Run tests and commit**

Run: `pytest tests/rules/test_judge.py -v && pytest tests/core tests/openapi tests/adapters tests/api_ir -q`  
Expected: PASS.

```bash
git add src/apiforge/rules tests/rules
git commit -m "feat: judge api contract and code divergence"
```

### Task 9: Persist a reproducible analysis case

**Files:**
- Create: `src/apiforge/case/models.py`
- Create: `src/apiforge/case/service.py`
- Create: `src/apiforge/case/__init__.py`
- Create: `tests/case/test_service.py`

**Interfaces:**
- Consumes: contract path, project path, `ApiModel`, facts, findings and deterministic IO.
- Produces: `CaseManifest`, `save_case(out_dir, ...) -> CaseManifest`, `load_case(out_dir) -> CaseManifest`.

- [ ] **Step 1: Write failing persistence test**

```python
def test_case_manifest_links_all_artifacts(tmp_path, analysis_result) -> None:
    manifest = save_case(tmp_path, analysis_result)
    assert (tmp_path / "case.json").exists()
    assert (tmp_path / "api-ir.json").exists()
    assert (tmp_path / "facts.json").exists()
    assert (tmp_path / "findings.json").exists()
    assert manifest.artifacts["api_ir"].sha256
    assert load_case(tmp_path) == manifest
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/case/test_service.py -v`  
Expected: FAIL because case service is absent.

- [ ] **Step 3: Implement manifest-last persistence**

Write `api-ir.json`, `facts.json`, `findings.json`, then `case.json` last so a manifest never references an artifact that does not exist yet. When contract changes were computed, persist `changes.json` as an additional declared artifact. The manifest contains schema version, tool version, input hashes, artifact relative paths/hashes, diagnostics count and finding counts by severity/status. On load, verify every declared artifact hash; raise `CaseIntegrityError("AF-CASE-HASH-MISMATCH", path)` on mismatch. Refuse an `out_dir` that escapes the working tree via `..` or a symlink, and refuse to write when `out_dir` contains or is contained by an input path — inputs stay read-only.

- [ ] **Step 4: Run tests and commit**

Run: `pytest tests/case/test_service.py -v`  
Expected: PASS.

```bash
git add src/apiforge/case tests/case
git commit -m "feat: persist reproducible analysis cases"
```

### Task 10: Wire the end-to-end CLI and deterministic output

**Files:**
- Modify: `src/apiforge/cli.py`
- Create: `src/apiforge/application/analyze.py`
- Create: `src/apiforge/application/__init__.py`
- Modify: `tests/test_cli.py`
- Create: `tests/e2e/test_vertical_slice.py`

**Interfaces:**
- Consumes: all prior public interfaces.
- Produces: `analyze_project(contract, project, baseline, out_dir) -> AnalysisResult`; functional `discover`, `analyze`, `judge`, `model build` and `diff contract` CLI commands.

- [ ] **Step 1: Write the failing end-to-end test**

```python
def test_analyze_command_is_reproducible(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    args = [
        "analyze",
        "--contract",
        "tests/fixtures/openapi/orders-v1.yaml",
        "--project",
        "tests/fixtures/fastapi_orders",
    ]
    assert runner.invoke(app, [*args, "--out-dir", str(first)]).exit_code == 0
    assert runner.invoke(app, [*args, "--out-dir", str(second)]).exit_code == 0
    for name in ("api-ir.json", "facts.json", "findings.json"):
        assert (first / name).read_bytes() == (second / name).read_bytes()


def test_invalid_input_returns_usage_exit_code(tmp_path: Path) -> None:
    result = runner.invoke(app, ["analyze", "--contract", "missing.yaml", "--project", "."])
    assert result.exit_code == 2
    assert "AF-INPUT-NOT-FOUND" in result.stderr
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/e2e/test_vertical_slice.py -v`  
Expected: FAIL because `analyze` is not implemented.

- [ ] **Step 3: Implement application orchestration and CLI**

Define frozen `AnalysisResult` with `manifest: CaseManifest`, `model: ApiModel`, `facts: tuple[Fact, ...]`, `findings: tuple[Finding, ...]`, `changes: tuple[ContractChange, ...]`, and `diagnostics: tuple[Diagnostic, ...]`. `analyze_project` validates paths, loads OpenAPI, extracts FastAPI, builds API-IR, judges findings, optionally diffs a `--baseline` OpenAPI document, persists the case and returns that result. Keep a pre-persistence payload (model, facts, findings, changes, diagnostics) separate from `AnalysisResult`: `save_case` consumes the payload and returns the manifest that completes the result, so construction is one-directional and never circular; when a baseline diff ran, `changes.json` is written as a declared case artifact. Commands expose individual stages but call the same application services. Success prints a compact JSON summary with artifact paths and counts. Input/validation errors exit 2; integrity/internal analysis errors exit 3; confirmed critical findings exit 4 only when `--fail-on critical` is supplied.

- [ ] **Step 4: Run complete verification**

Run: `pytest -q`  
Run: `ruff check src tests && ruff format --check src tests`  
Run: `mypy src/apiforge`  
Run: `apiforge analyze --contract tests/fixtures/openapi/orders-v1.yaml --project tests/fixtures/fastapi_orders --out-dir /tmp/apiforge-smoke`  
Expected: all checks PASS; smoke command prints valid JSON and creates the four case files.

- [ ] **Step 5: Commit**

```bash
git add src/apiforge/application src/apiforge/cli.py tests/test_cli.py tests/e2e
git commit -m "feat: deliver deterministic fastapi analysis slice"
```

### Task 11: Add documentation, threat boundaries and release gate

**Files:**
- Create: `README.md`
- Create: `docs/architecture/mvp-boundaries.md`
- Create: `docs/security/threat-model-mvp.md`
- Create: `docs/decisions/ADR-001-deterministic-core.md`
- Create: `docs/decisions/ADR-002-api-ir-provenance.md`
- Create: `scripts/check_mvp_release.py`
- Create: `tests/scripts/test_check_mvp_release.py`

**Interfaces:**
- Consumes: CLI behavior and repository files.
- Produces: reproducible quickstart and `python scripts/check_mvp_release.py` release gate.

- [ ] **Step 1: Write the failing release-gate test**

```python
from scripts.check_mvp_release import check_repository


def test_release_gate_accepts_complete_repository() -> None:
    failures = check_repository(Path("."))
    assert failures == []
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/scripts/test_check_mvp_release.py -v`  
Expected: FAIL because the script is absent.

- [ ] **Step 3: Write bounded documentation**

README contains installation, one analyze example, artifact meanings, exit codes, supported/unsupported syntax, no-network guarantee and known limitations. MVP boundaries explicitly exclude code execution, model calls, `$ref` over network, framework inference beyond FastAPI, cloud access and mutation. Threat model covers malicious YAML, hostile source code, path traversal, symlinks escaping project root, secret leakage, resource exhaustion and tampered case artifacts. ADRs record deterministic-first and provenance-preserving API-IR decisions.

- [ ] **Step 4: Implement the release gate**

`check_repository(root)` verifies required docs exist, no production import matches `(openai|anthropic|boto3|litellm)`, every catalog rule ID appears in a test, fixture analysis is reproducible, and the full test suite is not invoked recursively. The script prints each failure and exits 1, otherwise prints `API Forge MVP release gate: PASS` and exits 0.

- [ ] **Step 5: Run final gate and commit**

Run: `pytest -q && python scripts/check_mvp_release.py`  
Run: `ruff check . && ruff format --check . && mypy src/apiforge`  
Expected: all PASS.

```bash
git add README.md docs scripts tests/scripts
git commit -m "docs: define mvp boundaries and release gate"
```

## Amendments folded in during execution

Decisions recorded in `.superpowers/sdd/2026-09-21-api-forge-mvp-vertical-slice/progress.md`, now incorporated into the tasks above:

- CLI surface follows spec §12: `discover`, `analyze`, `judge`, `model build`, `diff contract` (Tasks 1, 10). The spec is binding over abbreviated command names.
- YAML loading rejects aliases, custom tags and duplicate keys explicitly; `yaml.safe_load` alone permits all three (Task 4).
- `OpenApiDocument` carries the raw `components` section so the Task 7 diff can resolve local refs (Task 4).
- FastAPI extraction resolves `include_router` arguments through cross-file imports and hashes every scanned file, route-bearing or not (Task 5).
- Trailing slash is significant in route matching — `/orders` ≠ `/orders/` (Tasks 5, 8).
- Task 6 composition tests use a dedicated `fastapi_flat` fixture resolving to `/orders`; the Task 5 fixture's effective paths live under `/v1` (Task 6).
- `AF-CONTRACT-001` yields `unresolved` under extraction uncertainty, never a fabricated confirmed absence (Task 8).
- The rule catalog ships as package data inside `apiforge.rules`, not as a top-level `rules/` directory, so the installed CLI works outside the checkout (Task 8).
- Cases persist `changes.json` when a baseline diff ran; the manifest is written last; `out_dir` traversal/symlink escapes and input/output overlap are refused (Tasks 9, 10).
- `AnalysisResult` is built after `save_case` from a pre-persistence payload — construction is one-directional, never circular (Task 10).
- Evidence immutability covers nested collections, not just attribute reassignment (Task 2).

## Final acceptance

Run in a clean Python 3.12 environment:

```bash
python -m pip install -e '.[dev]'
pytest -q
ruff check .
ruff format --check .
mypy src/apiforge
python scripts/check_mvp_release.py
apiforge analyze \
  --contract tests/fixtures/openapi/orders-v1.yaml \
  --project tests/fixtures/fastapi_orders \
  --out-dir .apiforge/acceptance
git status --short
```

Acceptance requires all checks to pass, deterministic artifacts to be produced, and `git status --short` to show only the explicitly ignored `.apiforge/acceptance` directory or no changes.
