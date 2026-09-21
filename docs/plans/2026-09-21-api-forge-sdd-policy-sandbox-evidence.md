# API Forge SDD, Policy, Sandbox and Release Evidence Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give API Forge a deterministic governance layer: SDD phase artifacts with a hash cascade, a policy engine that classifies actions before they run, isolated change environments (copy sandbox and git worktree), and a release evidence receipt that proves correspondence between claims and artifacts.

**Architecture:** New modules `apiforge.policy`, `apiforge.sdd`, `apiforge.sandbox`, and `apiforge.evidence` consume the plan-1 contracts (`Fact`, `Finding`, `Diagnostic`, `SourceRef`, `stable_id`), deterministic IO, case persistence, and the application/CLI split. Policy is data, not code: a versioned YAML file evaluated by pure functions. SDD state lives in committable Markdown artifacts under `docs/sdd/<FEATURE>/`; machine state stays under `.apiforge/`. The sandbox copies the tree, applies a unified diff, re-runs the plan-1 analysis on both copies and reports the finding delta — it never executes project code and never writes the main tree. The evidence receipt stores only paths and SHA-256 hashes and states exactly what it proves.

**Tech Stack:** Python 3.12, Pydantic 2, Typer, PyYAML, pytest, Ruff, mypy, Hatchling. No new runtime dependencies.

**Spec:** `docs/specs/2026-09-21-api-forge-design.md` (§6 SDD adaptativo, §10 release evidence, §11 autonomia e políticas, §12 CLI e estado)

**Depends on:** `docs/plans/2026-09-21-api-forge-mvp-vertical-slice.md` — all of its public interfaces must exist before Task 3.

## Global Constraints

- Every refusal is named: a `AF-*` code, the `field` that is wrong, and an `unlock` telling the operator what to do. Silence and guessing are both failures.
- `irreversible` actions are denied by default; `destructive` requires exact target, impact, dry-run or the reason it is impossible, rollback, and explicit confirmation. Ambiguity produces `deny` with a named reason, never an inferred class.
- SDD artifacts form a hash cascade: each phase stamps the SHA-256 of its upstream artifact; `sdd check` reports `AF-SDD-UPSTREAM-STALE` instead of letting a validated phase be silently reused after upstream changes.
- A dispensed phase is recorded as `not_required` with rule and justification — never skipped silently (spec §6).
- The sandbox refuses before the first byte is written and leaves `main_tree_touched: false` in every report.
- The evidence receipt carries no implicit wall-clock: `--now` is the only time source, so unchanged inputs still produce byte-identical artifacts.
- Text hashes normalize CRLF to LF — the checkout may be on Windows.
- Catalogs (`gates.yaml`, `profiles.yaml`, rule metadata) ship as package data inside `apiforge.*` packages, not as top-level directories.
- Keep files focused; production modules below 300 lines unless a reviewer approves an exception. TDD and commit after every task.

## Review Focus

- Frontmatter and policy YAML must go through the hardened loader from plan 1 (aliases, custom tags, duplicate keys rejected); Task 1 moves it into `core` for reuse.
- `sdd stamp` must write only the upstream hash line — never reformat or reorder the artifact; Task 4 pins this.
- Gate satisfaction is decided by the presence of declared evidence (a fact kind or a hashed artifact), never by a `--gate-ok` flag; Task 5 pins this.
- The sandbox's before/after copies must prune `.git`, `.apiforge`, `.venv`, `__pycache__` and dependency directories, with every skip named in `copy_skipped`; Task 6 pins this.
- The receipt states `proves: correspondence between this receipt and these artifacts — never authorship`; Task 8 pins this.
- Exit codes stay consistent with plan 1: 2 for usage/input errors, 3 for integrity/internal failures, 4 for `--fail-on` findings; `sdd check` additionally exits 1 when refusals exist and 0 when only gaps remain.

---

## Delivery sequence position

This is item 1 of the delivery sequence in the MVP plan (`docs/plans/2026-09-21-api-forge-mvp-vertical-slice.md`). It deliberately excludes: FastAPI build/verify execution (plan 3), Spring Boot and Go adapters, any AWS or Terraform verb, MCP, and LLM-backed phases. SDD `build`/`verify` phases here validate artifact structure and evidence references — the verbs that produce that evidence arrive with their own plans.

### Task 1: Promote hardened YAML loading and text hashing to core

**Files:**
- Create: `src/apiforge/core/yaml.py`
- Modify: `src/apiforge/openapi/loader.py`
- Modify: `src/apiforge/core/io.py`
- Create: `tests/core/test_yaml.py`

**Interfaces:**
- Consumes: plan-1 `OpenApiLoadError` behavior (unchanged for callers).
- Produces: `load_yaml_strict(text: str, *, source: str) -> object` raising `StrictYamlError(code, message)`; `split_frontmatter(text: str) -> tuple[str | None, str]`; `text_sha256(path: Path) -> str` (CRLF-normalized).

- [ ] **Step 1: Write failing core YAML tests**

```python
import pytest
from apiforge.core.yaml import StrictYamlError, load_yaml_strict, split_frontmatter


def test_rejects_alias() -> None:
    with pytest.raises(StrictYamlError, match="AF-YAML-ALIAS"):
        load_yaml_strict("a: &x 1\nb: *x\n", source="inline")


def test_rejects_duplicate_key() -> None:
    with pytest.raises(StrictYamlError, match="AF-YAML-DUPLICATE-KEY"):
        load_yaml_strict("a: 1\na: 2\n", source="inline")


def test_frontmatter_tolerates_utf8_bom() -> None:
    block, body = split_frontmatter("﻿---\nkey: 1\n---\nbody\n")
    assert block == "key: 1\n"
    assert body == "body\n"
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/core/test_yaml.py -v`  
Expected: FAIL because `apiforge.core.yaml` is absent.

- [ ] **Step 3: Move the hardened loader into core**

Move the `SafeLoader` subclass (alias/merge-key, custom-tag and duplicate-key rejection) out of `apiforge.openapi.loader` into `apiforge.core.yaml` behind `load_yaml_strict`, with distinct codes `AF-YAML-ALIAS`, `AF-YAML-CUSTOM-TAG`, `AF-YAML-DUPLICATE-KEY`, `AF-YAML-INVALID`, `AF-YAML-NOT-MAPPING`. `openapi/loader.py` now calls it and maps the codes to `AF-OPENAPI-INVALID-YAML` — existing Task-4 tests must pass unchanged. `split_frontmatter` returns `(None, text)` when the `---` fence never opens or never closes, tolerating one leading UTF-8 BOM. Add `text_sha256` to `core/io.py`: read bytes, replace `\r\n` with `\n`, hash.

- [ ] **Step 4: Run regression and commit**

Run: `pytest tests/core tests/openapi -q && mypy src/apiforge/core src/apiforge/openapi`  
Expected: PASS — no behavior change for OpenAPI loading.

```bash
git add src/apiforge/core src/apiforge/openapi tests/core
git commit -m "refactor: promote strict yaml loading and text hashing to core"
```

### Task 2: Policy file schema and loader

**Files:**
- Create: `src/apiforge/policy/models.py`
- Create: `src/apiforge/policy/loader.py`
- Create: `src/apiforge/policy/__init__.py`
- Create: `tests/policy/test_loader.py`
- Create: `tests/fixtures/policy/full.yaml`

**Interfaces:**
- Consumes: `load_yaml_strict`, frozen models.
- Produces: `AutonomyClass`, `Policy`, `PolicyRule`, `load_policy(path: Path | None) -> Policy`, `DEFAULT_POLICY`.

- [ ] **Step 1: Write failing policy tests**

```python
import pytest
from apiforge.policy.loader import PolicyLoadError, load_policy


def test_default_policy_denies_irreversible() -> None:
    policy = load_policy(None)
    assert policy.defaults["irreversible"] == "deny"
    assert policy.defaults["destructive"] == "gate"


def test_unknown_top_key_is_named() -> None:
    path = tmp_path / "policy.yaml"  # contains "surprise: true"
    with pytest.raises(PolicyLoadError, match="AF-POLICY-SCHEMA"):
        load_policy(path)


def test_gate_requirements_are_closed() -> None:
    policy = load_policy(FIXTURES / "full.yaml")
    assert policy.gates["destructive"] == (
        "exact_target",
        "impact",
        "dry_run_or_reason",
        "rollback",
        "confirmation",
    )
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/policy/test_loader.py -v`  
Expected: FAIL because the module is absent.

- [ ] **Step 3: Implement the closed schema**

`AutonomyClass` StrEnum: `read_only`, `local_reversible`, `sensitive`, `external_mutation`, `destructive`, `irreversible` (spec §11). Policy YAML shape:

```yaml
version: 1
defaults:            # outcome when no rule matches; every class must appear
  read_only: allow
  local_reversible: allow
  sensitive: gate
  external_mutation: gate
  destructive: gate
  irreversible: deny
gates:
  destructive: [exact_target, impact, dry_run_or_reason, rollback, confirmation]
rules:
  - name: no-force-push
    match: {verb: "git.push", arg_glob: "--force*"}
    decision: deny
    reason: "rewrites shared history"
```

Closed vocabulary: unknown keys, unknown classes, decisions outside `allow|gate|deny`, or `version != 1` each produce `PolicyLoadError("AF-POLICY-SCHEMA", field)`. `load_policy(None)` returns `DEFAULT_POLICY` — a code-defined object identical to the YAML above, so the engine never runs without policy. Lookup order: `--policy` flag, then `apiforge.policy.yaml`, then `.apiforge/policy.yaml`, then default.

- [ ] **Step 4: Run checks and commit**

Run: `pytest tests/policy -v && mypy src/apiforge/policy`  
Expected: PASS.

```bash
git add src/apiforge/policy tests/policy tests/fixtures/policy
git commit -m "feat: load versioned closed-schema autonomy policy"
```

### Task 3: Policy decision engine

**Files:**
- Create: `src/apiforge/policy/decide.py`
- Create: `tests/policy/test_decide.py`

**Interfaces:**
- Consumes: `Policy`, `AutonomyClass`.
- Produces: `ActionRequest`, `PolicyDecision`, `decide(policy, action) -> PolicyDecision`.

- [ ] **Step 1: Write failing decision tests**

```python
from apiforge.policy.decide import ActionRequest, decide
from apiforge.policy.loader import DEFAULT_POLICY


def test_unknown_class_is_denied_by_name() -> None:
    d = decide(DEFAULT_POLICY, ActionRequest(verb="x", autonomy_class="bogus"))
    assert d.outcome == "deny"
    assert d.reason_code == "AF-POLICY-CLASS-UNKNOWN"


def test_destructive_lists_missing_requirements() -> None:
    d = decide(DEFAULT_POLICY, ActionRequest(verb="fs.delete", autonomy_class="destructive"))
    assert d.outcome == "gate"
    assert "exact_target" in d.missing_requirements


def test_deny_rule_beats_default_allow() -> None:
    d = decide(
        DEFAULT_POLICY,
        ActionRequest(verb="git.push", autonomy_class="local_reversible", args=("--force",)),
    )
    assert d.outcome == "deny"
    assert d.rule == "no-force-push"
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/policy/test_decide.py -v`  
Expected: FAIL.

- [ ] **Step 3: Implement pure decision**

`ActionRequest` is frozen: `verb`, optional `autonomy_class`, `args` tuple, optional `target`, `detail`. Evaluate in order: rules first-match by `verb` plus `arg_glob` (fnmatch, case-sensitive); then the class default. Outcomes: `allow`, `gate` (with `missing_requirements` computed from `policy.gates[class]` minus supplied `detail` keys), `deny` (with `reason_code`). Missing/unknown class → `deny` + `AF-POLICY-CLASS-UNKNOWN`. A `gate` outcome with zero missing requirements becomes `allow` only when the caller supplies evidence fields — the engine records which fields satisfied the gate, it never self-satisfies. Every decision is a frozen `PolicyDecision` with `outcome`, `rule`, `reason_code`, `missing_requirements`, `subject`.

- [ ] **Step 4: Run checks and commit**

Run: `pytest tests/policy -v && mypy src/apiforge/policy`  
Expected: PASS.

```bash
git add src/apiforge/policy/decide.py tests/policy/test_decide.py
git commit -m "feat: decide action autonomy deterministically"
```

### Task 4: SDD artifact model, discovery and stamp verb

**Files:**
- Create: `src/apiforge/sdd/models.py`
- Create: `src/apiforge/sdd/load.py`
- Create: `src/apiforge/sdd/stamp.py`
- Create: `src/apiforge/sdd/__init__.py`
- Create: `src/apiforge/sdd/profiles.yaml` (package data)
- Create: `tests/sdd/test_load.py`
- Create: `tests/sdd/test_stamp.py`
- Create: `tests/fixtures/sdd/DEMO_FEATURE/discover.md`

**Interfaces:**
- Consumes: `split_frontmatter`, `load_yaml_strict`, `text_sha256`, `write_json`.
- Produces: `PHASES`, `SddArtifact`, `FeatureDiscovery`, `discover_features(root) -> FeatureDiscovery`, `load_artifact(path) -> SddArtifact`, `stamp(path) -> StampResult`.

- [ ] **Step 1: Write failing load/stamp tests**

```python
def test_discovers_only_uppercase_feature_dirs() -> None:
    found = discover_features(Path("tests/fixtures/sdd_root"))
    assert "DEMO_FEATURE" in found.features
    assert found.features["DEMO_FEATURE"]["discover"].name == "discover.md"
    assert any(s.name == "templates" for s in found.skipped)


def test_stamp_writes_only_upstream_line(tmp_path: Path) -> None:
    upstream = tmp_path / "discover.md"
    target = tmp_path / "define.md"
    # write both, stamp target, then diff line count and non-upstream bytes
    result = stamp(target, upstream)
    assert result.changed is True
    assert target.read_text().count("\n") == BEFORE_LINE_COUNT
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/sdd -v`  
Expected: FAIL.

- [ ] **Step 3: Implement artifacts, profiles and stamping**

`PHASES = (discover, intent, contract, architecture, plan, build, verify, secure, benchmark, ship)` — the spec §6 pipeline. `SddArtifact` = frozen `{path, meta, body, error}`; meta must be a mapping or the artifact carries `error` naming `AF-SDD-FRONTMATTER`. Feature dirs match `^[A-Z0-9_]+$`; anything else under the root (`templates/`, `archive/`, stray files) lands in `skipped` with a reason — never silently dropped. `profiles.yaml` maps each profile to its required phases: `quick` → `intent, plan, build, verify, ship`; `standard` → all except `benchmark`; `critical` and `migration` → all ten. `stamp(path, upstream)` rewrites exactly the `upstream:` block in the target's frontmatter to `{path: <relative posix>, sha256: <text_sha256>}`, returns `{path, upstream, sha256, previous, changed}`, and refuses (`AF-SDD-STAMP`) when the artifact has no frontmatter or the upstream file does not exist.

- [ ] **Step 4: Run checks and commit**

Run: `pytest tests/sdd -v && mypy src/apiforge/sdd`  
Expected: PASS.

```bash
git add src/apiforge/sdd tests/sdd tests/fixtures/sdd
git commit -m "feat: discover sdd artifacts and stamp upstream hashes"
```

### Task 5: SDD check, status, gates and phase transitions

**Files:**
- Create: `src/apiforge/sdd/checks.py`
- Create: `src/apiforge/sdd/gates.yaml` (package data)
- Create: `src/apiforge/sdd/service.py`
- Create: `tests/sdd/test_checks.py`
- Create: `tests/fixtures/sdd_root/<features>` covering ready, stale and gapped states

**Interfaces:**
- Consumes: `FeatureDiscovery`, `SddArtifact`, `profiles.yaml`, `gates.yaml`, `text_sha256`.
- Produces: `check(root, feature=None, strict=False) -> SddReport`, `status(root) -> SddStatus`, `set_phase(feature, phase, status, strict, overrides) -> PhaseChange`.

- [ ] **Step 1: Write failing check tests**

```python
def test_upstream_stale_is_named_with_unlock(sdd_root) -> None:
    report = check(sdd_root)
    refusal = next(r for r in report.refused if r.code == "AF-SDD-UPSTREAM-STALE")
    assert refusal.field == "upstream.sha256"
    assert "stamp" in refusal.unlock


def test_gap_allowed_at_ready_forbidden_at_done(sdd_root) -> None:
    report = check(sdd_root, feature="GAPPED_FEATURE")
    assert any(u.code == "AF-SDD-GAP-TEST-NOT-WRITTEN" for u in report.unresolved)
    assert not report.ok  # done requires zero gaps


def test_skipped_phase_must_be_declared(sdd_root) -> None:
    report = check(sdd_root, feature="SILENT_SKIP")
    assert any(r.code == "AF-SDD-PHASE-SKIPPED-UNDECLARED" for r in report.refused)
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/sdd/test_checks.py -v`  
Expected: FAIL.

- [ ] **Step 3: Implement the checker and gates**

Common frontmatter: `sdd: 1`, `feature` (= dir name), `phase` (= file name), `profile`, `status` ∈ `draft|ready|done|superseded`, `upstream: {path, sha256}` (required on every phase except `discover`). Per-phase required fields — authoritative list lives in the contract doc (Task 10): `discover` → `approaches`, `chosen`; `intent` → `problem`, `success[]`, `out_of_scope`; `contract` → `covers`, optional `api_ir`; `architecture` → `files`, `decisions[]` (`rollback` required per decision); `plan` → `tasks[]` each with `covers` and `test` or `proof`; `build` → `tasks[].status`, `claims`; `verify` → `results`; `secure` → `threat_model`; `benchmark` → `baseline`, `results`; `ship` → `deviations`, `evidence[]` of `{path, sha256}`.

Refusals: `AF-SDD-SCHEMA-INVALID`, `AF-SDD-PHASE-ORDER`, `AF-SDD-UPSTREAM-MISSING`, `AF-SDD-UPSTREAM-STALE`, `AF-SDD-ACCEPTANCE-UNCOVERED`, `AF-SDD-TASK-WITHOUT-TEST`, `AF-SDD-PHASE-SKIPPED-UNDECLARED`, `AF-SDD-EVIDENCE-MISMATCH` (ship evidence hash diverges from file). Gaps (allowed at `ready`, blocking `done`): `AF-SDD-GAP-TEST-NOT-WRITTEN`, `AF-SDD-GAP-FACT-NOT-COLLECTED`, `AF-SDD-GAP-FINDING-NOT-OBSERVED`. `gates.yaml` declares gate → `{satisfied_by, produced_by, guards_phases}`; under `strict`, `set_phase` refuses a transition into a guarded phase while its evidence kind is absent from the case, and `set_phase(..., override={gate, reason, actor})` records the bypass inside `.apiforge/sdd/<FEATURE>/gate-overrides.json` — data, not a flag. `check` output shape: `{ok, root, features, refused[], unresolved[]}`; `ok` requires zero refusals and zero gaps.

- [ ] **Step 4: Run checks and commit**

Run: `pytest tests/sdd -v && mypy src/apiforge/sdd`  
Expected: PASS.

```bash
git add src/apiforge/sdd tests/sdd tests/fixtures/sdd_root
git commit -m "feat: check sdd phase cascade and evidence gates"
```

### Task 6: Copy-based change sandbox

**Files:**
- Create: `src/apiforge/sandbox/diff.py`
- Create: `src/apiforge/sandbox/models.py`
- Create: `src/apiforge/sandbox/service.py`
- Create: `src/apiforge/sandbox/__init__.py`
- Create: `tests/sandbox/test_diff.py`
- Create: `tests/sandbox/test_service.py`
- Create: `tests/fixtures/sandbox_project/` (a minimal FastAPI tree reusing `fastapi_flat`)

**Interfaces:**
- Consumes: `sha256_file`, `write_json`, and the plan-1 analysis callable (injected — this module never imports adapters directly).
- Produces: `parse_unified_diff(text) -> tuple[Patch, ...]`, `sandbox_apply(root, diff_text, analyze) -> SandboxReport`, `sandbox_clean(root) -> dict`, `SandboxError` codes.

- [ ] **Step 1: Write failing diff and sandbox tests**

```python
def test_diff_path_outside_copy_is_refused(tmp_path, analyze_stub) -> None:
    report = sandbox_apply(tmp_path, DIFF_TOUCHING_EVIL_PY, analyze_stub)
    assert report["applied"] is False
    assert report["refused"][0]["code"] == "AF-SANDBOX-PATH-OUTSIDE"


def test_sandbox_reports_finding_delta(sandbox_project, analyze) -> None:
    report = sandbox_apply(sandbox_project, DIFF_ADDING_ROUTE, analyze)
    assert report["applied"] and report["main_tree_touched"] is False
    assert {f["rule_id"] for f in report["new"]}
    assert report["id"] == sandbox_apply(sandbox_project, DIFF_ADDING_ROUTE, analyze)["id"]
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/sandbox -v`  
Expected: FAIL.

- [ ] **Step 3: Implement bounded diff and two-copy evaluation**

`parse_unified_diff` handles `---`/`+++`/`@@` hunks for create/modify/delete; binary patches and mode-only changes are refused by name (`AF-SANDBOX-BINARY-PATCH`, `AF-SANDBOX-MODE-ONLY`). `sandbox_apply` inventories the root (relative path → sha256, skipping `.git`, `.apiforge`, `.venv`, `__pycache__`, `node_modules`, `dist`, `build` — each skip recorded in `copy_skipped`), verifies every patched path exists in the inventory before writing anything, computes `sandbox_id = sha256(diff_bytes + manifest)[:16]`, then creates `.apiforge/sandbox/<id>/{before,after}` — the main tree is never opened for write. The injected `analyze` callable runs identically on both copies; the report contains `applied`, `main_tree_touched: false`, `files_changed`, findings `new`/`resolved`/`kept_count`, `moved_candidates`, `next_steps` (name the missing measurement — never assert improvement), and `scan_refused` propagated per side. Re-running with the same diff yields the same `id` and replaces the directory atomically. `sandbox_clean` removes only `.apiforge/sandbox` and reports the removed ids.

- [ ] **Step 4: Run checks and commit**

Run: `pytest tests/sandbox -v && mypy src/apiforge/sandbox`  
Expected: PASS.

```bash
git add src/apiforge/sandbox tests/sandbox tests/fixtures/sandbox_project
git commit -m "feat: evaluate diffs in an isolated two-copy sandbox"
```

### Task 7: Git worktree isolation

**Files:**
- Create: `src/apiforge/sandbox/worktree.py`
- Create: `tests/sandbox/test_worktree.py`

**Interfaces:**
- Consumes: `decide` (worktree ops are `local_reversible`), git CLI via `subprocess` with no shell.
- Produces: `worktree_create(root, name) -> WorktreeInfo`, `worktree_list(root) -> tuple[WorktreeInfo, ...]`, `worktree_remove(root, name) -> None`.

- [ ] **Step 1: Write failing worktree tests**

```python
def test_refuses_when_not_a_git_repo(tmp_path: Path) -> None:
    with pytest.raises(WorktreeError, match="AF-WORKTREE-NO-GIT"):
        worktree_create(tmp_path, "feature-x")


def test_create_and_remove_roundtrip(git_repo: Path) -> None:
    info = worktree_create(git_repo, "feature-x")
    assert info.branch == "apiforge/feature-x"
    assert Path(info.path).is_dir()
    worktree_remove(git_repo, "feature-x")
    assert not Path(info.path).exists()
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/sandbox/test_worktree.py -v`  
Expected: FAIL.

- [ ] **Step 3: Implement worktree wrapper**

Worktrees live under `.apiforge/worktrees/<name>` on branch `apiforge/<name>`; `name` must match `^[a-z0-9-]+$`. Use `git -C <root> worktree add ...` with argument arrays — never `shell=True`. Refusals: `AF-WORKTREE-NO-GIT` (no repo or no binary), `AF-WORKTREE-NAME-INVALID`, `AF-WORKTREE-EXISTS`, `AF-WORKTREE-DIRTY` (remove only with `--force` recorded). Persist `.apiforge/worktrees/index.json` (name, branch, head sha, path) via `write_json`; `worktree_list` reconciles the index against `git worktree list --porcelain` and reports drift instead of hiding it.

- [ ] **Step 4: Run checks and commit**

Run: `pytest tests/sandbox -v && mypy src/apiforge/sandbox`  
Expected: PASS.

```bash
git add src/apiforge/sandbox/worktree.py tests/sandbox/test_worktree.py
git commit -m "feat: isolate change work in git worktrees"
```

### Task 8: Release evidence receipt — emit and verify

**Files:**
- Create: `src/apiforge/evidence/models.py`
- Create: `src/apiforge/evidence/build.py`
- Create: `src/apiforge/evidence/verify.py`
- Create: `src/apiforge/evidence/__init__.py`
- Create: `tests/evidence/test_receipt.py`

**Interfaces:**
- Consumes: `CaseManifest`/`load_case`, SDD `check` results, sandbox reports, `text_sha256`, `write_json`.
- Produces: `EvidenceReceipt`, `emit_receipt(root, out, now=None) -> EvidenceReceipt`, `verify_receipt(root, path) -> Verification`.

- [ ] **Step 1: Write failing receipt tests**

```python
def test_receipt_is_deterministic_without_now(case_dir: Path) -> None:
    a = emit_receipt(case_dir, case_dir / "r1.json")
    b = emit_receipt(case_dir, case_dir / "r2.json")
    assert a.receipt_id == b.receipt_id
    assert a.emitted_at is None


def test_verify_names_the_diverged_part(case_dir: Path, receipt_path) -> None:
    (case_dir / "findings.json").write_text("{}")  # tamper after emit
    result = verify_receipt(case_dir, receipt_path)
    assert result.ok is False
    assert result.diverged[0].part == "evidence"
    assert result.diverged[0].path == "findings.json"
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/evidence -v`  
Expected: FAIL.

- [ ] **Step 3: Implement correspondence receipt**

The receipt stores `{path, sha256}` per artifact — never content — covering: the case manifest and every artifact it declares, `docs/sdd/` feature index with per-artifact hashes, `.apiforge/sandbox/*/report.json`, and the policy file used. Shape: `{receipt_version: 1, emitted_at: <only when --now given>, case, sdd[], sandbox[], policy, unresolved[], refused[], proves, receipt_id}`. Missing inputs land in `unresolved` with named reasons (`AF-EVIDENCE-CASE-ABSENT`, `AF-EVIDENCE-SDD-INCOMPLETE`); `refused` always carries the two fixed entries `authorship`/`content_addressed_sem_chave`-equivalent → use codes `AF-EVIDENCE-NO-AUTHORSHIP` and `AF-EVIDENCE-NO-TOOL-IO`. `proves` is the literal string `"correspondence between this receipt and these artifacts — never authorship"`. `receipt_id` = `stable_id("receipt", doc-minus-id)`. `verify_receipt` recomputes every declared hash and reports `diverged[]` entries `{part, path, expected, actual}` — it names which part diverged (evidence, sdd, sandbox, policy, or receipt_id), never just "invalid".

- [ ] **Step 4: Run checks and commit**

Run: `pytest tests/evidence -v && mypy src/apiforge/evidence`  
Expected: PASS.

```bash
git add src/apiforge/evidence tests/evidence
git commit -m "feat: emit and verify release evidence receipts"
```

### Task 9: Wire policy, SDD, sandbox, worktree and evidence into the CLI

**Files:**
- Modify: `src/apiforge/cli.py`
- Create: `src/apiforge/application/sdd_service.py`
- Create: `src/apiforge/application/sandbox_service.py`
- Create: `src/apiforge/application/evidence_service.py`
- Create: `tests/e2e/test_governance_slice.py`

**Interfaces:**
- Consumes: every interface above plus plan-1 application services.
- Produces: CLI groups `sdd` (`check`, `status`, `stamp`, `set-phase`, `new`), `policy` (`check`), `sandbox` (`apply`, `clean`), `worktree` (`create`, `list`, `remove`), `evidence` (`emit`, `verify`), and `release check`.

- [ ] **Step 1: Write failing CLI tests**

```python
def test_sdd_check_exit_codes(sdd_root: Path) -> None:
    refused = runner.invoke(app, ["sdd", "check", "--root", str(sdd_root / "BROKEN")])
    assert refused.exit_code == 1
    missing = runner.invoke(app, ["sdd", "check", "--root", str(sdd_root), "--feature", "NOPE"])
    assert missing.exit_code == 2


def test_policy_check_roundtrip() -> None:
    result = runner.invoke(
        app, ["policy", "check", "--verb", "fs.delete", "--class", "destructive", "--json"]
    )
    assert result.exit_code == 0
    assert '"outcome": "gate"' in result.stdout
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/e2e/test_governance_slice.py -v`  
Expected: FAIL because commands are absent.

- [ ] **Step 3: Implement application services and commands**

One application function per verb; CLI commands are thin adapters printing compact JSON to stdout and diagnostics to stderr. `sdd check` exits 1 on refusals, 0 with gaps only, 2 for unknown `--feature` or missing root. `sdd stamp <artifact>` prints the stamp record. `sdd set-phase` requires `--strict` to enforce gates and `--override <gate> --reason <why>` to bypass, writing the override record. `sdd new <FEATURE>` scaffolds `docs/sdd/<FEATURE>/discover.md` from a package-data template with `status: draft`. `policy check` runs `decide` on the described action. `sandbox apply --diff <file>` injects the plan-1 `analyze_project` pipeline; `worktree` commands call Task 7; `evidence emit --case <dir> [--now ISO]` and `evidence verify <receipt>`. `release check` composes: `sdd check` for the feature, `load_case` integrity, and `verify_receipt` — exit 1 naming every failure, exit 0 printing `release check: PASS`.

- [ ] **Step 4: Run full verification and commit**

Run: `pytest -q && ruff check src tests && ruff format --check src tests && mypy src/apiforge`  
Expected: all PASS.

```bash
git add src/apiforge/application src/apiforge/cli.py tests/e2e
git commit -m "feat: wire sdd policy sandbox and evidence commands"
```

### Task 10: Contract doc, threat model update and extended release gate

**Files:**
- Create: `docs/contracts/sdd-contract.md`
- Create: `docs/contracts/policy-contract.md`
- Create: `docs/decisions/ADR-003-policy-as-data.md`
- Create: `docs/decisions/ADR-004-hash-cascade.md`
- Create: `docs/decisions/ADR-005-correspondence-not-authorship.md`
- Modify: `docs/security/threat-model-mvp.md`
- Modify: `scripts/check_mvp_release.py` → rename `scripts/check_release.py`
- Modify: `tests/scripts/test_check_mvp_release.py` → rename accordingly
- Create: `docs/sdd/templates/` one valid artifact per phase

**Interfaces:**
- Consumes: the refusal/gap code vocabulary emitted by Tasks 4–8.
- Produces: an AST-locked contract doc and an extended release gate.

- [ ] **Step 1: Write failing contract-coverage and gate tests**

```python
def test_every_refusal_code_is_documented() -> None:
    codes = collect_codes_via_ast(Path("src/apiforge"))  # literals passed to errors
    documented = parse_contract_codes(Path("docs/contracts"))
    assert codes <= documented


def test_release_gate_covers_governance() -> None:
    failures = check_repository(Path("."))
    assert failures == []
```

- [ ] **Step 2: Verify failure**

Run: `pytest tests/scripts -v`  
Expected: FAIL.

- [ ] **Step 3: Write the contract docs and templates**

`sdd-contract.md` documents every field per phase, every `AF-SDD-*` code with when it fires and its `unlock`, and the gap taxonomy; a test extracts every code literal handed to `SddError`/`refused`/`unresolved` in `src/apiforge/sdd` via `ast` and requires set equality with the doc's code table — code without a doc line, or a doc line without code, fails. `policy-contract.md` does the same for `AF-POLICY-*` plus the schema. ADRs record: policy-as-data (rules in YAML, evaluation in pure functions), the hash cascade (validated state is never silently reused), and correspondence-not-authorship (the receipt proves hashes match, not who wrote them). `docs/sdd/templates/` holds one valid artifact per phase for `sdd new`.

- [ ] **Step 4: Extend the threat model and release gate**

Add to the threat model: policy file tampering (hash the active policy into the receipt), sandbox escape via crafted diff paths or symlinks inside the copied tree, frontmatter injection, gate override abuse (the override record is the audit), and worktree confusion between index and `git worktree list`. Rename the release gate to `check_release.py` and extend `check_repository` to verify: contract docs exist and their code sets equal the AST-extracted sets, `profiles.yaml` covers all four profiles, `gates.yaml` references only known evidence kinds, `docs/sdd/templates/` parses clean under `sdd check`, and the receipt round-trips on the plan-1 fixture case. Print each failure; exit 1 on any, else print `API Forge release gate: PASS` and exit 0. Update the README command table for the new groups.

- [ ] **Step 5: Run final gate and commit**

Run: `pytest -q && python scripts/check_release.py`  
Run: `ruff check . && ruff format --check . && mypy src/apiforge`  
Expected: all PASS.

```bash
git add docs scripts tests README.md src/apiforge
git commit -m "docs: lock sdd and policy contracts and extend release gate"
```

## Amendments and open questions

Decisions taken while writing this plan — revisit at execution if they fight the code:

- SDD artifacts live in `docs/sdd/<FEATURE>/` (committable by default), while machine state — overrides, worktree index, sandbox copies — stays under `.apiforge/`. If the operator-profile split from spark-forge becomes real, `--root` already accepts an alternate root.
- The receipt omits `emitted_at` unless `--now` is passed; reproducibility beats convenience. A case-level timestamp can be added later as input-derived data.
- `gates.yaml` starts with presence-of-kind satisfaction only; content-level gates (e.g. "benchmark compares the same workload") are named as unresolved until a later plan owns them.
- The sandbox reuses the plan-1 analysis as an injected callable so `apiforge.sandbox` never imports adapters — the same seam later plans use for Spring Boot and Go.
- `sdd build`/`verify` phases validate artifact structure and evidence references only; the verbs that produce build/verify evidence (plan 3) will extend `gates.yaml`, not this code.

## Final acceptance

Run in a clean Python 3.12 environment on top of the completed MVP slice:

```bash
python -m pip install -e '.[dev]'
pytest -q
ruff check .
ruff format --check .
mypy src/apiforge
python scripts/check_release.py
apiforge sdd check --root docs/sdd
apiforge policy check --verb fs.delete --class destructive --json
apiforge evidence emit --case .apiforge/acceptance --out .apiforge/receipt.json
apiforge evidence verify --receipt .apiforge/receipt.json
git status --short
```

Acceptance requires all checks to pass, deterministic receipts on unchanged inputs, `sdd check` reporting only named gaps for the template feature, and `git status --short` showing no unintended changes.
