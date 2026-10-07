# DESIGN: API Forge Economy — Context Gateway (P0)

> Technical design for implementing API_FORGE_ECONOMY_CONTEXT_GATEWAY (Onda 0 medição + Onda 1 Context Gateway)

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_CONTEXT_GATEWAY |
| **Date** | 2026-09-27 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_ECONOMY_CONTEXT_GATEWAY.md](./DEFINE_API_FORGE_ECONOMY_CONTEXT_GATEWAY.md) |
| **Status** | ✅ Shipped |
| **Confidence** | 0.90 (codebase patterns + KB pydantic/testing; graph→source span mapping validated in build, A-001) |

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                 SURFACES (thin, same payload)                                │
│  CLI context capsule|expand      CLI economy stats|explain   CLI evals economy│
│  MCP context_capsule|expand      MCP economy_stats|explain                    │
└───────────────┬──────────────────────────────┬──────────────────────┬────────┘
                │                              │                      │
                ▼                              ▼                      ▼
┌──────────────────────────────┐  ┌───────────────────────────┐  ┌──────────────────┐
│ context/gateway/             │  │ economy/run_ledger.py     │  │ evals/economy.py │
│  capsule.build_capsule()     │  │  RunLedger/CostVector     │  │  baseline|run    │
│   L0 intent                  │  │  append(entry)            │  │  recall, median  │
│   L1 ContextService.resolve ─┼──┼▶ stats(by source/run)     │  │  gate SC2/SC3    │
│   L2 assess_graph_impact     │  │  explain(run) rules-only  │  └────────┬─────────┘
│   L3 refs + dedup + budget   │  │  legacy reader (dual)     │           │
│   L4 focused spans           │  └─────────────▲─────────────┘           │
│  refs.CtxStore put/get/verify│                │ record()                │
│  canonical.dumps()           │────────────────┘                         │
└──────────────┬───────────────┘                                          │
               ▼                                                          ▼
   <root>/.apiforge/ctx/<sha256>        <root>/.apiforge/economy.jsonl   evals/corpus/economy/*.yaml
   (content-addressed objects)          (legacy + run entries, one file) (12 cases + baseline.json)
                                                ▲
                                   economy report (unchanged, reads legacy fields)
```

Layering (no cycles): `contracts` ← `economy` ← `context/gateway` ← `evals/economy` ← surfaces (`cli_context.py`, `cli_economy.py`, `mcp/tools.py`). Gateway never imports surfaces; ledger never imports gateway.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `contracts/context.py` (+) | `ContextRef/v1`, `ContextCapsule/v1`, `CapsuleBudget/v1`, `CapsuleRefusal/v1` | pydantic `VersionedContract` (frozen, extra=forbid) |
| `contracts/economy.py` (new) | `CostVector/v1`, `RunLedgerEntry/v1` | pydantic `VersionedContract` |
| `context/gateway/canonical.py` | Canonical JSON bytes + LF-normalized sha256 | stdlib `json`, `hashlib` |
| `context/gateway/refs.py` | `CtxStore`: put/get/verify under `.apiforge/ctx/` | stdlib, atomic write via temp+rename |
| `context/gateway/levels.py` | L0–L4 selection pipeline | `ContextService`, `graph.impact.assess_graph_impact` |
| `context/gateway/dedup.py` | Canonical schema + parity/delta for DTO/SDK | pure functions |
| `context/gateway/capsule.py` | `build_capsule()` / `expand_ref()` orchestration + budget | composes above |
| `economy/run_ledger.py` | Append `RunLedgerEntry`, `stats()`, `explain()`, dual reader | stdlib json; reuses `ledger_path` |
| `evals/economy.py` | Load corpus, record baseline, run capsule, compute recall/median, gate | stdlib + yaml |
| Surfaces | CLI (`cli_context.py`, new `cli_economy.py`) + MCP tools | typer, existing `_run`/`_echo_json`/`_call` |

---

## Key Decisions

### Decision 1: `ctx://sha256/<hex>` is identity; kind/label are metadata

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-27 |

**Context:** DEFINE Q2 — ref format readable (`ctx://schema/OrderRequest`) vs pure hash. Readable names collide across revisions; hash guarantees integrity and dedup (G4, G5).

**Choice:** URI `ctx://sha256/<64 hex>`. `ContextRef` carries `kind` (`contract|schema|code|test|policy|knowledge`), `label` (e.g. `schema:OrderRequest`), `source` path, `span` (`start_line`,`end_line` or null), `revision` (git SHA or `worktree`), `size_bytes`, `provenance` (rule id that selected it).

**Rationale:** Integrity check is a single comparison; identical content across targets dedups for free; label keeps human/agent readability without being load-bearing.

**Alternatives Rejected:**
1. `ctx://<kind>/<name>` — rejected: not unique across revisions, needs separate integrity field.
2. `ctx://<kind>/<name>@sha256:<hex>` — rejected: two sources of truth; parsing burden with no P0 gain.

**Consequences:**
- Agents must read `label` to understand a ref (accepted; capsule lists labels).
- Free dedup and tamper detection (`AF-CTX-HASH-MISMATCH`).

---

### Decision 2: Single ledger file, versioned entries, dual reader

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-27 |

**Context:** G6 requires `RunLedger`+`CostVector` while `economy report` must stay byte-identical (AT-009). Existing lines are `{verb, detail_level, payload_bytes, ...}`.

**Choice:** Keep `.apiforge/economy.jsonl`. New entries are written by `run_ledger.append()` as a **superset** of legacy fields: `{verb, detail_level, payload_bytes, schema:"apiforge/run-ledger-entry/v1", run_id, source, cost:{CostVector}}`. `ledger.report()` untouched (reads only legacy keys). `run_ledger.stats()` reads both: lines without `schema` go to `source: legacy`.

**Rationale:** Zero migration, `report` behaviour preserved by construction, one append path, no second file to keep in sync.

**Alternatives Rejected:**
1. Separate `run-ledger.jsonl` — rejected: double writes, divergence risk, `report` blind to new calls.
2. Rewrite legacy lines — rejected: mutates history; violates append-only.

**Consequences:**
- `report` counts gateway calls too (desired: bytes are bytes).
- Entry size grows ~150 bytes; acceptable.

---

### Decision 3: Budget exhaustion and missing graph are *partial results*, not crashes; tampering is a refusal

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-27 |

**Context:** DEFINE Q1 — exit code for degraded capsule. `ContextResult.status` already models `ready|degraded|unresolved|blocked`.

**Choice:**
- `AF-CONTEXT-BUDGET-EXHAUSTED` → capsule returned with `status: "unresolved"`, `reached_level`, refusal entry; **exit 0**; no ref partially included (whole ref or none).
- `AF-CTX-GRAPH-UNAVAILABLE` → capsule `status: "degraded"`, levels L0/L1 only, refusal in `unresolved`; **exit 0**.
- `AF-CTX-REF-NOT-FOUND`, `AF-CTX-HASH-MISMATCH`, `AF-CTX-REF-INVALID` → raise `ContractError` → existing `_run` refusal path (non-zero, `code`/`field`/`unlock` preserved).

**Rationale:** Partial capsules are still useful evidence and honest (no silent downgrade — status + code are explicit). Integrity failures must never return content.

**Alternatives Rejected:**
1. Non-zero exit for budget exhaustion — rejected: breaks agent flows that want the partial capsule to decide next expansion.
2. Truncate the last ref to fit budget — rejected: silent evidence loss.

**Consequences:**
- Callers must read `status`; documented in skill routing + catalog.

---

### Decision 4: Baseline = what an agent reads today

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-27 |

**Context:** A-002 — `context resolve` payload alone may not contain evidence (unfair baseline).

**Choice:** `baseline_bytes(case)` = canonical bytes of `context resolve --scope target --target <t>` payload **+** full UTF-8 bytes of every distinct file named in the case's `required_refs`. `baseline_recall` = fraction of `required_refs` whose `path`+`symbol` appear in that material (normally 1.0).

**Rationale:** Models the status quo "resolve then Read whole files"; makes SC2 meaningful (capsule must match full-file recall) and SC3 honest.

**Alternatives Rejected:**
1. Baseline = `context resolve` only — rejected: recall near 0, SC2 trivial.
2. Baseline = whole repo — rejected: inflates savings.

**Consequences:**
- Baseline recorded once into `evals/corpus/economy/baseline.json` (hash of fixture tree included); re-recorded only via explicit `--record-baseline`.

---

### Decision 5: Deterministic canonical serialization with LF normalization

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-27 |

**Context:** SC4/AT-007 byte-identical capsules; A-006 Windows CRLF.

**Choice:** `canonical.dumps(obj) = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")`. Content hashed after `text.replace("\r\n", "\n")`. Tuples ordered by `(kind, label, source, span)`. No timestamps inside capsule body (run timestamp lives only in ledger).

**Rationale:** Stable hashes across OS; reproducible benchmarks.

**Alternatives Rejected:**
1. Hash raw bytes — rejected: CRLF checkout breaks AT-007 cross-OS.

**Consequences:** Stored object content is LF-normalized (expand returns LF).

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/context.py` | Modify | Add `ContextRef`, `CapsuleBudget`, `CapsuleRefusal`, `ContextCapsule` | @python-developer | None |
| 2 | `src/apiforge/contracts/economy.py` | Create | `CostVector`, `RunLedgerEntry` | @python-developer | None |
| 3 | `src/apiforge/contracts/registry.py` | Modify | Register 6 new `*/v1` contracts | @python-developer | 1, 2 |
| 4 | `src/apiforge/contracts/__init__.py` | Modify | Export new contracts | @python-developer | 1, 2 |
| 5 | `src/apiforge/context/gateway/__init__.py` | Create | Public API `build_capsule`, `expand_ref` | @python-developer | 6–10 |
| 6 | `src/apiforge/context/gateway/canonical.py` | Create | Canonical bytes + sha256 | @python-developer | None |
| 7 | `src/apiforge/context/gateway/refs.py` | Create | `CtxStore` put/get/verify | @python-developer | 1, 6 |
| 8 | `src/apiforge/context/gateway/dedup.py` | Create | Canonical schema + parity/delta | @python-developer | 1 |
| 9 | `src/apiforge/context/gateway/levels.py` | Create | L0–L4 selection | @python-developer | 1, 7 |
| 10 | `src/apiforge/context/gateway/capsule.py` | Create | Orchestration + budget + ledger record | @python-developer | 6–9, 11 |
| 11 | `src/apiforge/economy/run_ledger.py` | Create | append/stats/explain/dual reader | @python-developer | 2 |
| 12 | `src/apiforge/application/context.py` | Modify | `build_context_capsule`, `expand_context_ref` app functions | @python-developer | 5 |
| 13 | `src/apiforge/cli_context.py` | Modify | `context capsule`, `context expand` | @python-developer | 12 |
| 14 | `src/apiforge/cli_economy.py` | Create | `economy stats`, `economy explain` register fn | @python-developer | 11 |
| 15 | `src/apiforge/cli.py` | Modify | Register `cli_economy`; `evals economy` command | @python-developer | 14, 17 |
| 16 | `src/apiforge/mcp/tools.py` (+ server registration) | Modify | `context_capsule`, `context_expand`, `economy_stats`, `economy_explain` | @python-developer | 12, 11 |
| 17 | `src/apiforge/evals/economy.py` | Create | Corpus loader, baseline, runner, gate | @api-verification-engineer | 5, 11 |
| 18 | `evals/corpus/economy/*.yaml` (12) + `README.md` | Create | Cases with `required_refs` ground truth | @api-test-strategist | fixtures |
| 19 | `evals/corpus/economy/baseline.json` | Create | Recorded baseline (Wave 0, before gateway gate) | @api-verification-engineer | 17, 18 |
| 20 | `docs/catalog-contract.md` | Modify | 6 new `AF-*` codes with field/unlock | @api-release-guardian | 3 |
| 21 | `tests/contracts/test_context_capsule.py` | Create | Contract validation + registry | @test-generator | 1–3 |
| 22 | `tests/context/test_gateway_canonical.py` | Create | AT-007, CRLF | @test-generator | 6 |
| 23 | `tests/context/test_gateway_refs.py` | Create | AT-002/003/004 | @test-generator | 7 |
| 24 | `tests/context/test_gateway_capsule.py` | Create | AT-001/005/006/008 | @test-generator | 10 |
| 25 | `tests/economy/test_run_ledger.py` | Create | AT-009/010/011, SC6 | @test-generator | 11 |
| 26 | `tests/evals/test_economy_eval.py` | Create | AT-012 gate logic | @test-generator | 17 |
| 27 | `tests/mcp/test_economy_context_tools.py` | Create | AT-013 CLI↔MCP parity | @test-generator | 13–16 |
| 28 | `docs/sdd/API_FORGE_ECONOMY_CONTEXT_GATEWAY/*.md` | Create | SDD chain intent→ship (house format) | @api-release-guardian | all |
| 29 | `.claude/skills/api-forge-context/SKILL.md` (+ host mirrors) | Modify | Route agents to `context capsule`/`expand` first | @api-agentic-orchestrator | 13, 16 |
| 30 | `README.md` | Modify | Document new verbs | (general) | 13–15 |

**Total Files:** 30 entries (≈41 physical files incl. 12 corpus YAML)

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @python-developer | 1–16 | Typed pydantic contracts, pure functions, typer/MCP wiring |
| @api-verification-engineer | 17, 19 | Independent evidence/recall verification, benchmark gate |
| @api-test-strategist | 18 | Ground-truth `required_refs` per fixture, negative space |
| @test-generator | 21–27 | pytest unit/integration per acceptance test |
| @api-release-guardian | 20, 28 | AF catalog + SDD evidence chain |
| @api-agentic-orchestrator | 29 | Host routing / skill mirrors |
| (general) | 30 | Docs only |

**Agent Discovery:** agentspec `agents/**` (python-developer, test-generator) + project `.claude/agents/api-*`; matched by path (`src/`, `tests/`), purpose keywords (verification, catalog, routing), KB domains (pydantic, testing).

---

## Code Patterns

### Pattern 1: New contracts (house `VersionedContract` style)

```python
# src/apiforge/contracts/context.py (append)
RefKind = Literal["contract", "schema", "code", "test", "policy", "knowledge"]
CapsuleLevel = Literal["L0", "L1", "L2", "L3", "L4"]
RefSource = Literal["graph", "contract", "code", "knowledge", "filesystem"]


class ContextRef(VersionedContract):
    """Content-addressed pointer to one piece of evidence."""

    uri: str = Field(pattern=r"^ctx://sha256/[0-9a-f]{64}$")
    kind: RefKind
    label: str = Field(min_length=1)
    source: str = Field(min_length=1)
    span: tuple[int, int] | None = None
    revision: str = "worktree"
    size_bytes: int = Field(ge=0)
    provenance: str = Field(min_length=1)  # rule id: "graph-edge:<id>" | "target" | "policy:<id>"
    origin: RefSource
    parity: bool | None = None
    delta: dict[str, tuple[str, ...]] = Field(default_factory=dict)


class CapsuleBudget(VersionedContract):
    context_bytes: int = Field(ge=256)
    max_level: CapsuleLevel = "L3"
    serialized_bytes: int = Field(default=0, ge=0)
    reached_level: CapsuleLevel = "L0"


class CapsuleRefusal(VersionedContract):
    code: str = Field(pattern=r"^AF-[A-Z0-9-]+$")
    field: str
    unlock: str
    detail: str = ""


class ContextCapsule(VersionedContract):
    """Minimal sufficient evidence for one intent, addressed by ctx:// refs."""

    schema: Literal["apiforge/context-capsule/v1"] = "apiforge/context-capsule/v1"  # type: ignore[assignment]
    capsule_id: str = Field(pattern=r"^ctx://sha256/[0-9a-f]{64}$")
    intent: dict[str, str]
    scope: ContextScope
    fingerprint: dict[str, object] = Field(default_factory=dict)
    impact: dict[str, int] = Field(default_factory=dict)  # {"direct": n, "transitive": m}
    refs: tuple[ContextRef, ...] = ()
    policies: tuple[str, ...] = ()
    expertise: tuple[str, ...] = ()
    budget: CapsuleBudget
    refusals: tuple[CapsuleRefusal, ...] = ()
    unresolved: tuple[str, ...] = ()
    status: Literal["ready", "degraded", "unresolved"] = "ready"

    @model_validator(mode="after")
    def refs_are_unique(self) -> ContextCapsule:
        uris = [ref.uri for ref in self.refs]
        if len(set(uris)) != len(uris):
            raise ValueError("capsule refs must be unique")
        return self
```

### Pattern 2: Canonical bytes and content store

```python
# src/apiforge/context/gateway/canonical.py
import hashlib
import json
from typing import Any


def dumps(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def normalize(text: str) -> str:
    return text.replace("\r\n", "\n")


def uri_for(content: str) -> str:
    return "ctx://sha256/" + hashlib.sha256(normalize(content).encode("utf-8")).hexdigest()


# src/apiforge/context/gateway/refs.py
from pathlib import Path

from apiforge.context.gateway.canonical import normalize, uri_for
from apiforge.contracts.base import ContractError

_PREFIX = "ctx://sha256/"


class CtxStore:
    def __init__(self, root: Path) -> None:
        self.dir = Path(root) / ".apiforge" / "ctx"

    def put(self, content: str) -> str:
        uri = uri_for(content)
        path = self.dir / uri.removeprefix(_PREFIX)
        if not path.exists():
            self.dir.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(normalize(content), encoding="utf-8", newline="\n")
            tmp.replace(path)
        return uri

    def get(self, uri: str) -> str:
        if not uri.startswith(_PREFIX) or len(uri) != len(_PREFIX) + 64:
            raise ContractError("AF-CTX-REF-INVALID", f"field=uri unlock=use ctx://sha256/<64 hex>: {uri}")
        path = self.dir / uri.removeprefix(_PREFIX)
        if not path.is_file():
            raise ContractError("AF-CTX-REF-NOT-FOUND", f"field=uri unlock=rebuild capsule: {uri}")
        content = path.read_text(encoding="utf-8")
        if uri_for(content) != uri:
            raise ContractError("AF-CTX-HASH-MISMATCH", f"field=uri unlock=delete object and rebuild: {uri}")
        return content
```

(Build aligns the `field`/`unlock` carriage with how `_run` currently projects `ContractError` — verify against an existing refusal test before finalizing.)

### Pattern 3: Budget-respecting inclusion (whole ref or none)

```python
def admit(refs, budget_bytes: int, base_bytes: int):
    admitted, used = [], base_bytes
    for ref in refs:  # already ordered by level, then (kind, label, source, span)
        cost = len(dumps(ref.model_dump(mode="json")))
        if used + cost > budget_bytes:
            return admitted, used, False  # exhausted → caller sets status="unresolved"
        admitted.append(ref)
        used += cost
    return admitted, used, True
```

### Pattern 4: Ledger entry (superset of legacy)

```python
# src/apiforge/economy/run_ledger.py
def append(root: Path, entry: RunLedgerEntry) -> None:
    line = {
        "verb": entry.verb,
        "detail_level": entry.detail_level,
        "payload_bytes": entry.cost.context_bytes + entry.cost.tool_result_bytes,
        **entry.model_dump(mode="json"),
    }
    try:
        path = ledger_path(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(line, sort_keys=True) + "\n")
    except OSError:
        return
```

### Pattern 5: Corpus case

```yaml
# evals/corpus/economy/fastapi-orders-post.yaml
id: economy-fastapi-orders-post
fixture: tests/fixtures/fastapi_orders
intent: {action: evolve, target: "POST:/orders", objective: add idempotency key}
level: L3
budget_bytes: 16000
required_refs:
  - {path: openapi.yaml, symbol: "components.schemas.OrderCreate"}
  - {path: app/main.py, symbol: create_order}
  - {path: tests/test_orders.py, symbol: test_create_order}
```

---

## Data Flow

```text
1. Caller: context capsule --target POST:/orders --budget-bytes 16000 --level L3
   │
   ▼
2. L0 intent → dict; L1 ContextService.resolve(scope=target) → fingerprint (framework, contracts, repo)
   │   (no graph in WorkspaceStatus → status=degraded, AF-CTX-GRAPH-UNAVAILABLE, stop at L1)
   ▼
3. L2 assess_graph_impact(nodes, edges, target_id, mode="transitive") → impacted_nodes
   ▼
4. L3 for each node (+ target contract op/schema): extract span → CtxStore.put → ContextRef
   │   dedup.py: schema canonical once; DTO/SDK refs → parity/delta
   │   admit() under budget; overflow → status=unresolved, AF-CONTEXT-BUDGET-EXHAUSTED
   ▼
5. L4 (if max_level=L4 and budget left): focused line spans for top-ranked code refs
   ▼
6. capsule_id = uri_for(canonical body); run_ledger.append(source per ref, CostVector)
   ▼
7. Emit ContextCapsule/v1 (CLI JSON / MCP dict) ; later: context expand ctx://… → verified content
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| Local filesystem (repo, `.apiforge/`) | Read source; write `ctx/` + ledger | N/A (local) |
| Host transcript JSONL (optional) | Read-only via existing `economy/tokens.read_transcript` | N/A |
| MCP hosts (Claude/Codex/Devin) | Existing MCP server, new tools | Existing host config |

No network, no provider SDK, no live mutation.

---

## Testing Strategy

Per-task: run only the targeted test file(s) listed. Full suite + `apiforge sdd check --root docs/sdd` **once** at the end of build.

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Contracts, canonical, store, dedup, admit, ledger | 21, 22, 23, 25 | pytest | 90% of new modules |
| Integration | Capsule on fixtures, CLI↔MCP parity | 24, 27 | pytest + typer CliRunner, `tmp_path` copies of fixtures | All ATs |
| Benchmark | Corpus 12 cases vs baseline | 26 + `apiforge evals economy` | pytest + CLI | SC1–SC3 |

| AT | Test |
|----|------|
| AT-001, 005, 006, 008 | `tests/context/test_gateway_capsule.py` |
| AT-002, 003, 004 | `tests/context/test_gateway_refs.py` |
| AT-007 | `tests/context/test_gateway_canonical.py` (incl. CRLF input) |
| AT-009, 010, 011 | `tests/economy/test_run_ledger.py` (+ snapshot of `report()` on legacy fixture) |
| AT-012 | `tests/evals/test_economy_eval.py` (gate logic on synthetic results) + real run at end |
| AT-013 | `tests/mcp/test_economy_context_tools.py` |
| SC7 | existing catalog test extended for 6 new codes |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| `AF-CONTEXT-BUDGET-EXHAUSTED` | Partial capsule, `status=unresolved`, `reached_level`, exit 0 | No (caller raises budget/lowers level) |
| `AF-CTX-GRAPH-UNAVAILABLE` | Degraded capsule L0/L1, exit 0 | No |
| `AF-CTX-REF-NOT-FOUND` | Refusal via `_run`, non-zero | No |
| `AF-CTX-HASH-MISMATCH` | Refusal, content never returned | No |
| `AF-CTX-REF-INVALID` | Refusal (malformed URI) | No |
| `AF-ECONOMY-RUN-NOT-FOUND` | `economy explain` unknown run_id refusal | No |
| Ledger write `OSError` | Swallowed (best-effort, as today) | No |
| Malformed ledger line | Skipped, counted in `stats.diagnostics.malformed_lines` | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `--budget-bytes` | int | `16000` | Capsule serialized byte ceiling |
| `--level` | str | `L3` | Max expansion level (L0–L4) |
| `--impact` | str | `transitive` | Graph mode passed to `assess_graph_impact` |
| `--record-baseline` (evals) | bool | `false` | Rewrite `baseline.json` explicitly |
| `--min-reduction` (evals) | float | `0.40` | SC3 threshold |

Defaults live as module constants in `context/gateway/capsule.py` and `evals/economy.py` (no new config file in P0).

---

## Security Considerations

- `expand` only reads inside `<root>/.apiforge/ctx/`; URI validated by regex → no path traversal.
- Hash verification before returning content; tampered objects refused.
- Capsule source extraction reads only files already inside the resolved scope root; symlinks resolved and rejected if outside root.
- No secrets added: ctx objects are copies of repo files already present; `.apiforge/` already gitignored (verify in build).

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | None new; results are JSON payloads |
| Metrics | `RunLedgerEntry` per emission: `CostVector{context_bytes, tool_result_bytes, expansions, cache_hits, duration_ms, observed_tokens|null}` + `source` |
| Tracing | `run_id` (uuid4 hex) shared by capsule + subsequent expands via `--run-id`; `economy explain <run_id>` |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-27 | design-agent | Initial version; resolves DEFINE Q1 (Decision 3) and Q2 (Decision 1) |
| 1.1 | 2026-09-27 | ship-agent | Shipped and archived |

---

## Next Step

**Ready for:** `/agentspec:workflow:ship .claude/sdd/features/DEFINE_API_FORGE_ECONOMY_CONTEXT_GATEWAY.md`
