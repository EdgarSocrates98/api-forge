# ToolSurfaceAudit/v1

§40 the audited MCP surface — findings over measured schema/description
bytes plus declared-shape hypotheses.

| Field | Meaning |
|---|---|
| `surface` | `full` or `compact` |
| `tool_count`/`total_bytes` | measured surface size |
| `findings` | `SurfaceFinding` rows sorted by kind/tool/detail |
| `accepted` | findings matched by a declared `accepted:` policy exception, detail carrying the reason — recorded, never silently dropped |
| `unresolved` | detectors without a basis (e.g. output sizes need a benchmark) |

Invariant: size/duplication claims are `observed`; shape suspicions are
`hypothesis` — never upgraded. A declared exception moves a finding to
`accepted`; it never erases it.
