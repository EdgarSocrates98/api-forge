# DEFINE: API Forge Economy — Tool/Host Economy (Onda 5)

> Compact, lossless projections of what API Forge already produces — outputs, MCP surface, test and CI logs — chosen per host without changing the core.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_TOOL_HOST |
| **Date** | 2026-09-28 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 14/15 |
| **Source** | `.claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_TOOL_HOST.md` |

---

## Problem Statement

Every CLI payload is pretty-printed, the MCP server exposes one 86-tool surface whose cost has never been measured, test and CI logs reach agents raw, and no projection adapts to the host (Claude, Codex, Devin, Copilot). Hosts pay transport cost that deterministic projections could remove without losing evidence.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Agent host | Calls CLI/MCP | Pretty JSON, huge tool list, raw logs |
| CI / maintainer | Reads failures | 10k-line logs for one failing assertion |
| Integrator | Configures hosts | No declared, measured projection per host |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | G1: `--output compact|json` (root option + `APIFORGE_OUTPUT`): compact = minified canonical JSON with null/empty pruned; lossless by rule; bytes of both recorded (§42) |
| **MUST** | G2: `apiforge slice tests --input F [--format pytest|junit|auto]` → `TestSlice/v1` (counts, every failure with test/file/line/assertion/signature, full log `ctx://`); JUnit DOCTYPE refused (§43) |
| **MUST** | G3: `apiforge slice log --input F` → `ErrorSlice/v1`: deduped failure signatures, relevant frames, preceding context, environment lines, spans + `ctx://` of the full log (§44) |
| **MUST** | G4: Compact MCP surface: `apiforge_discover`, `apiforge_call`, `apiforge_context`, `apiforge_expand`, `apiforge_analyze`, `apiforge_evidence`; every full tool reachable via `apiforge_call`; `apiforge-mcp --surface compact|full` (§88–90) |
| **MUST** | G5: `apiforge mcp surface [--surface]` → `ToolSurface/v1`: per tool name/description/schema bytes and totals (§91) |
| **SHOULD** | G6: `rules/host_projections.yaml` + `apiforge agentops projection --host H` → `HostProjection/v1` (surface, output, deferred tools, verb map, measured bytes); `apiforge-mcp --host H` (§92–93) |
| **SHOULD** | G7: Verb-first map (artifact question → verb) in the projection and the context skill (§40–41) |
| **SHOULD** | G8: `evals tool-economy` with gates |

---

## Success Criteria

- [ ] Compact output ≤ 65% of `--output json` bytes (aggregate) on ≥ 6 real payloads (revised from 60% after measurement: lossless pruning+minify yields ~37%, content-dominated capsules ~25%); `json.loads(compact) == prune(json)` for all.
- [ ] Compact MCP surface bytes ≤ 25% of full; `apiforge_call` reaches 100% of full tools; discover top-5 contains the expected tool for every corpus query.
- [ ] Slicers: failing-test and signature recall 1.0 on the corpus; slice ≤ 20% of log bytes on logs ≥ 4 KB.
- [ ] Output of existing commands unchanged in the default `json` mode.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Compact output | any command | `--output compact` | minified, no null/empty, parseable, same non-empty leaves |
| AT-002 | Env default | `APIFORGE_OUTPUT=compact` | command without flag | compact |
| AT-003 | Pytest slice | failing pytest log | `slice tests` | counts + each failure's test, assertion, file:line |
| AT-004 | JUnit slice | JUnit XML | `slice tests --format junit` | same shape; DOCTYPE → `AF-SLICE-XML-REFUSED` |
| AT-005 | Log slice | CI log with Java/Python/Go errors | `slice log` | signatures deduped with counts, frames, context, spans |
| AT-006 | Expand | slice ref | `context expand <uri>` | full log verified |
| AT-007 | Discover | "grpc breaking" | `apiforge_discover` | grpc compatibility tools in top 5 |
| AT-008 | Call | `apiforge_call("rules_list", {})` | compact MCP | same result as full tool |
| AT-009 | Unknown tool | `apiforge_call("nope")` | — | `AF-MCP-TOOL-UNKNOWN` with unlock |
| AT-010 | Surface | `mcp surface --surface compact` | — | bytes per tool and totals |
| AT-011 | Host projection | `--host claude` | projection | surface compact, output compact, deferred tools true |

---

## Out of Scope

- Test selection by impact and the V0–V5 verification ladder (extras wave).
- YAML output; live host probing.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | `mcp` extra optional; surface measured without it | Schemas from signatures via pydantic |
| Technical | No provider SDK, offline | Declared host table |
| Technical | AF codes cataloged | `AF-SLICE-*`, `AF-MCP-TOOL-UNKNOWN`, `AF-OUTPUT-*`, `AF-HOST-*` |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/output/`, `agentops/slicing.py`, `agentops/projection.py`, `mcp/{gateway,surface}.py`, `rules/host_projections.yaml` | Additive |
| **KB Domains** | python, testing | — |
| **IaC Impact** | None | — |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | All CLI JSON goes through `_echo_json` | Some commands skip compact | [ ] spot-check in build |
| A-002 | Tool signatures resolvable with `typing.get_type_hints` | Schema bytes incomplete | [ ] build |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Concrete |
| Users | 3 | Host, CI, integrator |
| Goals | 3 | Section-mapped |
| Success | 3 | Numeric |
| Scope | 2 | Host behavior declared, not probed |
| **Total** | **14/15** | |

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | define-agent | Initial version |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_API_FORGE_ECONOMY_TOOL_HOST.md`
