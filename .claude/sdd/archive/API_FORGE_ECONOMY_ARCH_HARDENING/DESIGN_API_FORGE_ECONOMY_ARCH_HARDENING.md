# DESIGN: API Forge Economy Architecture Hardening

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_ARCH_HARDENING |
| **Date** | 2026-09-28 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_ECONOMY_ARCH_HARDENING.md](./DEFINE_API_FORGE_ECONOMY_ARCH_HARDENING.md) |
| **Status** | ✅ Shipped |
| **Branch** | `codex/new-economy-arch` |

---

## Architecture Overview

```text
                       H1 TRUST BOUNDARY
case.json/facts/graph ──> case.service.load_case() (manifest, containment, re-hash)
        │                          │
        │                 case.service.load_verified_case()  ← only case reader
        ▼                          ▼
 inputs.project / fact.source.path / node.props.path
        │
        ▼
 security.source_paths.resolve_allowed_source(candidate, AllowedRoots)
   roots = project root + WorkspaceManifest repositories
   refuse: absolute outside roots, "..", drive/UNC, symlink escape
        │ ok                         │ refused
        ▼                            ▼
 gateway / evidence / delta     unresolved "AF-PATH-OUTSIDE-ROOT:<ref>" (never read, never ctx://)

                       H2 BUDGET + ACCOUNTING
BudgetEnvelope.context_bytes ─> class pools (share × total) ─> instances (pool ÷ n)
RoleContextPlan  validator: total_bytes ≤ context_bytes, row.bytes ≤ row.budget_bytes
ControlPlane.start / record_call(kind)  ← primary, review, fallback, shadow
ControlRun.calls_by_kind + validator  sum == calls_used ≤ max_calls
economy_checkpoint.json ← ControlRun (single source of truth)
run_ledger.stats ─> TokenCoverage{status, observed_rows, eligible_rows}
run_ledger.append(auditable=True) ─> persist failure recorded as unresolved

                       H3 PROOF + CACHE
step "ran" ─> proofs[] {proof_id, kind, sha256, artifact_ref}
deterministic_proof ─> match kind/id → resolve artifact (H1) → re-hash → L0
CacheStore.lookup: local stale/corrupt → continue to shared → miss only if none fresh
CacheEntry validator: created_at/expires_at ISO-8601 → else corrupt miss
knowledge LRU key: (root, generation) ; generation = sha256(pack.yaml bytes + mtimes)

                       H4 REPORTING + EVALS + CI
PhaseBudgetPlan{quality_status, budget_status}
run summary/result: unresolved.routing
DeltaSlice.status: ready | degraded | unresolved (unmapped runtime path → degraded)
retrieval tokenizer: NFKC + casefold + \w
EconomyMatrix.claim_scope ; evals agentic-quality (recorded specialist outputs)
CI: auto-merge with APIFORGE_PR_TOKEN when set; scheduled main validation backstop
```

---

## Components

| Component | Purpose | Location |
|-----------|---------|----------|
| Source resolver | One containment check for every path read from case/graph data | `src/apiforge/security/source_paths.py` (new) |
| Verified case reader | Returns the gateway's dict shape from verified artifacts only | `src/apiforge/case/service.py::load_verified_case` |
| Gateway/evidence/delta | Consume verified case + resolver | `context/gateway/levels.py`, `capsule.py`, `evidence/resolve.py`, `context/delta.py` |
| Context pools | Global budget → class pool → instance | `runtime/role_context.py`, `contracts/selective.py` |
| Call accounting | Shadow through `ControlPlane`; per-kind counts | `runtime/control.py`, `runtime/supervisor.py` |
| Token coverage | complete/partial/unresolved | `economy/run_ledger.py`, `contracts/economy.py` |
| Structured proofs | L0 on receipts, not substrings | `runtime/economy.py`, `contracts/economy.py` |
| Cache fall-through | stale local → shared | `cache/store.py`, `contracts/cache.py` |
| Knowledge generation | invalidate LRU on disk change | `knowledge/selector.py`, `knowledge/retrieval.py` |
| Reporting | phase statuses, routing unresolved, delta degraded | `economy/phase_budget.py`, `runtime/supervisor.py`, `context/delta.py` |
| Evals | hardening corpus + agentic quality + claim scope | `evals/hardening.py`, `evals/agentic_quality.py`, `evals/matrix.py` |
| CI | CI on merged commits | `.github/workflows/ci.yml` |

---

## Key Decisions

### D1: One resolver, refuse per ref

**Status:** Accepted

**Context:** Three modules join untrusted strings (`inputs.project`, `source.path`, `props.path`) onto the root.

**Choice:** `resolve_allowed_source(candidate: str, roots: AllowedRoots, *, base: Path) -> Path` raises `SourcePathError(code="AF-PATH-OUTSIDE-ROOT", field, unlock)`. Rules: reject drive-qualified or UNC strings (`PureWindowsPath(c).drive`) and POSIX absolute paths unless the resolved path is inside a root; reject `..` components; `resolve(strict=False)` then `relative_to` one root; if any existing component is a symlink, the resolved target must still be inside a root. `AllowedRoots.for_project(root)` = project root + `WorkspaceManifest.repositories[*].path` when `.apiforge/workspace.yaml` exists (declared only). Callers catch the error and append `AF-PATH-OUTSIDE-ROOT:<ref>` to `unresolved`; the file is never opened.

**Alternatives Rejected:**
1. Refuse the whole command — one poisoned fact would DoS analysis (user decision).
2. Per-module checks — the bug is precisely duplicated logic.

**Consequences:** `inputs.project` outside roots makes code-level selection unresolved but the capsule still serves contract/fact refs.

### D2: Gateway reads cases only through the case service

**Choice:** Add `load_verified_case(case_dir) -> dict | None` in `case/service.py`: missing manifest → `None` (current gateway semantics); otherwise `load_case()` (re-hash, containment) then read each verified artifact by its manifest ref. `levels.load_case` is deleted and its import sites switch. `CaseIntegrityError` is mapped to `GatewayError(code, field="case", unlock="re-run apiforge analyze")`.

**Rejected:** keep a gateway loader that calls `load_case` first — still two readers.

**Consequences:** A tampered `facts.json` refuses the capsule with `AF-CASE-HASH-MISMATCH` (full refusal, per DEFINE).

### D3: Class pools, validators on contracts

**Choice:** Pool for class = `int(share × context_bytes)`; each instance of that class gets `pool // n_instances` (remainder to the first instance). `RoleContextPlan` gains `model_validator`: `total_bytes == sum(roles.bytes)`, `total_bytes ≤ context_bytes`, each `bytes ≤ budget_bytes`. `RoleContext` gains `pool_bytes`. Selective-agentics eval adds the absolute gate `total_bytes ≤ context_bytes`.

**Rejected:** test-only check — the review asks for invariants.

### D4: ControlPlane is the only call counter

**Choice:** `ControlRun` gains `calls_by_kind: dict[str,int]` (additive, default `{}`) with validator `sum(values) ≤ calls_used ≤ max_calls` for new runs; `start()` records kind from the step name/role (`primary|review|fallback|critic`) and new `record_call(run_id, kind="shadow")` increments `calls_used` atomically, emits `call_recorded`, refuses with `AF-BUDGET-EXHAUSTED` when `calls_used ≥ max_calls`. `_shadow` calls `record_call` before invoking; refusal → `ShadowDecision(executed=False, reason="AF-BUDGET-EXHAUSTED")`. Checkpoint reads `calls_used` from `ControlRun` (already) — now true. `ShadowDecision` gains `mode: Literal["paired_ab","capability_eval"] = "paired_ab"`; `capability_eval` builds the challenger's own row via `plan_roles` for `(challenger, "specialist")` within the shadow pool.

**Rejected:** separate usage counters — two sources drift.

### D5: Token coverage

**Choice:** `TokenCoverage(status, observed_rows, eligible_rows)` contract; eligible rows = attribution rows with `source` in model-facing sources (`runtime role:*`, `provider`, `transcript`) — rows from deterministic verbs are not eligible. `stats` reports `token_coverage` and `observed_tokens` as `{value, coverage}`; `tokens_unresolved` is `true` unless coverage is `complete`. `append(..., auditable=False)` keeps best-effort; `auditable=True` returns `False` on `OSError` and writes a sidecar marker `economy.persist-failures` when possible; `stats` exposes `persist_failures` and adds `AF-ECONOMY-LEDGER-PERSIST` to `unresolved`. Runtime role rows use `auditable=True`.

### D6: Structured proofs for L0

**Choice:** `ProofReceipt(proof_id, kind, sha256, artifact_ref)` contract. A task step may carry `proofs: [...]`. `expected_proofs` entries match a receipt when equal to its `kind` or `proof_id`. L0 requires: all expected matched, each `artifact_ref` resolves via D1 inside the task root, file exists, `sha256_file == sha256`, run terminal `awaiting_supervision`, all steps `ran`. Substring matches no longer count; a run with only textual mentions yields L1 at most plus diagnostic `AF-ECONOMY-PROOF-UNSTRUCTURED`; bad hash → `AF-ECONOMY-PROOF-HASH-MISMATCH` (L1).

### D7: Cache fall-through and timestamp validation

**Choice:** In `lookup`, a non-reuse decision on a tier is remembered (stale invalidated as today) and the loop continues; the final result is the first reuse, else the remembered stale/corrupt decision, else `miss`. `CacheEntry` validates `created_at`/`expires_at` as ISO-8601 (`datetime.fromisoformat`) — invalid → `ValidationError` → `_read_entry` None → corrupt miss (existing path). `assess` wraps parsing too (defense in depth).

### D8: Knowledge generation key

**Choice:** `knowledge_generation(root) -> str` = sha256 over sorted `(relative path, mtime_ns, size)` of every `pack.yaml` and pack markdown under root. `_catalog(root, generation)` and `_passages(root, generation)` take it as an extra cache argument; public functions compute it per call (a directory stat walk, no reads).

### D9: Reporting semantics

**Choice:** `PhaseBudgetPlan` gains `quality_status: Literal["ok","unresolved"]` and `budget_status: Literal["ok","protected_overrun","exceeded"]`; legacy `status` kept (= `quality_status`, `unresolved` on non-protected exceed). Supervisor adds `unresolved.routing = routing.unresolved` to `summary.json` and the run result. `DeltaSlice.status` adds `degraded`: unmapped path whose suffix/area is runtime (`.py .java .go .ts .js .kt .yaml .yml .json .proto .sql`, not under `docs/` nor `*.md`) → `degraded` with `AF-DELTA-UNMAPPED-SOURCE:<path>`; docs remain informational. Retrieval tokenizer: `unicodedata.normalize("NFKC", text).casefold()` + `re.compile(r"[^\W_][\w-]*")`.

### D10: Evals and claim scope

**Choice:** `EconomyMatrix.claim_scope: Literal["deterministic-safety-economy"]`. New `evals agentic-quality`: corpus `evals/corpus/agentic-quality/*.yaml` with `baseline`, `candidate`, `ground_truth: {verdict}` and `responses: {<capability>: <AgentArtifact payload with verdict>}`; runner executes `runtime run` per profile with `FakeModelAdapter(responses)` and scores the specialist artifact `payload.verdict` against ground truth; `--responses-dir` accepts user-provided recorded outputs of the same schema. Report `claim_scope="recorded-agentic-outputs"`; gate: per-profile accuracy ≥ deep accuracy and no safety violation. Docs (both languages) separate deterministic, provider/token and end-to-end evidence.

### D11: CI on merged commits

**Context:** `auto-merge-green` enables auto-merge with `GITHUB_TOKEN`; GitHub does not start workflows for events caused by that token, so squash commits on `main` have no check-runs (last `push` CI on `main` predates PRs #10–#13).

**Choice:** Enable auto-merge with `APIFORGE_PR_TOKEN` when configured (same fallback pattern as `open-green-pr`), and add `schedule: cron "17 3 * * *"` validating `main` as a backstop; `validate` job unchanged. Receipt notes which token class was used.

**Rejected:** `workflow_run` — also not fired for `GITHUB_TOKEN` pushes' downstream semantics; merge-queue — not configured on the repo.

---

## File Manifest

| # | File | Action | Purpose | Wave | Dependencies |
|---|------|--------|---------|------|--------------|
| 1 | `src/apiforge/security/__init__.py`, `security/source_paths.py` | Create | Resolver + AllowedRoots | H1 | — |
| 2 | `src/apiforge/case/service.py` | Modify | `load_verified_case` | H1 | — |
| 3 | `src/apiforge/context/gateway/levels.py`, `capsule.py`, `selection_cache.py` | Modify | Verified case + resolver | H1 | 1, 2 |
| 4 | `src/apiforge/evidence/resolve.py`, `context/delta.py` | Modify | Verified case + resolver | H1 | 1, 2 |
| 5 | `tests/security/test_source_paths.py`, `tests/context/test_gateway_trust.py`, `evals/corpus/economy-hardening/` | Create | 8 adversarial cases | H1 | 1–4 |
| 6 | `src/apiforge/contracts/selective.py`, `runtime/role_context.py`, `evals/selective.py` | Modify | Pools + validators + absolute gate | H2 | — |
| 7 | `src/apiforge/runtime/control.py`, `runtime/supervisor.py` | Modify | `calls_by_kind`, `record_call`, shadow accounting + mode | H2 | 6 |
| 8 | `src/apiforge/contracts/economy.py`, `economy/run_ledger.py` | Modify | `TokenCoverage`, auditable append | H2 | — |
| 9 | `src/apiforge/contracts/economy.py`, `runtime/economy.py` | Modify | `ProofReceipt`, structured L0 | H3 | 1 |
| 10 | `src/apiforge/contracts/cache.py`, `cache/store.py`, `cache/freshness.py` | Modify | Fall-through + timestamp validation | H3 | — |
| 11 | `src/apiforge/knowledge/selector.py`, `knowledge/retrieval.py` | Modify | Generation key + Unicode tokenizer | H3/H4 | — |
| 12 | `src/apiforge/contracts/economy_resume.py`, `economy/phase_budget.py` | Modify | quality/budget status | H4 | — |
| 13 | `src/apiforge/contracts/cache.py` (`DeltaSlice`), `context/delta.py` | Modify | `degraded` | H4 | 4 |
| 14 | `src/apiforge/contracts/economy_evals.py`, `evals/matrix.py`, `evals/agentic_quality.py`, `evals/hardening.py`, `cli.py`, `mcp/tools.py` | Modify/Create | claim scope + 2 evals | H4 | all |
| 15 | `.github/workflows/ci.yml` | Modify | Token + schedule | H4 | — |
| 16 | `docs/contracts/*`, `docs/catalog-contract.md`, threat model EN/PT-BR, economy guide EN/PT-BR, README rows, skill mirrors, `docs/sdd/API_FORGE_ECONOMY_ARCH_HARDENING/` | Modify/Create | Docs + SDD chain | each wave | — |

**Total Files:** ~45 (≈10 new)

---

## Code Patterns

### Pattern 1: resolver

```python
def resolve_allowed_source(candidate: str, roots: AllowedRoots, *, base: Path) -> Path:
    raw = str(candidate)
    if not raw or PureWindowsPath(raw).drive or raw.startswith(("\\\\", "//")):
        raise _outside(raw, "drive, UNC or empty path")
    rel = Path(raw)
    if ".." in rel.parts:
        raise _outside(raw, "parent traversal")
    target = (rel if rel.is_absolute() else base / rel).resolve(strict=False)
    for root in roots.paths:
        try:
            target.relative_to(root)
        except ValueError:
            continue
        return target
    raise _outside(raw, "outside allowed roots")
```

`resolve()` follows symlinks, so a link pointing outside fails `relative_to`.

### Pattern 2: contract invariant

```python
@model_validator(mode="after")
def within_envelope(self) -> RoleContextPlan:
    if self.total_bytes != sum(row.bytes for row in self.roles):
        raise ValueError("total_bytes must equal the sum of role bytes")
    if self.total_bytes > self.context_bytes:
        raise ValueError("total_bytes exceeds BudgetEnvelope.context_bytes")
    return self
```

### Pattern 3: refusal shape (unchanged repo convention)

```python
error = ContractError("AF-PATH-OUTSIDE-ROOT", detail)
error.field = "path"
error.unlock = "keep sources inside the project or declare the repository in .apiforge/workspace.yaml"
```

---

## Testing Strategy

| Test Type | Scope | Files | Coverage Goal |
|-----------|-------|-------|---------------|
| Unit | resolver (8 cases incl. symlink via `os.symlink`, skipped when not permitted), validators, coverage, proofs, cache | `tests/security`, `tests/economy`, `tests/cache`, `tests/runtime` | every AT |
| Integration | capsule/evidence with tampered case and poisoned facts; shadow run then checkpoint | `tests/context`, `tests/runtime` | AT-001..007 |
| Eval | `evals economy-hardening`, `evals agentic-quality`, 7 existing economy evals | `evals/corpus/*` | all gates pass |
| Release | `scripts/check_release.py`, `sdd check` | — | only the pre-existing orphan |

---

## Error Handling

| Error Type | Handling | Retry? |
|------------|----------|--------|
| `AF-PATH-OUTSIDE-ROOT` | per-ref `unresolved`, file never opened | No |
| `AF-CASE-HASH-MISMATCH` / `AF-CASE-*` | full refusal with field/unlock | No |
| `AF-BUDGET-EXHAUSTED` on shadow | shadow skipped, reason recorded | No |
| `AF-ECONOMY-LEDGER-PERSIST` | stats `unresolved`, run continues | No |
| `AF-ECONOMY-PROOF-UNSTRUCTURED` / `-HASH-MISMATCH` | L1 at most, diagnostic | No |
| `AF-DELTA-UNMAPPED-SOURCE` | delta `degraded` | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `APIFORGE_PR_TOKEN` (repo secret) | secret | unset | Enables CI on merged commits via auto-merge |
| `.apiforge/workspace.yaml` | file | absent | Declares extra allowed roots |

---

## Security Considerations

- Threat model rows (EN + PT-BR): case-loader bypass, out-of-root source read, symlink escape, uncounted shadow calls, partial-token claims.
- No new network, provider or mutation paths; CI change only swaps which token enables auto-merge.

---

## Observability

- `summary.json`: `unresolved.routing`, `shadow.mode`, `calls_by_kind`.
- `economy stats`: `token_coverage`, `persist_failures`.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | design-agent | Initial from DEFINE |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_API_FORGE_ECONOMY_ARCH_HARDENING.md`
