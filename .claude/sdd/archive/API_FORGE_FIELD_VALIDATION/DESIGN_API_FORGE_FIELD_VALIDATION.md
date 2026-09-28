# DESIGN: API Forge Field Validation + System Graph Inference

> Technical design for an evidence-joining field-validation harness (track F) and an isolated, opt-in cross-repo relation inference (track S).

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_FIELD_VALIDATION |
| **Date** | 2026-09-28 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_FIELD_VALIDATION.md](./DEFINE_API_FORGE_FIELD_VALIDATION.md) |
| **Status** | ✅ Shipped |
| **Design confidence** | 0.85 (codebase patterns strong; agentspec KB is data-engineering-centric → project patterns dominate) |

---

## Architecture Overview

```text
┌──────────────────────────────── TRACK F: FIELD VALIDATION ─────────────────────────────────┐
│                                                                                            │
│  docs/field/corpus.yaml ─┐        (pre-registered tasks, ground truth, repo refs)          │
│  docs/field/hypothesis.md┤                                                                 │
│                          ▼                                                                 │
│                 field/corpus.py ── validate + registration cutoff (git-free: registered_at)│
│                          │                                                                 │
│  existing run artifacts  │                                                                 │
│  ┌──────────────────────┐│   field/record.py  (JOIN, never collect)                        │
│  │ .apiforge/economy.jsonl ├──► run_ledger rows ─┐                                         │
│  │ runs/<id>/summary.json  ├──► unresolved, human_gate                                     │
│  │ runs/<id>/economy_checkpoint.json ├──► calls_used, bytes │                              │
│  └──────────────────────┘│                       ▼                                         │
│                          └────────────► FieldRun (field-run/v1) ──► docs/field/runs/*.json │
│                                                  ▲                                         │
│   human ── field annotate ───────────────────────┤  (closed enums, AF-FIELD-* refusals)    │
│   verifier ── field verify (blind) ──────────────┘                                         │
│                                                  │                                         │
│                                   field/report.py (pure, deterministic)                    │
│                                   Wilson CI · theme qualification · H1 verdict · --ab      │
│                                                  │                                         │
│                                   field/export.py ──► evals/corpus/field/ (anonymized)     │
└──────────────────────────────────────────────────┼─────────────────────────────────────────┘
                                                   │ reads ledger rows "workspace.infer"
┌──────────────────────────────── TRACK S: INFERENCE (opt-in) ───────────────────────────────┐
│                                                  │                                         │
│  per-repo facts (existing adapters)              │                                         │
│   api_ir ApiModel operations (method, path) ─┐   │                                         │
│   data.streaming.topic / messaging.destination┤  │                                         │
│  NEW http_targets extractor (method + literal path/base-url near call site)                │
│                                              ▼   │                                         │
│             workspace/inference/match.py  (pure: facts × facts → candidates)               │
│                                              ▼                                             │
│             WorkspaceRelation(evidence.level="inferred", confidence, refs=file:line)       │
│                                              ▼                                             │
│   workspace graph --infer  ──► build_graph(manifest, inferred=...) + ledger row           │
│   (default OFF → graph byte-identical to today)                                            │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `contracts/field.py` | Pydantic contracts: `CorpusManifest`, `CorpusTask`, `FieldRun`, `Annotation`, `VerifierVerdict`, `FieldReport` | pydantic `VersionedContract` (existing base) |
| `field/errors.py` | `FieldError(code, detail, field, unlock)` + code constants | mirrors `EconomyError` |
| `field/corpus.py` | Load/validate corpus + hypothesis; registration cutoff check | `core.yaml` strict loader |
| `field/record.py` | Join ledger/summary/checkpoint into automatic fields; contamination check | stdlib json |
| `field/annotate.py` | Apply human annotation / blind verifier verdict with enum validation | pure |
| `field/report.py` | Counts, Wilson 95% CI, theme qualification, H1 verdict, A/B deltas | pure, stdlib `math` |
| `field/export.py` | Anonymize (sha256 repo ref, hashed paths) → `evals/corpus/field/` | pure + allow-list |
| `field/store.py` | Read/write `docs/field/runs/<task_id>__<phase>.json` (sorted keys, atomic write) | stdlib |
| `cli_field.py` | `apiforge field record|annotate|verify|report|export` | typer (pattern of `cli_economy.py`) |
| `mcp/tools.py` + `mcp/surface.py` | MCP parity: `field_record`, `field_annotate`, `field_verify`, `field_report` | existing `_call` wrapper |
| `adapters/http_targets.py` | NEW extractor: method + literal path/base-url for outbound HTTP/gRPC calls | regex, offline (pattern of `adapters/resilience.py`) |
| `workspace/inference/match.py` | Match outbound targets ↔ served operations; producers ↔ consumers by topic | pure |
| `workspace/inference/__init__.py` | `infer_relations(manifest) -> InferenceResult` | pure |
| `contracts/workspace.py` | `RelationKind` += `"publishes_to_consumer"`; no other change | Literal extension |
| `workspace/graph.py` | `build_graph(manifest, inferred=())` — inferred edges appended only when passed | minimal patch |
| `cli_workspace.py` | `workspace graph --infer` flag; writes ledger attribution row `verb="workspace.infer"` | typer |
| `docs/catalog-contract.md` | Catalog `AF-FIELD-*` and `AF-WORKSPACE-INFER-*` codes | md |

---

## Key Decisions

### Decision 1: `field record` joins existing artifacts; never collects

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** DEFINE F2 forbids a new telemetry layer. Ledger (`economy/run_ledger.py`), `summary.json` (`runtime/supervisor.py:360,1242`) and `economy_checkpoint.json` (`runtime/economy_checkpoint.py:18`) already hold `payload_bytes`, `calls_used`, `unresolved` per run.

**Choice:** `record.py` is a read-only projection keyed by `run_id`. Missing source ⇒ field `null` + `unresolved_reason` (`ledger_missing`, `summary_missing`, `checkpoint_missing`). Nothing is estimated.

**Rationale:** One source of truth; no drift between economy report and field report; AT-010 honest-null behavior falls out naturally.

**Alternatives Rejected:**
1. Emit a new `field` event from runtime — rejected: duplicates ledger, touches supervisor hot path, violates F2.
2. Parse host transcripts for tokens — rejected: optional input already handled by `economy stats --transcript`; not required by DEFINE.

**Consequences:**
- Metric quality bounded by existing emission (A-001 risk; surfaced as nulls, not hidden).
- Zero change to runtime; trivially reversible.

---

### Decision 2: Wall-clock via explicit `--started/--ended`, validated against ledger

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** `CostVector.duration_ms` sums emission durations ≠ task wall-clock (DEFINE open question). A task may span multiple runs and human time outside API Forge.

**Choice:** `field record` requires `--started` and `--ended` (RFC3339) supplied by the operator; `time_to_solution_ms = ended − started`. `time_to_evidence_ms = first ledger row timestamp with evidence/receipt verb for linked run_ids − started`; null if ledger rows lack timestamps. Refuse `AF-FIELD-TIME-ORDER` if `ended < started` or any linked ledger row lies outside `[started, ended]` window (±60s tolerance).

**Rationale:** Task time includes human work the runtime never sees; ledger cross-check catches typos.

**Alternatives Rejected:**
1. Runtime-emitted start/end — rejected: misses human time between runs; needs supervisor change.
2. Sum `duration_ms` — rejected: measures compute, not solution time.

**Consequences:**
- Relies on operator discipline (mitigated by window check).
- `time_to_evidence` may be null for older ledger rows → reported as unresolved.

---

### Decision 3: Contamination detected from evidence, not trusted from input

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** S3/AT-006: baseline runs must not use inference. An operator-supplied `--inference-flag` bool can lie or be forgotten.

**Choice:** Inference is reachable only via `workspace graph --infer` (and its MCP twin), which always appends a ledger attribution row `verb="workspace.infer"` with the run_id when one is in scope (auditable=True). `field record --phase baseline` scans linked run_ids for that verb; any hit → `AF-FIELD-FLAG-CONTAMINATION`. `inference_flag` in the record is **derived**, never an input.

**Rationale:** Evidence-derived state matches repo principle "inspect persisted evidence before reasoning"; defeats human error.

**Alternatives Rejected:**
1. Env var `APIFORGE_WORKSPACE_INFER` — rejected: invisible in artifacts, unauditable.
2. Operator flag on `field record` — rejected: self-report.

**Consequences:**
- Inference used outside a run context (no run_id) is not attributable → report counts it under `unresolved` for the cycle audit.
- Persist failure on the ledger row surfaces `AF-ECONOMY-LEDGER-PERSIST` (existing behavior), so contamination can't be silently lost.

---

### Decision 4: Pre-registration enforced by manifest timestamps + git, not by trust

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** F4/AT-002/AT-003 require refusing unregistered and late-registered tasks.

**Choice:** Each `CorpusTask` carries `registered_at` (RFC3339). `corpus.yaml` carries `cycle_started_at` set when the first run is recorded (written once by `field record`, immutable afterwards). Task with `registered_at > cycle_started_at` → `AF-FIELD-LATE-REGISTRATION`. Absent task → `AF-FIELD-TASK-UNREGISTERED`. Git commit order is verified in the ship-phase evidence (read-only `git log`), not by core code (core stays git-free).

**Rationale:** Deterministic, testable without git; git proof kept for release evidence.

**Alternatives Rejected:**
1. Core shells out to git — rejected: couples core to VCS, breaks fixtures.
2. No enforcement, convention only — rejected: R4 (pre-written conclusion) returns.

**Consequences:**
- `registered_at` is self-declared; git log in ship evidence is the independent check.

---

### Decision 5: Wilson score interval; theme qualification is a hard rule

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** n≈30; normal approximation breaks at small p.

**Choice:** Wilson 95% (z=1.959964) per `exit_reason` proportion over **verified** runs (`verifier_verdict == agree`). Theme qualifies iff count ≥ `min_tasks` (5) AND distinct `repo_ref` ≥ `min_repos` (2); thresholds read from `corpus.yaml.gate`. H1 verdict: `confirmed` if H1's declared category qualifies and ranks #1 by count; `refuted` if the H1 category does not qualify while another does; else `inconclusive`. Divergent/unresolved runs excluded from counts and listed.

**Rationale:** Stdlib-only, deterministic, well-behaved at small n; rule matches DEFINE AT-007/AT-008.

**Alternatives Rejected:**
1. Bootstrap CI — rejected: randomness breaks byte-determinism (AT-009) unless seeded; unneeded.
2. scipy — rejected: new dependency for one formula.

**Consequences:**
- Ranking among qualified themes is by count only; ties reported as ties.

---

### Decision 6: Inference = pure matcher over facts; new extractor only for outbound targets

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** `resilience.http_call` facts carry `method` but not target path (`adapters/resilience.py:104`), so HTTP inference needs new extraction. Topic facts already exist (`data.streaming.topic` in `adapters/streaming.py:108`, `data.messaging.destination`).

**Choice:** New `adapters/http_targets.py` emits `http.outbound` facts `{method, path_literal, base_hint, heuristic}` from string literals within the call line ±2 lines (requests/httpx/fetch/axios/RestTemplate/WebClient/net-http, gRPC stub `.<Method>(` with service name). `match.py` normalizes path templates (`{id}`, `:id`, `<int:id>` → `{}`), matches against `ApiModel` operations of **other** repos. Confidence: exact method+template 0.9; template-only (method unknown) 0.6; base_hint matches repo/service name +0.1 cap 0.95; ≥2 candidate repos → each ≤0.45 and an `unresolved` entry (AT-014). Topic edges: producer repo → consumer repo per identical topic string, 0.85; relation `publishes_to_consumer`, topic in `refs`.

**Rationale:** Keeps inference offline and deterministic; reuses api_ir and streaming facts; isolates new heuristics in one adapter.

**Alternatives Rejected:**
1. Extend `resilience.http_call` with path — rejected: widens a stable fact contract used by resilience scoring.
2. Trace-based (runtime) inference — rejected: out of scope (no live access; Contract-to-Runtime deferred).
3. LLM-assisted matching — rejected: non-deterministic, provider call in core.

**Consequences:**
- Dynamic URLs (env/config concatenation) lower recall (A-004) → measured by precision/recall gate on OTel Demo.
- New `RelationKind` value requires contract version note (additive, backward-compatible).

---

### Decision 7: Storage in repo (`docs/field/`), anonymization at export only

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-28 |

**Context:** Records must be reviewable in PRs and by the verifier; own repos are private.

**Choice:** `corpus.yaml` stores `repo_ref` as `sha256:<hex>` for own repos + a local, git-ignored `docs/field/repos.local.yaml` mapping ref → path. Runs stored as JSON under `docs/field/runs/`. `export` re-checks anonymity (no path, name or code outside allow-listed snippet fields) and refuses `AF-FIELD-EXPORT-LEAK`.

**Rationale:** Evidence persisted and diffable; privacy boundary explicit and tested (AT-016).

**Alternatives Rejected:**
1. `.apiforge/` runtime dir — rejected: not reviewable, often ignored.
2. External DB — rejected: violates local-first.

**Consequences:**
- `.gitignore` gains `docs/field/repos.local.yaml`.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/field.py` | Create | Field contracts + enums | @python-developer | None |
| 2 | `src/apiforge/field/__init__.py` | Create | Package exports | (general) | 1 |
| 3 | `src/apiforge/field/errors.py` | Create | `FieldError` + codes | @python-developer | None |
| 4 | `src/apiforge/field/store.py` | Create | Atomic JSON read/write of runs | @python-developer | 1, 3 |
| 5 | `src/apiforge/field/corpus.py` | Create | Corpus/hypothesis load, registration cutoff | @python-developer | 1, 3 |
| 6 | `src/apiforge/field/record.py` | Create | Join ledger/summary/checkpoint; time + contamination checks | @python-developer | 3, 4, 5 |
| 7 | `src/apiforge/field/annotate.py` | Create | Human annotation + blind verifier verdict | @python-developer | 3, 4 |
| 8 | `src/apiforge/field/report.py` | Create | Wilson CI, qualification, H1, A/B | @python-developer | 1, 4, 5 |
| 9 | `src/apiforge/field/export.py` | Create | Anonymized eval export + leak check | @python-developer | 4, 5 |
| 10 | `src/apiforge/cli_field.py` | Create | Typer commands | @python-developer | 5–9 |
| 11 | `src/apiforge/cli.py` | Modify | Register `field_app` | (general) | 10 |
| 12 | `src/apiforge/mcp/tools.py` | Modify | `field_*` tool functions | @python-developer | 5–8 |
| 13 | `src/apiforge/mcp/surface.py` | Modify | Expose field tools in surface | (general) | 12 |
| 14 | `src/apiforge/adapters/http_targets.py` | Create | `http.outbound` extractor | @python-developer | None |
| 15 | `src/apiforge/workspace/inference/__init__.py` | Create | `infer_relations` orchestration | @python-developer | 14, 16 |
| 16 | `src/apiforge/workspace/inference/match.py` | Create | Pure matcher + confidence | @python-developer | None |
| 17 | `src/apiforge/contracts/workspace.py` | Modify | `RelationKind` += `publishes_to_consumer` | (general) | None |
| 18 | `src/apiforge/workspace/graph.py` | Modify | `inferred=` parameter | (general) | 17 |
| 19 | `src/apiforge/cli_workspace.py` | Modify | `--infer` + ledger row `workspace.infer` | @python-developer | 15, 18 |
| 20 | `docs/catalog-contract.md` | Modify | Catalog `AF-FIELD-*`, `AF-WORKSPACE-INFER-*` | @code-documenter | 3, 19 |
| 21 | `docs/field/corpus.yaml` | Create | Corpus skeleton (OTel Demo + placeholders), gate thresholds | (general) | 1 |
| 22 | `docs/field/hypothesis.md` | Create | H1 + refutation criterion | (general) | None |
| 23 | `docs/field/README.md` | Create | Operator protocol (record → annotate → verify → report) | @code-documenter | 10 |
| 24 | `docs/field/ground-truth/otel-demo-relations.yaml` | Create | Hand-curated relation list for precision/recall | (general) | None |
| 25 | `.gitignore` | Modify | `docs/field/repos.local.yaml` | (general) | None |
| 26 | `tests/fixtures/field/` | Create | Ledger/summary/checkpoint samples, corpus, runs | @test-generator | 1 |
| 27 | `tests/fixtures/workspace_infer/` | Create | 3 mini repos: web→payment HTTP, payment→order topic, ambiguous pair | @test-generator | None |
| 28 | `tests/field/test_corpus.py` | Create | AT-002, AT-003 | @test-generator | 5, 26 |
| 29 | `tests/field/test_record.py` | Create | AT-001, AT-006, AT-010, time window | @test-generator | 6, 26 |
| 30 | `tests/field/test_annotate.py` | Create | AT-004, AT-005 | @test-generator | 7, 26 |
| 31 | `tests/field/test_report.py` | Create | AT-007, AT-008, AT-009, AT-015, Wilson values | @test-generator | 8, 26 |
| 32 | `tests/field/test_export.py` | Create | AT-016 | @test-generator | 9, 26 |
| 33 | `tests/field/test_cli_mcp_parity.py` | Create | Refusal code/field/unlock parity CLI↔MCP | @test-generator | 10, 12 |
| 34 | `tests/workspace/test_inference.py` | Create | AT-011, AT-012, AT-014 | @test-generator | 15, 16, 27 |
| 35 | `tests/workspace/test_graph_default.py` | Create | AT-013 byte-identical default graph | @test-generator | 18 |
| 36 | `tests/adapters/test_http_targets.py` | Create | Extractor per client library | @test-generator | 14 |
| 37 | `docs/sdd/API_FORGE_FIELD_VALIDATION/{intent,discover,contract,architecture,plan,build,verify,secure,benchmark,ship}.md` + `evidence/` | Create | Repo SDD artifacts for `sdd check` | @code-documenter | all |
| 38 | host mirrors (`.claude/skills/api-forge-context`, `AGENTS.md` routing) | Modify | Route "field validation" → `apiforge field` | (general) | 10 |

**Total Files:** 38 entries (~46 files incl. SDD phase docs)

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @python-developer | 1, 3–10, 12, 14–16, 19 | Typed pydantic contracts, pure functions, typer CLI — matches project style |
| @test-generator | 26–36 | pytest fixtures + AT-mapped tests |
| @code-documenter | 20, 23, 37 | Catalog + operator protocol + SDD phase docs |
| (general) | 2, 11, 13, 17, 18, 21, 22, 24, 25, 38 | One-line wiring/config edits; build handles directly |
| Review (not file owners) | — | `api-verification-engineer` verifies build receipts; `api-adversarial-critic` reviews gap-report logic (report.py) before ship |

**Agent Discovery:**
- Scanned: `agentspec/3.5.0/agents/**/*.md` + project `.claude/agents/`
- Matched by: file type (.py), purpose (tests/docs), project verification roles

---

## Code Patterns

### Pattern 1: Field error (mirrors `EconomyError`)

```python
from apiforge.contracts.base import ContractError


class FieldError(ContractError):
    def __init__(self, code: str, detail: str, *, field: str, unlock: str) -> None:
        super().__init__(code, detail)
        self.field = field
        self.unlock = unlock


TASK_UNREGISTERED = "AF-FIELD-TASK-UNREGISTERED"
LATE_REGISTRATION = "AF-FIELD-LATE-REGISTRATION"
ENUM = "AF-FIELD-ENUM"
FLAG_CONTAMINATION = "AF-FIELD-FLAG-CONTAMINATION"
TIME_ORDER = "AF-FIELD-TIME-ORDER"
EXPORT_LEAK = "AF-FIELD-EXPORT-LEAK"
RUN_MISSING = "AF-FIELD-RUN-MISSING"
CORPUS_INVALID = "AF-FIELD-CORPUS-INVALID"
```

### Pattern 2: Field-run contract

```python
from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract

Scenario = Literal["maintenance", "evolution", "security", "multi_repo", "incident", "performance"]
ExitReason = Literal[
    "knowledge_gap", "capability_gap", "context_gap", "graph_gap", "tool_gap",
    "ux_gap", "evaluation_gap", "integration_gap", "none",
]
Phase = Literal["baseline", "ab_on"]


class FieldRun(VersionedContract):
    schema: Literal["apiforge/field-run/v1"] = "apiforge/field-run/v1"  # type: ignore[assignment]
    task_id: str
    scenario: Scenario
    repo_ref: str
    phase: Phase
    run_ids: tuple[str, ...] = Field(min_length=1)
    inference_flag: bool  # derived from ledger, never an input
    started_at: str
    ended_at: str
    provider_calls: int | None = None
    context_bytes: int | None = None
    cache_reuse: int | None = None
    time_to_evidence_ms: int | None = None
    time_to_solution_ms: int | None = None
    task_completed: bool | None = None
    exit_reason: ExitReason | None = None
    manual_context_required: bool | None = None
    human_intervention: bool | None = None
    false_positives: int | None = Field(default=None, ge=0)
    false_negatives: int | None = Field(default=None, ge=0)
    verifier_verdict: Literal["agree", "disagree", "unresolved"] | None = None
    sources: tuple[str, ...] = ()  # artifact paths behind automatic values
    unresolved: tuple[str, ...] = ()
```

### Pattern 3: Wilson interval (deterministic, stdlib)

```python
import math

Z95 = 1.959964


def wilson(k: int, n: int, z: float = Z95) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4))
```

### Pattern 4: CLI registration (mirrors `cli_economy.py`)

```python
from pathlib import Path

import typer


def register(field_app: typer.Typer) -> None:
    @field_app.command("report")
    def field_report(
        root: Path = typer.Option(Path("."), "--root"),
        ab: bool = typer.Option(False, "--ab"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Counts, Wilson 95% CI, theme qualification and H1 verdict from verified runs."""
        from apiforge.cli import _echo_json, _run
        from apiforge.field.report import build_report

        _echo_json(_run(lambda: build_report(root, ab=ab)), detail_level)
```

### Pattern 5: Inferred relation

```python
from apiforge.contracts.evidence import EvidenceRecord
from apiforge.contracts.workspace import WorkspaceRelation


def inferred_call(from_id: str, to_id: str, confidence: float, ref: str) -> WorkspaceRelation:
    return WorkspaceRelation(
        relation="calls",
        source="workspace.inference",
        from_id=from_id,
        to_id=to_id,
        evidence=EvidenceRecord(
            level="inferred", source="http.outbound", confidence=confidence, refs=(ref,)
        ),
        limitations=("static inference; not runtime proof",),
    )
```

### Pattern 6: Corpus manifest

```yaml
schema: apiforge/field-corpus/v1
cycle_started_at: null          # written once by first `field record`
gate:
  max_runs: 30
  max_weeks: 4
  min_tasks_per_theme: 5
  min_repos_per_theme: 2
  min_tasks_per_scenario: 5
hypothesis:
  id: H1
  category: graph_gap
  refutation: "graph_gap not qualified while another category qualifies"
repos:
  - ref: oss:open-telemetry/opentelemetry-demo@<commit>
    kind: oss
  - ref: sha256:<hex>           # own repo; path in repos.local.yaml
    kind: own
tasks:
  - id: T001
    scenario: incident
    repo_ref: oss:open-telemetry/opentelemetry-demo@<commit>
    registered_at: "2026-10-01T12:00:00Z"
    prompt: "checkout latency spike after flag X enabled; find cause"
    ground_truth:
      kind: injected_failure
      ref: "feature flag <name>"
```

---

## Data Flow

```text
1. Owner registers tasks in corpus.yaml (+ hypothesis.md) and commits
   │
   ▼
2. Owner runs task with normal API Forge flow (no --infer) → runtime writes ledger/summary/checkpoint
   │
   ▼
3. `apiforge field record --task T --run R... --phase baseline --started .. --ended ..`
   → corpus check → join artifacts → contamination scan → FieldRun JSON (auto fields + sources)
   │
   ▼
4. `apiforge field annotate --task T ...` (human enums)
   `apiforge field verify --task T --verdict agree|disagree|unresolved` (verifier, without human labels in its prompt)
   │
   ▼
5. Gate hit (30 runs / 4 weeks) → `apiforge field report` → critic review
   │
   ▼
6. A/B: multi_repo tasks re-run with `workspace graph --infer`, recorded `--phase ab_on`
   → `apiforge field report --ab`
   │
   ▼
7. `apiforge field export` → evals/corpus/field/ ; ≤2 themes → next SDDs
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|------------------|----------------|
| Economy ledger / runtime store | File read (existing formats) | None (local) |
| API IR builder (`api_ir/builder.py`) | In-process call per repo | None |
| Streaming/messaging adapters | In-process facts | None |
| OpenTelemetry Demo repo | Local clone analyzed offline | None |
| Git | Read-only `git log` in ship evidence only | None |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | corpus, record, annotate, report, export, match, extractor | `tests/field/*`, `tests/workspace/test_inference.py`, `tests/adapters/test_http_targets.py` | pytest (`--basetemp E:/afpt`) | 100% of AT-001…AT-016 |
| Contract | CLI↔MCP refusal parity | `tests/field/test_cli_mcp_parity.py` | pytest + typer CliRunner | every `AF-FIELD-*` |
| Regression | default graph unchanged | `tests/workspace/test_graph_default.py` | golden JSON | byte-identical |
| Determinism | report twice | `test_report.py` | pytest | byte-identical |
| Field acceptance | precision/recall on OTel Demo | `docs/field/ground-truth/` + evidence | manual run, recorded in `docs/sdd/.../evidence/` | P≥0.80, R≥0.60 |
| Full suite | whole repo | — | pytest | once before ship |
| SDD | `apiforge sdd check --root docs/sdd` | — | CLI | green |

AT mapping: AT-001/006/010 → test_record; AT-002/003 → test_corpus; AT-004/005 → test_annotate; AT-007/008/009/015 → test_report; AT-011/012/014 → test_inference; AT-013 → test_graph_default; AT-016 → test_export.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Missing ledger/summary/checkpoint | Field `null` + `unresolved_reason`; record still written | No |
| Unregistered / late task | `FieldError` refusal (code, field, unlock) | No |
| Invalid enum / time order | `FieldError` refusal | No |
| Contamination | `AF-FIELD-FLAG-CONTAMINATION`, record not written | No |
| Ambiguous inference target | Candidates ≤0.45 + `unresolved` entry | No |
| Export leak detected | `AF-FIELD-EXPORT-LEAK`, nothing written | No |
| Ledger persist failure on `workspace.infer` | Existing `AF-ECONOMY-LEDGER-PERSIST` surfaced as unresolved | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `gate.max_runs` | int | 30 | Cycle stop by count |
| `gate.max_weeks` | int | 4 | Cycle stop by time |
| `gate.min_tasks_per_theme` | int | 5 | Theme qualification |
| `gate.min_repos_per_theme` | int | 2 | Theme qualification |
| `gate.min_tasks_per_scenario` | int | 5 | Coverage warning in report |
| `hypothesis.category` | ExitReason | `graph_gap` | H1 |
| `workspace graph --infer` | CLI flag | off | Only entry to inference |

---

## Security Considerations

- Own-repo paths never enter tracked files; `repos.local.yaml` git-ignored; export leak check refuses on any path/name/code outside allow-list.
- No network, no provider SDK, no live AWS/DB/broker; extractor reads local files only.
- Verifier blindness: `field verify` CLI does not print human labels; README instructs verifier prompts to exclude them.
- Refusals carry `unlock` text without echoing sensitive values.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | None new; outputs are JSON payloads via `_echo_json` |
| Metrics | FieldRun automatic fields derived from economy ledger |
| Audit | `workspace.infer` ledger rows; `sources` list on every FieldRun |

---

## Pipeline Architecture (if applicable)

N/A — no scheduled pipeline; local, operator-driven records. Schema evolution: `field-run/v1` additive-only; breaking change → `v2` with reader for v1.

---

## Build Order (dependency layers)

```text
L0: contracts/field.py, field/errors.py, contracts/workspace.py (Literal), adapters/http_targets.py, workspace/inference/match.py
L1: field/store.py, field/corpus.py, workspace/inference/__init__.py, workspace/graph.py
L2: field/record.py, field/annotate.py, field/report.py, field/export.py, cli_workspace.py
L3: cli_field.py, cli.py, mcp/tools.py, mcp/surface.py
L4: docs (catalog, field/, sdd), host mirrors, fixtures+tests per layer
```
No cycles: `field/*` reads ledger via `economy.run_ledger` (one-way); `workspace/inference` never imports `field`.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | design-agent | Initial version |
| 1.1 | 2026-09-28 | ship-agent | Shipped and archived |

---

## Next Step

**Ready for:** `/ship .claude/sdd/features/DEFINE_API_FORGE_FIELD_VALIDATION.md`
