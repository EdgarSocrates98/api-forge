# ContextRef/v1

`ContextRef/v1` points to one evidence object in `<root>/.apiforge/ctx`.

| Field | Meaning |
|---|---|
| `uri` | `ctx://sha256/<64 hex>` of the LF-normalized content — the identity |
| `kind` | `contract`, `schema`, `code`, `test`, `policy` or `knowledge` |
| `label` | Readable handle, e.g. `schema:PaymentRequest`, `handler:create_payment` |
| `source` | Root-relative POSIX path of the source file |
| `span` | Inclusive `[start, end]` lines when the object is a slice |
| `revision` | `worktree` in P0 |
| `size_bytes` | UTF-8 size of the stored object |
| `provenance` | Selection rule: `target`, `schema-ref:<name>`, `schema-model:<name>`, `graph-edge:<kind>:<id>`, `fact-match:code.route:<id>`, `symbol-match:<name>` |
| `origin` | Attribution source: `graph`, `contract`, `code`, `knowledge` or `filesystem` |
| `level` | `L3` pointer, or `L4` when `excerpt` is inlined |
| `parity` / `delta` | For code models mirroring a schema: `parity: true`, or `delta` with `missing`/`extra` field names |
| `excerpt` | L4 only — inline focused code |

`apiforge context expand <uri>` re-hashes the object before returning it and
refuses with `AF-CTX-HASH-MISMATCH` on tampering.
