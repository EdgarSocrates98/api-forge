# DESIGN: Field Integrity Hardening

> Technical design for sealing the field cycle, binding verification to annotations, proving verifier independence, gating decisions on readiness, and completing HTTP inference provenance.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | FIELD_INTEGRITY_HARDENING |
| **Date** | 2026-09-28 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_FIELD_INTEGRITY_HARDENING.md](./DEFINE_FIELD_INTEGRITY_HARDENING.md) |
| **Status** | ✅ Shipped |
| **Confidence** | 0.80 — strong codebase pattern (`BenchmarkIdentity/v1`, `FieldError`, CLI/MCP `_run`/`_call` refusal path); agentspec KB has no field/provenance domain (generic `pydantic`, `testing`, `python` only) |

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                          FIELD HARNESS (after hardening)                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  CLI (cli_field.py) ─┐                                                        │
│  MCP (mcp/tools.py) ─┴─► field.record / annotate / verify / report / export   │
│                                   │                                           │
│                                   ▼                                           │
│                    ┌──────────────────────────────┐                           │
│                    │ field.identity.ensure_cycle() │◄── docs/field/corpus.yaml │
│                    │  recompute FieldCycleIdentity │◄── docs/field/hypothesis.md│
│                    │  compare vs cycle.lock.json   │◄── docs/field/cycle.lock.json
│                    └──────────────┬───────────────┘                           │
│                     mismatch ─────┼────► FieldError AF-FIELD-CYCLE-MUTATED    │
│                                   ▼                                           │
│   record ──► field.readiness.cycle_state(now) ── expired ─► AF-FIELD-CYCLE-EXPIRED
│      │          (runs_total vs max_runs, now vs started+max_weeks)            │
│      ├─ first record: seal() = mark_cycle_started + write lock                │
│      └─ executor: ActorRef (field.actors.parse_actor)                         │
│                                                                               │
│   annotate ──► FieldRun v2 (receipt untouched; digest now differs → stale)    │
│   verify ───► ActorRef verifier ≠ executor ─► VerificationReceipt/v1          │
│                 {verdict, annotation_sha256, verifier, verified_at}           │
│                                                                               │
│   report ──► summarize(manifest, runs, now)                                   │
│               verification_state(run) ∈ agree|disagree|unresolved|stale|none  │
│               cycle_status ∈ collecting|ready|expired → h1 gate               │
│   export ──► only verification_state == agree; + cycle_status + identity      │
│                                                                               │
│  workspace/inference/match.py _http(): refs = {call.ref} ∪ {route.ref…}       │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `field/identity.py` (new) | Canonical hashing, `compute_identity`, `seal`, `ensure_cycle`, lock read/write | stdlib `hashlib`, `json`, `subprocess` (optional git HEAD) |
| `field/actors.py` (new) | Parse/validate `kind:id` actor strings → `ActorRef` | stdlib `re` |
| `field/readiness.py` (new) | `verification_state`, `annotation_digest`, `cycle_state` (status + coverage gate) | pure functions, injectable `now` |
| `contracts/field.py` | `ActorRef`, `VerificationReceipt/v1`, `FieldCycleIdentity/v1`, `CoverageGate`; `FieldRun` → v2, `FieldReport` → v2; `FieldGate.max_runs` default 40 | pydantic `VersionedContract` |
| `field/record.py` | Require executor; check expiry; seal on first record; carry executor/verification on re-record | — |
| `field/annotate.py` | `annotate` keeps receipt (stale by digest); `verify` enforces independence, writes receipt | — |
| `field/report.py` | Readiness-gated H1 + recommendation; `stale_runs`, `provisional_h1`, `cycle_status`, `coverage_gate` | — |
| `field/export.py` | Filter by `verification_state`; add cycle status + identity to result | — |
| `field/corpus.py` | Unchanged API; `mark_cycle_started` reused by `seal` | — |
| `field/errors.py` | `CYCLE_MUTATED`, `CYCLE_EXPIRED`, `VERIFIER_NOT_INDEPENDENT`, `ACTOR_INVALID` | — |
| `cli_field.py`, `mcp/tools.py` | `--executor` on record, `--verifier` on verify; parity | typer / MCP |
| `workspace/inference/match.py` | HTTP edges carry callee `Served.ref` | — |

---

## Key Decisions

### Decision 1: Sealed lockfile `docs/field/cycle.lock.json` checked by every field command

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** Pre-registration is declarative: `load_corpus` checks only that `hypothesis.md` exists (`corpus.py:61`), `registered_at` and `cycle_started_at` are editable YAML, so a corpus can be edited or backdated after results appear with no runtime detection.

**Choice:** `FieldCycleIdentity/v1` = `{cycle_started_at, corpus_sha256, hypothesis_sha256, gate_sha256, tasks_sha256, repos_sha256, git_commit?}` written once by the first `field record` (same call that sets `cycle_started_at`). `ensure_cycle(root, manifest)` runs at the start of `record/annotate/verify/report/export`:

| corpus `cycle_started_at` | lock | result |
|---|---|---|
| null | absent | pre-cycle → `None` (no check) |
| null | present | `AF-FIELD-CYCLE-MUTATED` field=`cycle.cycle_started_at` |
| set | absent | `AF-FIELD-CYCLE-MUTATED` field=`cycle.lock` |
| set | present, `same_cycle` false | `AF-FIELD-CYCLE-MUTATED` field=`cycle.<first differing component>` |
| set | present, equal | identity returned |

`corpus_sha256` hashes the canonical JSON of `CorpusManifest.model_dump(mode="json")` **minus `cycle_started_at`** (the seal writes that key, so it must not self-invalidate); `cycle_started_at` is compared as its own component, which also catches moving the start forward to admit a late task. Hypothesis hashed over LF-normalized UTF-8 bytes. Per-component hashes exist so the refusal names *what* changed.

**Rationale:** Turns the documented rule ("editing hypothesis after start invalidates the cycle") into an invariant, mirroring the in-repo `BenchmarkIdentity/v1.same_experiment()` pattern. Hashing the parsed model (not raw YAML bytes) survives `mark_cycle_started`'s `yaml.safe_dump` rewrite and comment/formatting noise while catching every semantic edit.

**Alternatives Rejected:**
1. Inline `identity:` block in `corpus.yaml` — self-referential hash, mixes declaration with seal (brainstorm Approach B).
2. Append-only event ledger — rewrites storage model; beyond scope (Approach C).
3. Raw-bytes corpus hash — invalidated by the seal's own rewrite.

**Consequences:**
- A deleted/edited lock or corpus stops the whole cycle; recovery = restore sealed commit or start a new cycle manually (no reset command, by YAGNI).
- `git_commit` is informational only (excluded from `same_cycle`), filled via `git rev-parse HEAD` when available, `None` otherwise.

---

### Decision 2: `FieldRun`/`FieldReport` move to v2 in place; `verifier_verdict` replaced by `verification`

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** `VersionedContract` convention says v2 lands as a sibling class. But `docs/field/runs/` holds only `.gitkeep`, the corpus has `tasks: []`, field contracts are not in `contracts/registry.py`, and the only schema-literal consumer is `tests/field/test_export_parity.py:151` (A-001, A-002 verified).

**Choice:** Change schema literals to `apiforge/field-run/v2` and `apiforge/field-report/v2` and edit the classes in place. `FieldRun` drops `verifier_verdict`, gains `executor: ActorRef` (required) and `verification: VerificationReceipt | None`. `field verify` output keeps the key `verifier_verdict` for CLI/MCP stability, plus `verified_at` and `verifier_kind` (never labels).

**Rationale:** No v1 payload exists anywhere, so a sibling v1 class would be dead code kept only for ceremony; bumping the schema literal still makes any stray v1 file fail validation loudly (`extra="forbid"`).

**Alternatives Rejected:**
1. Sibling v1 + v2 classes — dead code, no payload to read.
2. Keep `verifier_verdict` as derived property — pydantic frozen model would still serialize/accept it ambiguously; two sources of truth.

**Consequences:**
- `docs/sdd/API_FORGE_FIELD_VALIDATION/contract.md` still lists v1 (historical); the new SDD's `contract.md` covers v2.

---

### Decision 3: Annotation digest binds evidence identity, not only labels

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** `_update()` (`annotate.py:35`) merges changes over an already-verified run; `record` re-run also carries human fields (`record.py:HUMAN_FIELDS`).

**Choice:** `annotation_digest(run)` = sha256 of canonical JSON of `{task_id, phase, run_ids, executor, task_completed, exit_reason, manual_context_required, human_intervention, false_positives, false_negatives}`. The receipt stores it; `verification_state` returns `stale` when it differs. `annotate` and re-`record` never touch the receipt — staleness is derived, the receipt is history.

**Rationale:** The verifier judged a specific labelling of specific runs; re-linking different run ids is as much a change as relabelling. Derived staleness needs no write-path coordination and cannot be forgotten by a future code path.

**Alternatives Rejected:**
1. Clear verdict on annotate — loses the fact a verification happened; forgettable in new paths.
2. Refuse annotate after verify — blocks honest corrections; needs unlock command.
3. Digest of labels only — re-record with different runs would stay "verified".

**Consequences:** Re-verification after any change is required to count the run; `stale_runs` makes this visible.

---

### Decision 4: Actors as `kind:id` strings; executor required; new `AF-FIELD-ACTOR-INVALID`

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** Nothing proves verifier ≠ executor; humans must stay anonymized.

**Choice:** `--executor` (record) and `--verifier` (verify) take `human:sha256:<64hex>` or `agent:<slug>` (`^[a-z][a-z0-9-]{1,63}$`, e.g. `agent:api-verifier`). Malformed → `AF-FIELD-ACTOR-INVALID` (field=`executor`/`verifier`). `verifier == executor` (kind and id) → `AF-FIELD-VERIFIER-NOT-INDEPENDENT`. Agent ids are not checked against the roster.

**Rationale:** A dedicated code gives a precise `unlock` ("use human:sha256:<hex> or agent:<name>"); `AF-FIELD-ENUM` means "outside a closed set", which an id format is not. Roster lookup would couple `field` to `agents/` for no integrity gain.

**Alternatives Rejected:**
1. Reuse `AF-FIELD-ENUM` — wrong semantics, vaguer unlock.
2. Optional executor — independence check becomes skippable.
3. Validate agent id against `agents/*.md` — coupling; YAGNI.

**Consequences:** `field record` CLI/MCP gains a required parameter (breaking, acceptable: cycle not started). Four new AF codes total.

---

### Decision 5: Readiness is derived in `field/readiness.py` with an injectable clock; outputs stay deterministic

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** `summarize` emits H1 + "open follow-up SDDs" regardless of `scenarios_under_min`; `max_runs`/`max_weeks` are never read; `test_report_is_byte_deterministic` must keep passing.

**Choice:** `cycle_state(manifest, runs, now)` returns `(status, CoverageGate)`:
- `runs_total` = baseline runs; `deadline` = `cycle_started_at + max_weeks` (RFC3339 string, `None` pre-cycle).
- `within_timebox` = `runs_total ≤ max_runs ∧ (deadline is None ∨ now ≤ deadline)`.
- `enough_scenarios` = ∀ scenario, `agree`-verified count ≥ `min_tasks_per_scenario`.
- `ready` ⇔ `enough_scenarios ∧ within_timebox`; `expired` ⇔ ¬ready ∧ (`runs_total ≥ max_runs` ∨ now > deadline); else `collecting`.
- H1 logic (unchanged) → `provisional_h1`; `h1_verdict = provisional_h1 if ready else "inconclusive"`.
- Recommendation: ready → existing text; expired → `"inconclusive: extend the corpus; open no new feature"`; collecting → `"continue collecting: cycle not ready; open no new feature"`.
- `record` refuses with `AF-FIELD-CYCLE-EXPIRED` when status is `expired`, or when a *new* baseline record would make `runs_total > max_runs`; re-recording an existing task/phase is allowed while not expired.
- `now` is a keyword param (`now: datetime | None = None` → `datetime.now(UTC)`) on `record`, `summarize`, `build_report`; CLI/MCP never pass it. Report exposes `deadline`, never an elapsed duration.

**Rationale:** Separates observation (`provisional_h1`) from decision eligibility (`h1_verdict`), closing early stopping. Emitting a fixed deadline instead of elapsed time keeps the report byte-deterministic for fixed inputs.

**Alternatives Rejected:**
1. Timebox informative only — allows extending a cycle until a convenient result.
2. Global clock monkeypatch in tests — brittle; explicit seam is clearer.
3. Readiness also requiring repo coverage — theme qualification already requires `min_repos_per_theme` (A-004).

**Consequences:** `min_tasks_per_scenario × 6 = 30 ≤ max_runs 40` leaves 10 runs of slack for disagree/stale/unresolved.

---

### Decision 6: HTTP inferred edges record callee route refs

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** `_http` keeps only `call.ref` (`match.py:129`) though `Served.ref` exists; `_topics` already records both sides.

**Choice:** While scoring a callee, collect the refs of the routes that matched at the best score; candidates carry `(callee, score, route_refs)`; edge refs = `{call.ref} ∪ route_refs`. Ambiguity handling and confidence unchanged.

**Rationale:** Relation auditable from both repos; parity with topic inference; zero extractor change (A-007).

**Alternatives Rejected:** Only first matching route ref — nondeterministic under multiple equivalent routes (e.g. `ANY` + `GET`).

**Consequences:** `evidence.refs` grows by callee route refs; existing assertion `"web:client.py:2" in refs` still holds.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/field.py` | Modify | `ActorRef`, `VerificationReceipt`, `FieldCycleIdentity` (+`same_cycle`, `first_difference`), `CoverageGate`, `CycleStatus`; `FieldRun`/`FieldReport` v2; `max_runs` default 40 | @python-developer | None |
| 2 | `src/apiforge/field/errors.py` | Modify | 4 new codes | @python-developer | None |
| 3 | `src/apiforge/field/actors.py` | Create | `parse_actor`, `same_actor` | @python-developer | 1, 2 |
| 4 | `src/apiforge/field/identity.py` | Create | canonical hash, `compute_identity`, `read_lock`, `seal`, `ensure_cycle` | @python-developer | 1, 2 |
| 5 | `src/apiforge/field/readiness.py` | Create | `annotation_digest`, `verification_state`, `cycle_state` | @python-developer | 1 |
| 6 | `src/apiforge/field/record.py` | Modify | executor, ensure_cycle, expiry, seal, `now` | @python-developer | 3, 4, 5 |
| 7 | `src/apiforge/field/annotate.py` | Modify | ensure_cycle; verify → receipt + independence | @python-developer | 3, 4, 5 |
| 8 | `src/apiforge/field/report.py` | Modify | readiness-gated report, `now`, ensure_cycle | @python-developer | 4, 5 |
| 9 | `src/apiforge/field/export.py` | Modify | `verification_state` filter; cycle status + identity in result; ensure_cycle | @python-developer | 4, 5 |
| 10 | `src/apiforge/field/__init__.py` | Modify | export new public names if the module re-exports | (general) | 3-5 |
| 11 | `src/apiforge/cli_field.py` | Modify | `--executor` on record, `--verifier` on verify | @python-developer | 6, 7 |
| 12 | `src/apiforge/mcp/tools.py` | Modify | `executor`/`verifier` params on `field_record`/`field_verify` | @python-developer | 6, 7 |
| 13 | `src/apiforge/workspace/inference/match.py` | Modify | callee route refs in `_http` | @python-developer | None |
| 14 | `docs/field/corpus.yaml` | Modify | `gate.max_runs: 40` | (general) | 1 |
| 15 | `docs/field/README.md` | Modify | lock, receipt, actors, statuses, refusals, operator flow | @code-documenter | 6-9 |
| 16 | `docs/catalog-contract.md` | Modify | catalog 4 new AF codes | @code-documenter | 2 |
| 17 | `tests/field/support.py` | Modify | executor/verifier constants, `sealed_corpus`, `verified_runs` helper, fixed clocks | @test-generator | 1-9 |
| 18 | `tests/field/test_integrity.py` | Create | AT-001…AT-014 | @test-generator | 17 |
| 19 | `tests/field/test_annotate_report.py` | Modify | receipts instead of `verifier_verdict`; readiness in existing report tests | @test-generator | 17 |
| 20 | `tests/field/test_record.py` | Modify | `executor` arg; re-record carries receipt | @test-generator | 17 |
| 21 | `tests/field/test_export_parity.py` | Modify | v2 schema, CLI/MCP parity for new refusals + params (AT-016, AT-017) | @test-generator | 17 |
| 22 | `tests/workspace/test_inference.py` | Modify | AT-015 callee route ref | @test-generator | 13 |
| 23 | `docs/sdd/API_FORGE_FIELD_INTEGRITY_HARDENING/*.md` (+`evidence/`) | Create | repo SDD phase artifacts (intent…ship) mirroring `API_FORGE_FIELD_VALIDATION` layout, validated by `apiforge sdd check --root docs/sdd` | (general) | all |

**Total Files:** 22 source/test/doc files + 1 SDD artifact set.

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @python-developer | 1-9, 11-13 | Typed Python, dataclasses/pydantic, pure functions |
| @test-generator | 17-22 | pytest fixtures and acceptance-test coverage |
| @code-documenter | 15, 16 | Operator docs and error catalog |
| (general) | 10, 14, 23 | One-line re-exports, YAML value, repo-specific SDD tooling |

**Agent Discovery:**
- Scanned: `C:/Users/edgar/.claude/plugins/cache/agentspec/agentspec/3.5.0/agents/**/*.md` (python/, test/, dev/ categories)
- Matched by file type (`.py`, `tests/`, `docs/`) and purpose keywords; project roster agents (`api-verifier`, `api-release-guardian`) are review roles used after build, not file authors.

---

## Code Patterns

### Pattern 1: Canonical hashing and cycle identity (`field/identity.py`)

```python
"""Sealed field-cycle identity: pre-registration as an invariant, not a convention."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from apiforge.contracts.field import CorpusManifest, FieldCycleIdentity
from apiforge.field.corpus import HYPOTHESIS_NAME, mark_cycle_started
from apiforge.field.errors import CYCLE_MUTATED, FieldError
from apiforge.field.store import field_dir, write_json

LOCK_NAME = "cycle.lock.json"
_UNLOCK = "restore docs/field to the sealed commit, or start a new cycle with a new corpus"


def lock_path(root: Path) -> Path:
    return field_dir(root) / LOCK_NAME


def sha256_json(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _hypothesis_sha(root: Path) -> str:
    text = (field_dir(root) / HYPOTHESIS_NAME).read_bytes().decode("utf-8")
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def _git_head(root: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, timeout=5
        )
    except (OSError, subprocess.SubprocessError):
        return None
    head = out.stdout.strip()
    return head if out.returncode == 0 and len(head) == 40 else None


def compute_identity(root: Path, manifest: CorpusManifest, started_at: str) -> FieldCycleIdentity:
    body = manifest.model_dump(mode="json")
    body.pop("cycle_started_at", None)
    return FieldCycleIdentity(
        cycle_started_at=started_at,
        corpus_sha256=sha256_json(body),
        hypothesis_sha256=_hypothesis_sha(root),
        gate_sha256=sha256_json(body["gate"]),
        tasks_sha256=sha256_json(sorted(body["tasks"], key=lambda item: item["id"])),
        repos_sha256=sha256_json(sorted(body["repos"], key=lambda item: item["ref"])),
        git_commit=_git_head(root),
    )


def _mutated(component: str, detail: str) -> FieldError:
    return FieldError(CYCLE_MUTATED, detail, field=f"cycle.{component}", unlock=_UNLOCK)


def ensure_cycle(root: Path, manifest: CorpusManifest) -> FieldCycleIdentity | None:
    path = lock_path(root)
    if manifest.cycle_started_at is None:
        if path.is_file():
            raise _mutated("cycle_started_at", "lock exists but corpus cycle_started_at is null")
        return None
    if not path.is_file():
        raise _mutated("lock", f"cycle started at {manifest.cycle_started_at} but lock is missing")
    sealed = FieldCycleIdentity.model_validate(json.loads(path.read_text(encoding="utf-8")))
    current = compute_identity(root, manifest, manifest.cycle_started_at)
    difference = sealed.first_difference(current)
    if difference is not None:
        raise _mutated(difference, f"{difference} differs from the sealed cycle")
    return sealed


def seal(root: Path, manifest: CorpusManifest, started_at: str) -> FieldCycleIdentity:
    mark_cycle_started(root, started_at)
    identity = compute_identity(root, manifest, started_at)
    write_json(lock_path(root), identity.model_dump(mode="json"))
    return identity
```

### Pattern 2: Contracts (additions to `contracts/field.py`)

```python
ActorKind = Literal["human", "agent"]
CycleStatus = Literal["collecting", "ready", "expired"]
VerificationState = Literal["agree", "disagree", "unresolved", "stale"]
_SHA = r"^[0-9a-f]{64}$"
_IDENTITY_COMPONENTS = (
    "cycle_started_at",
    "corpus_sha256",
    "hypothesis_sha256",
    "gate_sha256",
    "tasks_sha256",
    "repos_sha256",
)


class ActorRef(VersionedContract):
    kind: ActorKind
    id: str = Field(min_length=1)


class VerificationReceipt(VersionedContract):
    schema: Literal["apiforge/field-verification-receipt/v1"] = (  # type: ignore[assignment]
        "apiforge/field-verification-receipt/v1"
    )
    verdict: VerifierVerdict
    annotation_sha256: str = Field(pattern=_SHA)
    verifier: ActorRef
    verified_at: str


class FieldCycleIdentity(VersionedContract):
    schema: Literal["apiforge/field-cycle-identity/v1"] = (  # type: ignore[assignment]
        "apiforge/field-cycle-identity/v1"
    )
    cycle_started_at: str
    corpus_sha256: str = Field(pattern=_SHA)
    hypothesis_sha256: str = Field(pattern=_SHA)
    gate_sha256: str = Field(pattern=_SHA)
    tasks_sha256: str = Field(pattern=_SHA)
    repos_sha256: str = Field(pattern=_SHA)
    git_commit: str | None = None

    def first_difference(self, other: FieldCycleIdentity) -> str | None:
        """First sealed component that differs; git_commit is informational."""
        for name in _IDENTITY_COMPONENTS:
            if getattr(self, name) != getattr(other, name):
                return name
        return None

    def same_cycle(self, other: FieldCycleIdentity) -> bool:
        return self.first_difference(other) is None


class CoverageGate(VersionedContract):
    enough_scenarios: bool
    runs_total: int = Field(ge=0)
    max_runs: int = Field(ge=1)
    deadline: str | None = None
    within_timebox: bool

# FieldRun: schema -> "apiforge/field-run/v2"; drop verifier_verdict;
#   executor: ActorRef ; verification: VerificationReceipt | None = None
# FieldReport: schema -> "apiforge/field-report/v2"; add
#   cycle_status: CycleStatus ; coverage_gate: CoverageGate ;
#   provisional_h1: H1Verdict ; stale_runs: tuple[str, ...] = ()
```

`FieldCycleIdentity`, `VerificationReceipt` are registered in `contracts/registry.py` only if the registry is the repo's single discovery path for new contracts (field v1 contracts are not registered today — Build follows that precedent and does not register).

### Pattern 3: Actors (`field/actors.py`)

```python
import re

from apiforge.contracts.field import ActorRef
from apiforge.field.errors import ACTOR_INVALID, FieldError

_HUMAN = re.compile(r"^sha256:[0-9a-f]{64}$")
_AGENT = re.compile(r"^[a-z][a-z0-9-]{1,63}$")


def parse_actor(value: str, *, field: str) -> ActorRef:
    kind, _, ident = value.partition(":")
    pattern = _HUMAN if kind == "human" else _AGENT if kind == "agent" else None
    if pattern is None or not pattern.match(ident):
        raise FieldError(
            ACTOR_INVALID,
            f"{value!r} is not a valid {field}",
            field=field,
            unlock="use human:sha256:<64 hex> (anonymized) or agent:<roster-name>",
        )
    return ActorRef(kind=kind, id=ident)  # type: ignore[arg-type]
```

### Pattern 4: Digest, verification state and readiness (`field/readiness.py`)

```python
from datetime import UTC, datetime, timedelta

from apiforge.contracts.field import (
    SCENARIOS, CorpusManifest, CoverageGate, CycleStatus, FieldRun, VerificationState,
)
from apiforge.field.identity import sha256_json
from apiforge.field.store import parse_ts

_DIGEST_FIELDS = (
    "task_id", "phase", "run_ids", "executor", "task_completed", "exit_reason",
    "manual_context_required", "human_intervention", "false_positives", "false_negatives",
)


def annotation_digest(run: FieldRun) -> str:
    dumped = run.model_dump(mode="json")
    return sha256_json({name: dumped[name] for name in _DIGEST_FIELDS})


def verification_state(run: FieldRun) -> VerificationState | None:
    receipt = run.verification
    if receipt is None:
        return None
    if receipt.annotation_sha256 != annotation_digest(run):
        return "stale"
    return receipt.verdict


def deadline(manifest: CorpusManifest) -> datetime | None:
    if manifest.cycle_started_at is None:
        return None
    start = parse_ts(manifest.cycle_started_at, field="cycle_started_at")
    return start + timedelta(weeks=manifest.gate.max_weeks)


def cycle_state(
    manifest: CorpusManifest, runs: tuple[FieldRun, ...], now: datetime | None = None
) -> tuple[CycleStatus, CoverageGate]:
    moment = now or datetime.now(UTC)
    gate = manifest.gate
    baseline = [run for run in runs if run.phase == "baseline"]
    agreed = [run for run in baseline if verification_state(run) == "agree"]
    counts = {name: sum(1 for run in agreed if run.scenario == name) for name in SCENARIOS}
    enough = all(counts[name] >= gate.min_tasks_per_scenario for name in SCENARIOS)
    end = deadline(manifest)
    in_time = end is None or moment <= end
    within = len(baseline) <= gate.max_runs and in_time
    coverage = CoverageGate(
        enough_scenarios=enough,
        runs_total=len(baseline),
        max_runs=gate.max_runs,
        deadline=end.isoformat().replace("+00:00", "Z") if end else None,
        within_timebox=within,
    )
    if enough and within:
        return "ready", coverage
    if len(baseline) >= gate.max_runs or not in_time:
        return "expired", coverage
    return "collecting", coverage
```

### Pattern 5: Verify with independence (`field/annotate.py`)

```python
def verify(
    root: Path, *, task_id: str, phase: str, verdict: str, verifier: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    root = Path(root)
    ensure_cycle(root, load_corpus(root))
    checked_phase: FieldPhase = _enum(phase, PHASES, "phase")  # type: ignore[assignment]
    checked = _enum(verdict, VERDICTS, "verdict")
    actor = parse_actor(verifier, field="verifier")
    run = load_run(root, task_id, checked_phase)
    if actor.kind == run.executor.kind and actor.id == run.executor.id:
        raise FieldError(
            VERIFIER_NOT_INDEPENDENT,
            f"verifier {actor.kind}:{actor.id} is the executor of {task_id}",
            field="verifier",
            unlock="verify with a different human or agent than the executor",
        )
    receipt = VerificationReceipt(
        verdict=checked,
        annotation_sha256=annotation_digest(run),
        verifier=actor,
        verified_at=_stamp(now),
    )
    updated = _update(root, run, {"verification": receipt.model_dump(mode="json")})
    return {
        "task_id": updated.task_id,
        "phase": updated.phase,
        "verifier_verdict": checked,
        "verifier_kind": actor.kind,
        "verified_at": receipt.verified_at,
    }
```

### Pattern 6: Record order of operations (`field/record.py`)

```python
manifest = load_corpus(root)
ensure_cycle(root, manifest)                     # V1/V2 before anything else
executor_ref = parse_actor(executor, field="executor")
task = registered_task(manifest, task_id, started_at=started_at)
runs = load_runs(root)
status, coverage = cycle_state(manifest, runs, now)
previous = maybe_load_run(root, task_id, phase)
if status == "expired" or (
    phase == "baseline" and previous is None and coverage.runs_total >= manifest.gate.max_runs
):
    raise FieldError(
        CYCLE_EXPIRED,
        f"cycle expired: {coverage.runs_total}/{coverage.max_runs} runs, deadline {coverage.deadline}",
        field="cycle",
        unlock="report the cycle as inconclusive; register a new cycle to continue",
    )
# ... existing evidence join (unchanged) ...
if manifest.cycle_started_at is None:
    seal(root, manifest, started_at)             # replaces mark_cycle_started
save_run(root, run)                               # executor=executor_ref, carries verification
```

### Pattern 7: HTTP callee route refs (`workspace/inference/match.py`)

```python
best = 0.0
route_refs: set[str] = set()
for route in callee.served:
    # ... unchanged template / method filters ...
    score = EXACT if call.method != "unknown" else PATH_ONLY
    if score > best:
        best, route_refs = score, {route.ref}
    elif score == best:
        route_refs.add(route.ref)
if best:
    if _hint_matches(call.base_hint, callee.name):
        best = min(CAP, best + HINT_BONUS)
    candidates.append((callee, best, route_refs))
# ... ambiguity handling unchanged, unpacking 3-tuples ...
edges[key] = (max(previous, score), refs | {call.ref} | route_refs)
```

### Pattern 8: Configuration (`docs/field/corpus.yaml`)

```yaml
schema: apiforge/field-corpus/v1
cycle_started_at: null
gate:
  max_runs: 40
  max_weeks: 4
  min_tasks_per_theme: 5
  min_repos_per_theme: 2
  min_tasks_per_scenario: 5
```

---

## Data Flow

```text
1. field record --task T --run R --executor agent:api-orchestrator
   │  load_corpus → ensure_cycle (pre-cycle: none) → parse_actor → registered_task
   │  cycle_state(now) → refuse if expired / over max_runs
   ▼
2. evidence join (ledger, summary, checkpoint) unchanged
   │  first record: seal() → cycle_started_at + cycle.lock.json
   ▼
3. field annotate --exit-reason graph_gap      (ensure_cycle; receipt untouched)
   ▼
4. field verify --verdict agree --verifier human:sha256:…
   │  ensure_cycle → independence → receipt{digest(run), verifier, verified_at}
   ▼
5. field report
   │  ensure_cycle → verification_state per run → cycle_state(now)
   │  provisional_h1 always; h1_verdict + SDD recommendation only when ready
   ▼
6. field export → only state == agree; result + cycle_status + identity
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| Local filesystem `docs/field/` | read/write JSON/YAML | none |
| `git rev-parse HEAD` | optional subprocess, read-only, 5s timeout | none |
| MCP host (`mcp/tools.py`) | same functions via `_call` | existing host config |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | identity, actors, digest, readiness | `tests/field/test_integrity.py` | pytest, `tmp_path`, fixed `now` | all branches of `ensure_cycle`, `cycle_state`, `parse_actor` |
| Integration | record/annotate/verify/report/export on tmp corpus | `tests/field/test_integrity.py`, updated `test_record.py`, `test_annotate_report.py` | pytest | AT-001…AT-014 |
| Parity | CLI vs MCP payloads/refusals | `tests/field/test_export_parity.py` | pytest, `typer.testing.CliRunner` | AT-016, AT-017 |
| Inference | HTTP provenance | `tests/workspace/test_inference.py` | pytest | AT-015 |
| Gates | repo SDD + agents | `apiforge sdd check --root docs/sdd`, `apiforge agents lint` | CLI | pass |

Acceptance-test mapping:

| AT | Test |
|----|------|
| AT-001 | `test_first_record_seals_cycle` (lock written; corpus hash stable after seal) |
| AT-002 | `test_hypothesis_edit_is_mutation` |
| AT-003 | `test_backdated_task_is_mutation` (+ `test_moved_cycle_start_is_mutation`) |
| AT-004 | `test_missing_lock_is_mutation` (+ lock present with null start) |
| AT-005 | `test_crlf_hypothesis_is_not_mutation` |
| AT-006 | `test_annotate_after_verify_is_stale` |
| AT-007 | `test_reverify_clears_stale` |
| AT-008 | `test_self_verification_refused` |
| AT-009 | `test_raw_human_id_refused` (`AF-FIELD-ACTOR-INVALID`) |
| AT-010 | `test_early_stop_stays_collecting` |
| AT-011 | `test_full_coverage_is_ready` |
| AT-012 | `test_expired_by_runs` |
| AT-013 | `test_expired_by_weeks` (fixed `now`) |
| AT-014 | `test_record_after_expiry_refused` (+ new baseline beyond `max_runs`) |
| AT-015 | `test_http_call_infers_edge_with_provenance` asserts callee `payment-service:…` ref |
| AT-016 | `test_export_carries_cycle_status_and_identity` |
| AT-017 | `test_cli_and_mcp_refusals_match` parametrized with 4 new codes |

Run policy: targeted `pytest tests/field tests/workspace/test_inference.py --basetemp=E:/afpt/fih` per task; full suite once before ship.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| `AF-FIELD-CYCLE-MUTATED` | `FieldError`, field=`cycle.<component>`, unlock restore/new cycle; raised before any write | No |
| `AF-FIELD-CYCLE-EXPIRED` | `FieldError` on `record`; report still readable (status `expired`) | No |
| `AF-FIELD-VERIFIER-NOT-INDEPENDENT` | `FieldError` on `verify`; run file untouched | Yes, with other verifier |
| `AF-FIELD-ACTOR-INVALID` | `FieldError` on `record`/`verify` | Yes, fixed id |
| Stale receipt | Not an error: run in `stale_runs` + `unresolved_runs` | Re-verify |
| git unavailable | `git_commit=None`; never an error | — |
| Stray v1 run file | pydantic validation fails loudly (schema literal) | No |

All four codes cataloged in `docs/catalog-contract.md` under the field section and surfaced via existing CLI `_run` / MCP `_call` refusal envelopes (`code`, `field`, `unlock`).

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `gate.max_runs` | int | `40` | Baseline runs before expiry |
| `gate.max_weeks` | int | `4` | Weeks from `cycle_started_at` to deadline |
| `gate.min_tasks_per_scenario` | int | `5` | Readiness coverage per scenario |
| `gate.min_tasks_per_theme` | int | `5` | Theme qualification (unchanged) |
| `gate.min_repos_per_theme` | int | `2` | Theme qualification (unchanged) |

---

## Security Considerations

- Human identities are only accepted as `sha256:<64hex>`; raw names refused, keeping `docs/field/runs` and exports free of personal data.
- `verify` output never echoes human labels (existing guarantee preserved).
- `git` subprocess runs with fixed argv, no shell, bounded timeout, read-only.
- Lock is tamper-evident, not tamper-proof: an actor able to rewrite corpus + lock consistently is detectable only via Git history — documented in `docs/field/README.md` as the external proof.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | None added; refusals carry code/field/unlock |
| Metrics | Report exposes `cycle_status`, `coverage_gate`, `stale_runs`, `divergence_rate` |
| Tracing | N/A (local CLI) |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | design-agent | Initial version |
| 1.1 | 2026-09-28 | ship-agent | Shipped and archived |

---

## Next Step

**Ready for:** `/agentspec:workflow:build .claude/sdd/features/DESIGN_FIELD_INTEGRITY_HARDENING.md`
