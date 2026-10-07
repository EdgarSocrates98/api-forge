# BRAINSTORM: API Forge Economy — Tool/Host Economy (Onda 5)

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_TOOL_HOST |
| **Date** | 2026-09-28 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |

---

## Initial Idea

**Raw Input:** `prompt_evo_economy.md` Wave 5 — compact tool surface measured, not assumed (§39, §91), verb-first (§40–41), compact results `--output compact` (§42), native RTK-like test/log slicing (§43–44), compact MCP gateways over full capability (§88–89), capability discovery on demand (§90), host-aware projections with a host-independent core (§92–93).

**Context Gathered:**
- `mcp/tools.py`: 86 tools registered in one FastMCP server (`TOOLS + OBSERVABILITY + GRPC + MIGRATION`); `mcp` extra is optional and not installed in the dev venv.
- `cli.py::_echo_json`: every command prints `json.dumps(indent=2)`; `detail_level` already prunes by level; bytes recorded in `economy.jsonl`.
- `agentops/compact.py`: RTK-style line compaction keeping critical lines (`context compact`); `agentops/filters.py`: closed per-command noise filters.
- `agentops/hosts.py`: 4 hosts (claude, gpt-codex, devin, copilot) with instruction file / skills / subagents / MCP support flags.
- No test-result or error slicer; no measurement of tool-surface bytes; no host projection.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/output/`, `mcp/surface.py`, `mcp/gateway.py`, `agentops/slicing.py`, `rules/host_projections.yaml` | Additive; core semantics unchanged |
| Relevant KB Domains | python, testing | Deterministic parsing |
| IaC Patterns | N/A | Offline |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | What is "compact output" without losing evidence? | Canonical minified JSON with null/empty values pruned; everything non-empty is kept (no truncation) | `--output compact` global option or `APIFORGE_OUTPUT=compact`; lossless by rule |
| 2 | How do we avoid hiding capability in a compact MCP? | 6 gateways incl. `apiforge_discover` (keyword ranking over the full catalog) and `apiforge_call` (dispatch to any full tool by name) | 86 capabilities reachable through 6 tools (§89) |
| 3 | How do we measure tool cost (§91)? | `mcp surface --surface full|compact`: name, description and JSON-schema bytes per tool, derived from signatures without the `mcp` extra | Numbers, not assumptions |
| 4 | Host awareness? | `rules/host_projections.yaml`: per host MCP surface, output mode, deferred tool loading, verb map; `apiforge-mcp --surface/--host` | Core untouched (§92) |
| 5 | Slicing inputs? | pytest text, JUnit XML (DOCTYPE refused), generic CI logs (Python/Java/Go traces) → `TestSlice/v1` / `ErrorSlice/v1` with full log stored in the ctx CAS | Agent receives failures + refs, expands on demand |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `evals/corpus/tool-economy/logs/*` (to create) | ~5 | pytest failure, JUnit XML, Java stack trace, Go panic, noisy CI build |
| Output examples | live command payloads on `economy_payments` | ~6 | capsule, stats, cache, knowledge select, audit, delta |
| Ground truth | corpus yaml expectations | ~10 | failing tests, signatures, discover queries |
| Related code | `agentops/compact.py`, `mcp/tools.py`, `cli.py` | — | Reuse |

---

## Approaches Explored

### Approach A: Projection layer (output modes, gateway MCP, slicers, host table) ⭐ Recommended

**Description:** Add projections around the existing core: an output renderer used by `_echo_json`, a compact MCP built from the same tool functions, slicers that store the full log in the CAS, and a host projection table.
**Pros:** Core semantics unchanged; every projection measurable against the full form.
**Cons:** Compact MCP dispatch loses per-tool typed schemas (by design).

### Approach B: Trim the full MCP registration per profile

**Cons:** Hides capability (§89); host deferred loading may already neutralize the gain (§39).

### Approach C: LLM summaries of logs

**Cons:** §9 — pays tokens to save tokens.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-09-28 — pre-approved autonomous delivery |
| **Reasoning** | Measurable, lossless, reversible |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Compact output prunes only null/empty | Lossless by construction | Truncating lists |
| 2 | Full MCP stays default | Compact is an opt-in projection | Replacing the full surface |
| 3 | Slicers never drop a failing test or first error line | Critical evidence floor | Budget-based truncation of failures |
| 4 | Full logs kept in the ctx CAS | `context expand` works unchanged | New `log://` store |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| YAML output mode | JSON-minified is lossless and parseable | Yes |
| Live per-host behavior probing | No host SDK in core; projection is declared | Yes |
| Test selection by impact / V0–V5 ladder | Extras wave | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Output modes + gateway MCP | ✅ | Autonomous mandate | No |
| Slicers + host projections | ✅ | Autonomous mandate | Yes — DOCTYPE refusal for JUnit |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
Hosts receive pretty-printed payloads, a single 86-tool MCP surface whose cost is never measured, and raw test/CI logs; nothing adapts the projection to the host.

### Success Criteria (Draft)
- [ ] Compact output ≤ 65% of JSON bytes on sampled payloads, lossless by rule.
- [ ] Compact MCP surface ≤ 25% of full bytes with 100% of full tools reachable.
- [ ] Slicers recall 1.0 on failing tests/signatures, ≤ 20% of log bytes.

### Out of Scope (Confirmed)
- Test selection, verification ladder, YAML output, live host probing.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 5 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 3 |
| Validations Completed | 2 |
| Duration | ~10 min |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_TOOL_HOST.md`
