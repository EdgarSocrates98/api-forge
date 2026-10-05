# ToolAuthorization/v1

The recorded decision for one `(subject, tool)` pair under the §13
allowlist-first model.

| Field | Meaning |
|---|---|
| `subject` / `tool` | The evaluated pair |
| `decision` | `allow` or `deny` |
| `risk_classes` | The tool's declared risk profile at decision time |
| `code` / `field` / `unlock` | `AF-TOOL-*` refusal triad; `None` when allowed |
| `reason` | Human-readable justification |

Denials are first-class output, never silent exceptions — every `deny` carries
a cataloged code so the caller can project a safe unlock.
