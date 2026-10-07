# TestSlice/v1

`TestSlice/v1` is `apiforge slice tests`: what a test run said, without the
log that said it.

| Field | Meaning |
|---|---|
| `format` | `pytest` (text output) or `junit` (XML; a DOCTYPE is refused) |
| `passed` / `failed` / `errors` / `skipped` | Counts from the final summary line or the JUnit test cases |
| `failures[]` | Every failing or erroring test — never budget-trimmed: `{test, outcome, file, line, assertion, signature, span}` |
| `log_ref` | `ctx://sha256/<hex>` of the whole log; `apiforge context expand` re-verifies it |
| `original_bytes` / `slice_bytes` | Log size versus this slice |
| `unresolved` | e.g. failures without a short test summary (`pytest -rfE` fixes it) |
