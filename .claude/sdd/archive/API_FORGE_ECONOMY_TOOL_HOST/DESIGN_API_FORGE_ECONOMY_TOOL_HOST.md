# DESIGN: API Forge Economy — Tool/Host Economy (Onda 5)

> Output modes, a gateway MCP surface, test/log slicers and host projections — all projections of the unchanged core, each measured against its full form.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_TOOL_HOST |
| **Date** | 2026-09-28 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_FORGE_ECONOMY_TOOL_HOST.md](./DEFINE_API_FORGE_ECONOMY_TOOL_HOST.md) |
| **Status** | ✅ Shipped |

---

## Architecture Overview

```text
                     ┌──────────── core verbs (unchanged) ────────────┐
CLI  ─ apiforge [--output json|compact] <verb>   → _echo_json → output.render(value, mode)
                                                    json: indent=2 (default, unchanged)
                                                    compact: prune(null/empty) + minified
MCP  ─ apiforge-mcp [--surface full|compact] [--host H]
         full:    86 tools (unchanged)
         compact: apiforge_discover(query)  → ranked full tools (name, summary)
                  apiforge_call(tool, args) → full tool by name (100% reachable)
                  apiforge_context(target|delta) · apiforge_expand(uri)
                  apiforge_analyze(contract, project) · apiforge_evidence(run_id)
mcp surface      → ToolSurface/v1 (name/description/schema bytes per tool; schema from signature)
slice tests      → TestSlice/v1  (pytest text | JUnit XML, DOCTYPE refused)   ┐ full log → ctx CAS
slice log        → ErrorSlice/v1 (signatures, frames, context, environment)   ┘ spans + ctx:// ref
agentops projection --host H → HostProjection/v1 (rules/host_projections.yaml + measured surface)
```

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `output/render.py` | `prune()`, `render(value, mode)`, mode resolution (flag > env > json) | json |
| `cli.py` | root `--output`, `_echo_json` uses renderer, ledger records emitted bytes | typer |
| `agentops/slicing.py` | pytest/JUnit/log parsers, signature normalization, CAS storage | re, xml.etree (DOCTYPE refused) |
| `mcp/gateway.py` | 6 gateway tools + `GATEWAY_TOOLS` | functions over `tools.py` |
| `mcp/surface.py` | per-tool bytes; schema via `pydantic.create_model` from signatures | pydantic |
| `mcp/server.py`, `mcp/main.py` | `--surface`, `--host`, `APIFORGE_MCP_SURFACE` | argparse |
| `rules/host_projections.yaml`, `agentops/projection.py` | host table + verb map | YAML |
| `contracts/tool_host.py` | TestSlice, TestFailure, ErrorSlice, ErrorSignature, ToolSurface, ToolCost, HostProjection | pydantic |
| `evals/tool_economy.py` + corpus | gates | fixtures |

---

## Key Decisions

### Decision 1: Compact = prune + minify, never truncate

Pruning removes `None`, `""`, `[]`, `{}` recursively; numbers/booleans (incl. `0`/`false`) stay. Lossless by rule: `json.loads(compact) == prune(json)`.

### Decision 2: Gateways dispatch, they don't reimplement

`apiforge_call` looks up the full tool by name in `TOOLS + OBSERVABILITY + GRPC + MIGRATION` and calls it with keyword args; unknown name → `AF-MCP-TOOL-UNKNOWN`, bad args → `AF-MCP-TOOL-ARGS`. `apiforge_discover` ranks tools by token overlap between the query and `name + docstring` (deterministic, ties by name).

### Decision 3: Schema bytes without the MCP SDK

`typing.get_type_hints(fn)` + `pydantic.create_model` → `model_json_schema()`; same information FastMCP derives. Reported as `schema_bytes` with `schema_source: "signature"`.

### Decision 4: Slicers keep every failure

Budgets apply only to context lines; every failing test and every distinct signature is always emitted. Signatures normalize digits, hex, quoted strings and absolute paths so repeats dedupe with counts.

### Decision 5: Host projection is declared data

Per host: `mcp_surface`, `output`, `deferred_tools`, `instruction_file`; `verb_map` shared. `apiforge-mcp --host` only selects the surface; core behavior never branches on host.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/tool_host.py` + registry | Create/Modify | Contracts | @python-developer | — |
| 2 | `src/apiforge/output/{__init__,render}.py`, `cli.py` | Create/Modify | Output modes | @python-developer | — |
| 3 | `src/apiforge/agentops/slicing.py`, `cli_tool_host.py` | Create | Slicers + CLI | @python-developer | 1 |
| 4 | `src/apiforge/mcp/{gateway,surface}.py`, `server.py`, `main.py` | Create/Modify | Compact MCP | @python-developer | 1 |
| 5 | `src/apiforge/rules/host_projections.yaml`, `agentops/projection.py` | Create | Host projections | @python-developer | 4 |
| 6 | `src/apiforge/evals/tool_economy.py`, `evals/corpus/tool-economy/*` | Create | Eval | @test-generator | 2–5 |
| 7 | tests | Create | Unit/parity | @test-generator | all |
| 8 | docs/contracts, catalog, README, skills, SDD chain | Create/Modify | Docs | @code-documenter | all |

---

## Agent Assignment Rationale

Executed inline.

---

## Code Patterns

```python
def prune(value):
    if isinstance(value, dict):
        kept = {k: prune(v) for k, v in value.items()}
        return {k: v for k, v in kept.items() if v not in (None, "", [], {})}
    if isinstance(value, list):
        return [prune(v) for v in value]
    return value
```

---

## Data Flow

CLI: verb → payload → `apply_detail_level` → `render(mode)` → stdout; ledger `payload_bytes` = emitted bytes.
MCP compact: host → gateway → full tool → payload → `prune` (gateway results are compact by definition).
Slicers: file → parse → `TestSlice`/`ErrorSlice` with `ctx://` of the whole file.

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| MCP hosts | stdio FastMCP (optional extra) | none |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | prune/render, slicers, discover/call, surface, projection | `tests/agentops/test_tool_host.py` | pytest | AT-001–011 |
| Parity | CLI json vs compact; gateway call vs full tool | same + `tests/mcp/test_gateway.py` | CliRunner | — |
| Eval | corpus gates | `evals tool-economy` | CLI | DEFINE success criteria |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Unknown output mode | `AF-OUTPUT-MODE-INVALID` | No |
| JUnit with DOCTYPE / invalid XML | `AF-SLICE-XML-REFUSED` / `AF-SLICE-INPUT-INVALID` | No |
| Missing input file | `AF-SLICE-INPUT-NOT-FOUND` | No |
| Unknown tool / bad args | `AF-MCP-TOOL-UNKNOWN` / `AF-MCP-TOOL-ARGS` | No |
| Unknown surface / host | `AF-MCP-SURFACE-INVALID` / `AF-HOST-UNKNOWN` | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `--output` / `APIFORGE_OUTPUT` | enum | `json` | CLI projection |
| `--surface` / `APIFORGE_MCP_SURFACE` | enum | `full` | MCP surface |
| `--host` / `APIFORGE_HOST` | enum | none | Host projection for MCP |

---

## Security Considerations

- JUnit parsing refuses DOCTYPE (no entity expansion); input size capped (25 MB).
- `apiforge_call` dispatches only to registered tools; no dynamic import.

---

## Observability

- Emitted bytes per call in `economy.jsonl`; `mcp surface` totals; slice `original_bytes`/`slice_bytes`.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-28 | design-agent | Initial version |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_API_FORGE_ECONOMY_TOOL_HOST.md`
