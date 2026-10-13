# ErrorSlice/v1

`ErrorSlice/v1` is `apiforge slice log`: failure signatures instead of a CI log.

| Field | Meaning |
|---|---|
| `signatures[]` | `{signature, first_line, count, spans, frames, context}`; the signature normalizes digits, hex, quoted strings and paths so repeats dedupe with a count |
| `frames` | Up to 6 following stack frames (Java `at ...`, Python `File "...", line N`, Go `file.go:N`, `goroutine N`) |
| `context` | Up to 3 non-empty preceding lines |
| `environment` | Runtime version lines found in the log (python, openjdk, go, node, platform) |
| `log_ref` | `ctx://sha256/<hex>` of the whole log |
| `original_bytes` / `original_lines` / `slice_bytes` | Sizes |
