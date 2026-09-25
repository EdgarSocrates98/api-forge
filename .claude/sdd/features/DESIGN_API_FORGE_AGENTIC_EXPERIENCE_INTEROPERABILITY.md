# DESIGN: API Forge Agentic Experience and Interoperability

> Arquitetura para uma TUI canônica e para as bases evidence-driven de knowledge, hosts, Python, CLI e debate.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_AGENTIC_EXPERIENCE_INTEROPERABILITY |
| **Date** | 2026-09-23 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_AGENTIC_EXPERIENCE_INTEROPERABILITY.md](./DEFINE_API_FORGE_AGENTIC_EXPERIENCE_INTEROPERABILITY.md) |
| **Status** | ✅ Complete (Built) |

---

## Architecture Overview

```text
┌────────────────────────────────────────────────────────────────────────────┐
│              API FORGE AGENTIC EXPERIENCE — LOCAL CONTROL PLANE             │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Textual TUI ─────┐                                                       │
│  Rich fallback ───┼──► ExperienceProjection / RuntimeExperience           │
│  CLI / JSON / MCP ┘                    │                                  │
│                                       ▼                                   │
│  EvidenceContract ◄── KnowledgeFreshness ◄── read-only receipts           │
│  HostNegotiation  ◄── host declarations / parity evidence                 │
│  PythonMatrix     ◄── bounded local/CI execution receipts                 │
│  AdaptiveDebate   ◄── fake/model adapters + policy + replay               │
│                                       │                                   │
│                                       ▼                                   │
│             Policy → ControlPlane → RunStore → Verifier → Eval Gate       │
│                                       │                                   │
│                         events / artifacts / hashes / gaps                │
└────────────────────────────────────────────────────────────────────────────┘
```

The dependency direction is intentionally one-way: presentation imports
application projections; application imports contracts and existing services;
adapters implement protocols; the runtime remains the authority for state and
transitions. Textual is optional, and the Rich/CLI/JSON projection is always
available for headless environments.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `ExperienceProjection` | Normalize status, review, doctor, resume, evidence, capabilities and debate payloads for all surfaces | Python dataclasses/Pydantic, existing RuntimeExperience |
| TUI shell | Screens, navigation, actions and refresh without direct persistence access | Optional Textual 8.x + Rich fallback |
| Evidence contract | Formalize level, source, confidence, limitations and refs across artifacts | Pydantic versioned contracts |
| Knowledge freshness | Validate pack source metadata and read-only receipts against declared windows | Existing YAML loader + SHA-256 + integration receipts |
| Host negotiation | Resolve requested capability against per-host declarations, prerequisites and evidence | Host-neutral dataclasses/protocols |
| Python matrix | Record observed interpreter/version/environment results without extrapolation | Existing migration matrix + execution receipts |
| CLI modules | Move command groups behind thin modules while retaining the existing app and aliases | Typer, compatibility facade |
| Adaptive debate | Choose bounded participants/quorum by risk and budget; persist dissent and replay | Existing debate service + fake/model adapter protocol |
| Quality gate | Run unit, integration, golden, holdout and mutation evidence per slice | pytest + existing eval gate |

---

## Key Decisions

### Decision 1: TUI is a projection, not a second runtime

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-23 |

**Context:** The project already has canonical control state, application services,
policy and evidence semantics. A UI-specific state machine would create drift and
make a successful screen different from a successful CLI/MCP run.

**Choice:** `ExperienceProjection` converts canonical service payloads into stable
view models. TUI actions call application services, which call policy and
ControlPlane; the TUI never writes stores or external adapters directly.

**Rationale:** This follows the clean-architecture dependency rule and the existing
`RuntimeExperience` pattern. It also allows a headless fallback and makes snapshot
parity testable.

**Alternatives Rejected:**
1. TUI-specific store access — rejected because it bypasses policy, replay and audit.
2. A second orchestration engine in the UI — rejected because it duplicates lifecycle semantics.

**Consequences:**
- Some screens require new application projections before they can be rendered.
- All surfaces benefit from the same error/gap/evidence behavior.

---

### Decision 2: Optional Textual with Rich/JSON fallback

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-23 |

**Context:** The requested UX is a complete TUI, but CI, pipes and minimal hosts
must continue to operate without a visual terminal dependency.

**Choice:** Add a `tui` optional dependency group with Textual and Rich support;
the base install exposes a fallback projection and a clear `AF-TUI-UNAVAILABLE`
result when the full TUI is requested without its optional dependency.

**Rationale:** Textual officially exposes app composition, screens, widgets,
workers and testing surfaces, while the project remains usable headlessly. The
dependency is isolated from the deterministic core and can be installed only by
users who need the rich terminal surface.

**Alternatives Rejected:**
1. `curses` as the only implementation — rejected for poorer portability and test ergonomics.
2. Mandatory Textual dependency — rejected because offline/headless installs must remain small.

**Consequences:** Optional dependency installation and TUI-specific tests become a
release matrix concern. Base CLI behavior remains dependency-free.

---

### Decision 3: Evidence Levels are additive and monotonic

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-23 |

**Context:** `EvidenceLevel` currently exists for adapter executions, while runs,
knowledge, host declarations, Python cells and debates need the same distinction.

**Choice:** Introduce a shared versioned evidence contract with a closed vocabulary
and preserve the existing adapter values. Missing legacy fields load as `unknown`;
verification can promote an observation only when a receipt/proof reference exists.

**Rationale:** A monotonic evidence model prevents heuristic or declared data from
being treated as verified. It follows the project rule that missing evidence is
`unresolved`, not zero or success.

**Alternatives Rejected:**
1. A numeric score only — rejected because score alone loses provenance and limitations.
2. Per-module evidence enums — rejected because surfaces would become incompatible.

**Consequences:** Contracts gain optional fields and migrations; every new result
must carry level, refs and limitations where applicable.

---

### Decision 4: Knowledge freshness is read-only and receipt-backed

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-23 |

**Context:** The local Knowledge Pack loader validates schema and source authority,
but it does not yet express observed freshness or external update evidence.

**Choice:** Add optional pack freshness metadata and a verifier that compares
source hash, version, observed timestamp and declared freshness window. External
refresh remains a GET-only adapter producing a receipt; no pack is rewritten by
the core.

**Rationale:** This preserves offline-first behavior and makes stale knowledge
visible without claiming a provider is current. It extends the existing external
receipt pattern instead of introducing a new network path.

**Alternatives Rejected:**
1. Silent auto-refresh — rejected because it mutates project knowledge and hides provenance.
2. Treating `verified` date as freshness — rejected because verification date is not observation time.

**Consequences:** Existing packs remain valid with `unknown` freshness until
metadata is added; stale/unresolved states must be rendered by every surface.

---

### Decision 5: Host negotiation resolves intersections, never equivalence

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-23 |

**Context:** The project has host adapters and parity reporting, but host-specific
subagents, MCP, hooks and slash commands differ.

**Choice:** Define host declarations containing host, capability, support state,
prerequisites, limits and evidence refs. Negotiation returns the eligible
intersection for a request plus explicit unsupported/unresolved reasons.

**Rationale:** This gives Codex, Claude, Devin and Copilot a common protocol without
claiming they expose the same runtime. It reuses current host layouts and parity
limitations.

**Alternatives Rejected:**
1. A single boolean `full_parity` — rejected because it erases per-capability differences.
2. Host SDK calls from core — rejected because host integrations belong behind adapters.

**Consequences:** Capability requests need stable identifiers and prerequisite
resolution; host declarations must be refreshed independently.

---

### Decision 6: Python compatibility is an observed matrix

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-23 |

**Context:** The project currently declares one Python range in `pyproject.toml`,
while migration already has a version matrix abstraction.

**Choice:** Extend the existing matrix with execution receipts and publish only
cells that ran under a declared interpreter/environment. At least two versions,
including the baseline, are the first target; unsupported cells remain unresolved.

**Rationale:** Compatibility claims need observed proof. Reusing migration models
avoids another version vocabulary and enables the same matrix to support future
language/runtime expansion.

**Alternatives Rejected:**
1. Claiming support from `requires-python` alone — rejected because metadata is not execution proof.
2. Inferring neighboring versions — rejected because runtime behavior can differ.

**Consequences:** CI/local matrix receipts become part of release evidence; the
current version remains the baseline until another cell passes.

---

### Decision 7: Debate is bounded plan → submissions → review

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-23 |

**Context:** The existing debate service enforces evidence and two-sided quorum,
but does not adapt participants or budget by risk and does not model provider
adapters as a reproducible boundary.

**Choice:** Add an adaptive policy that selects a bounded participant set,
quorum, retry budget and escalation based on risk. Fake adapters are mandatory
for local evals; real model adapters are optional, read-only with respect to the
project core, and must return structured submissions with evidence refs.

**Rationale:** The state-machine pattern makes transitions explicit and auditable;
the evaluation pattern requires structured outputs and quality gates. The existing
service already persists disagreement, so the change can remain additive.

**Alternatives Rejected:**
1. Unbounded multi-model fan-out — rejected for cost, noise and non-reproducibility.
2. Model text as a decision — rejected because unsupported opinions are refused.

**Consequences:** Debate results include policy, budget, participant declarations,
dissent and replay data; model quality remains unresolved without independent eval.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `pyproject.toml` | Modify | Optional `tui` dependencies and entrypoint metadata | @python-developer | 2, 3 |
| 2 | `src/apiforge/contracts/experience.py` | Create | Stable projection/action contracts for all surfaces | @python-developer | 3 |
| 3 | `src/apiforge/contracts/evidence.py` | Create | Shared Evidence Level and proof metadata contract | @python-developer | None |
| 4 | `src/apiforge/contracts/knowledge.py` | Create | Pack freshness and source observation contract | @data-contracts-engineer | 3 |
| 5 | `src/apiforge/contracts/host.py` | Create | Host declaration, negotiation request and resolution contract | @python-developer | 3 |
| 6 | `src/apiforge/contracts/compatibility.py` | Create | Python matrix cell and execution receipt contract | @python-developer | 3 |
| 7 | `src/apiforge/contracts/debate.py` | Create | Adaptive policy, participant and replay contracts | @genai-architect | 3 |
| 8 | `src/apiforge/application/experience_projection.py` | Create | Canonical view models from RuntimeExperience | @python-developer | 2 |
| 9 | `src/apiforge/tui/__init__.py` | Create | Optional TUI public API and availability check | @python-developer | 8, 10 |
| 10 | `src/apiforge/tui/app.py` | Create | Textual app, screens, actions and bindings | @python-developer | 8, 9, 11 |
| 11 | `src/apiforge/tui/fallback.py` | Create | Rich/CLI/JSON headless rendering | @python-developer | 8 |
| 12 | `src/apiforge/tui/styles.tcss` | Create | TUI layout/theme without business logic | @python-developer | 10 |
| 13 | `src/apiforge/knowledge/freshness.py` | Create | Local freshness verification over pack metadata/receipts | @data-quality-analyst | 4 |
| 14 | `src/apiforge/agentops/negotiation.py` | Create | Evidence-aware host capability resolution | @genai-architect | 5 |
| 15 | `src/apiforge/migration/matrix.py` | Modify | Attach observed execution receipts and unresolved cells | @python-developer | 6 |
| 16 | `src/apiforge/debate/service.py` | Modify | Adaptive bounded policy and replay metadata | @genai-architect | 7 |
| 17 | `src/apiforge/cli.py` | Modify | Thin TUI/fallback entrypoints and preserve expert commands | @python-developer | 8, 9, 11 |
| 18 | `src/apiforge/cli_tui.py` | Create | Isolated CLI command group for TUI invocation | @python-developer | 10, 11 |
| 19 | `src/apiforge/knowledge/loader.py` | Modify | Load optional freshness metadata additively | @data-contracts-engineer | 4, 13 |
| 20 | `tests/contracts/test_experience.py` | Create | Projection/action contract validation | @test-generator | 2 |
| 21 | `tests/contracts/test_evidence.py` | Create | Evidence monotonicity and legacy loading | @test-generator | 3 |
| 22 | `tests/tui/test_fallback.py` | Create | Headless parity and unavailable TUI behavior | @test-generator | 8, 11 |
| 23 | `tests/tui/test_app.py` | Create | Textual pilot/snapshot tests when optional dependency exists | @test-generator | 10, 12 |
| 24 | `tests/knowledge/test_freshness.py` | Create | Fresh/stale/unresolved receipts and pack metadata | @data-quality-analyst | 4, 13, 19 |
| 25 | `tests/agentops/test_negotiation.py` | Create | Four-host capability intersection and limitations | @test-generator | 5, 14 |
| 26 | `tests/migration/test_matrix_receipts.py` | Create | Observed Python cells and unresolved versions | @test-generator | 6, 15 |
| 27 | `tests/debate/test_adaptive.py` | Create | Risk/budget/quorum/dissent/replay scenarios | @genai-architect | 7, 16 |
| 28 | `tests/e2e/test_experience_parity.py` | Create | TUI/Rich/CLI/JSON projection equivalence | @test-generator | 8, 10, 11, 17 |
| 29 | `tests/fixtures/tui/experience_runs.yaml` | Create | TUI execution/governance scenarios | @test-generator | 20, 28 |
| 30 | `tests/fixtures/knowledge/freshness.yaml` | Create | Freshness golden/holdout/mutation cases | @data-quality-analyst | 24 |
| 31 | `tests/fixtures/hosts/negotiation.yaml` | Create | Four-host declarations and limitations | @test-generator | 25 |
| 32 | `tests/fixtures/compatibility/python-matrix.yaml` | Create | Baseline and additional observed matrix cells | @python-developer | 26 |
| 33 | `tests/fixtures/debate/adaptive.yaml` | Create | Deterministic bounded debate cases | @genai-architect | 27 |
| 34 | `tests/evals/cases/experience_interoperability.yaml` | Create | Mandatory slice eval declarations | @test-generator | 22, 24, 25, 26, 27, 28 |

**Total Files:** 34 planned files across the program; build may split them into
validated slices, but no file is allowed to bypass its listed contract/test
dependency.

---

## Agent Assignment Rationale

> Agents discovered from `${CLAUDE_PLUGIN_ROOT}/agents/` and matched by file purpose, KB domain and path.

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @python-developer | 1, 2, 3, 5, 6, 8-12, 15, 17, 18, 32 | Python contracts, clean layering, optional runtime surface and typed projection |
| @genai-architect | 7, 14, 16, 27, 33 | State machines, guardrails, multi-agent negotiation and bounded debate |
| @data-contracts-engineer | 4, 19 | Versioned source/freshness contract and Knowledge Pack schema |
| @data-quality-analyst | 13, 24, 30 | Freshness/timeliness dimensions, receipts and quality gates |
| @test-generator | 20-23, 25-26, 28-29, 31, 34 | Fixtures, integration, snapshots, parity and mandatory evals |

**Agent Discovery:**

- Scanned `${CLAUDE_PLUGIN_ROOT}/agents/**/*.md`.
- Matched by file type, purpose keywords, path, KB domain and existing project pattern.
- Direct execution remains acceptable if the host does not expose subagent tools;
  the manifest and assignments remain the audit record.

---

## Code Patterns

### Pattern 1: Canonical projection boundary

```python
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ExperienceView:
    status: str
    gaps: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    actions: tuple[str, ...]


class ExperienceReader(Protocol):
    def status(self, root: Path, task_id: str) -> dict[str, Any]: ...


def project_status(reader: ExperienceReader, root: Path, task_id: str) -> ExperienceView:
    payload = reader.status(root, task_id)
    return ExperienceView(
        status=str(payload.get("status", "REVIEW")),
        gaps=tuple(sorted(str(item) for item in payload.get("gaps", []))),
        evidence_refs=tuple(sorted(str(item) for item in payload.get("evidence_refs", []))),
        actions=("review", "resume", "doctor"),
    )
```

This applies the `python` clean-architecture and protocol patterns: UI consumes
an interface and immutable view data; it cannot mutate the runtime store.

### Pattern 2: Optional TUI with explicit fallback

```python
def run_tui(root: Path, task_id: str) -> dict[str, object]:
    try:
        from apiforge.tui.app import ForgeApp
    except ImportError:
        return render_fallback(root, task_id, code="AF-TUI-UNAVAILABLE")
    return ForgeApp(root=root, task_id=task_id).run()
```

The optional import is isolated in the presentation boundary. The fallback emits
the same canonical projection and a named refusal/unlock when the extra is absent.

### Pattern 3: Freshness verification without implicit network

```python
def verify_pack_freshness(pack: Pack, receipt: Receipt | None, now: datetime) -> Freshness:
    if receipt is None:
        return Freshness(status="unresolved", gaps=("missing external receipt",))
    if receipt.source_hash != pack.source_hash:
        return Freshness(status="stale", gaps=("source hash mismatch",))
    if now - receipt.observed_at > pack.freshness_window:
        return Freshness(status="stale", gaps=("receipt outside freshness window",))
    return Freshness(status="fresh", evidence_refs=(receipt.receipt_id,))
```

This follows data-quality timeliness and the existing read-only receipt boundary;
the verifier never fetches or rewrites data.

### Pattern 4: Host negotiation as intersection

```python
from collections.abc import Sequence


def negotiate(request: CapabilityRequest, declarations: Sequence[HostDeclaration]) -> Resolution:
    eligible = []
    unresolved = []
    for declaration in declarations:
        capability = declaration.capabilities.get(request.capability)
        if capability is None:
            unresolved.append(f"{declaration.host}: missing capability")
        elif capability.supported and request.prerequisites.issubset(capability.prerequisites):
            eligible.append(declaration.host)
        else:
            unresolved.append(f"{declaration.host}: unsupported or missing prerequisite")
    return Resolution(
        capability=request.capability, eligible_hosts=tuple(eligible), gaps=tuple(unresolved)
    )
```

The result reports capability-level evidence and limitations, never a global
`full_parity` claim.

### Pattern 5: Bounded adaptive debate

```python
policy = debate_policy.for_risk(risk="high", budget=3)
participants = adapters.select(policy.max_participants)
submissions = [adapter.submit(question, evidence_refs) for adapter in participants]
result = referee.close(
    submissions=submissions,
    quorum=policy.quorum,
    preserve_dissent=True,
    replay_id=stable_id("debate-replay", submissions),
)
```

State transitions remain explicit (`open → submissions → resolved|unresolved`),
and structured outputs follow the prompt-engineering validation pattern.

### Pattern 6: Configuration structure

```yaml
experience:
  tui:
    optional_dependency: true
    fallback: rich
  evidence:
    require_independent_verification: true
  debate:
    max_participants: 3
    max_rounds: 2
    preserve_dissent: true
  python_matrix:
    require_observed_cell: true
```

All tunables are policy/config data; no host, provider or production capability
is inferred from a default.

---

## Data Flow

```text
1. User starts TUI/Rich/CLI/MCP
   │
   ▼
2. Experience command loads persisted run/pack/host/matrix/debate artifacts
   │
   ▼
3. Application service validates contract version and computes projection
   │
   ├── status/review/doctor → ControlPlane + verifier evidence
   ├── knowledge            → local metadata + external receipt verifier
   ├── host                 → declarations + prerequisite resolver
   ├── Python               → observed matrix cells + execution receipts
   └── debate               → bounded policy + adapters + replay
   │
   ▼
4. Policy/eval gate preserves unresolved, refusal codes, gaps and next action
   │
   ▼
5. Projection renders the same canonical payload in Textual, Rich, CLI and JSON
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| Textual/Rich | Optional local Python dependencies | None |
| Knowledge authority | Existing read-only HTTP adapter/receipt | Adapter-owned; no core credential |
| Codex/Claude/Devin/Copilot | Local declarations and host mirrors | Host-managed; not asserted by core |
| Python interpreters/CI | Local process execution and receipt | Allowlisted process, no provider credential |
| Model providers | Optional adapter protocol for debate | Provider adapter/policy; no SDK import in core |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Contracts, projection, freshness, negotiation, matrix, adaptive policy | `tests/contracts`, `tests/knowledge`, `tests/agentops`, `tests/migration`, `tests/debate` | pytest, Pydantic validation | Every state and refusal path |
| Integration | Application service and fallback parity | `tests/tui/test_fallback.py`, `tests/e2e/test_experience_parity.py` | pytest, tmp_path, CliRunner | 100% canonical commands in fixture matrix |
| Optional TUI | Screens, keybindings, actions, unavailable dependency path | `tests/tui/test_app.py` | Textual pilot when installed | Boot, navigation, action and error paths |
| Compatibility | Legacy packs/runs/contracts and CLI aliases | `tests/contracts`, existing runtime/knowledge/CLI suites | pytest, snapshot payloads | No silent mutation or semantic drift |
| Eval gate | Golden, holdout, mutation, stale evidence, dissent and host limitations | `tests/evals/cases/experience_interoperability.yaml` | Existing offline eval gate | Mandatory cases block slice |
| Static quality | Full project lint/type/SDD/release checks | CI/local | Ruff, mypy, spec-linter, `apiforge sdd check` | Zero findings in full workspace |

Acceptance mapping: AT-001–AT-004 → TUI/fallback/e2e; AT-005–AT-007 → evidence/
knowledge tests; AT-008 → negotiation tests; AT-009 → matrix receipts; AT-010 →
CLI parity; AT-011–AT-012 → debate tests; AT-013 → eval gate; AT-014 → compatibility
tests and existing suites.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| TUI optional dependency missing | Render fallback and `AF-TUI-UNAVAILABLE` with install unlock | No |
| Projection contract mismatch | Preserve legacy payload, emit `AF-EXPERIENCE-CONTRACT` and `REVIEW` | No |
| Missing/stale freshness receipt | Return `stale`/`unresolved`, preserve source and next action | External refresh only through explicit read-only adapter |
| Host unsupported/prerequisite missing | Exclude host, preserve limitation and evidence refs | No automatic retry |
| Python cell not observed | Keep matrix cell `unresolved` | Retry only in declared matrix runner |
| Debate adapter timeout/invalid output | Record adapter failure, preserve dissent and continue only within budget | Bounded retry |
| Debate no quorum | Close `unresolved` with `AF-DEBATE-NO-QUORUM` | No automatic consensus |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `experience.tui.optional_dependency` | bool | `true` | Whether Textual is an optional surface |
| `experience.tui.fallback` | string | `rich` | Headless projection mode |
| `experience.evidence.require_independent_verification` | bool | `true` | Blocks false `DONE` |
| `experience.debate.max_participants` | int | `3` | Upper bound for adaptive debate |
| `experience.debate.max_rounds` | int | `2` | Upper bound for retries/review |
| `experience.debate.preserve_dissent` | bool | `true` | Keeps disagreement in outcome |
| `experience.python_matrix.require_observed_cell` | bool | `true` | No inferred compatibility |

---

## Security Considerations

- The TUI is an untrusted presentation surface: all mutations remain behind policy, ControlPlane, sandbox and verifier.
- External freshness is GET-only and receipts are evidence of an observation, not authorship, permissions or production health.
- Host declarations and model outputs are untrusted input; validate schemas, allowlists, hashes and evidence refs before projection.
- Debate adapters cannot publish conclusions without structured evidence and quorum; unsupported opinions remain unresolved.
- Optional UI dependencies and provider adapters remain outside the deterministic core boundary.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Canonical event IDs for projection, refresh observation, negotiation, matrix cell, debate round and refusal |
| Metrics | Local aggregates: screen/action count, fallback count, freshness status, eligible hosts, observed matrix cells, quorum/dissent and eval outcomes |
| Tracing | Replay-normalized command/projection/control events with input/result hashes; no external tracing service required |

Missing metrics remain `unresolved`, never zero. Every terminal result includes
status, gaps, evidence refs, refusal/error code when applicable and next safe action.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-23 | design-agent | Architecture for TUI-first interoperability program; KB-grounded contracts, adapters, gates and 34-file manifest |

---

## Next Step

**Ready for:** `/ship .claude/sdd/features/DEFINE_API_FORGE_AGENTIC_EXPERIENCE_INTEROPERABILITY.md`
