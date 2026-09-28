# EvidenceNode/v1

`EvidenceNode/v1` is `apiforge evidence resolve evidence://{operation|fact|finding|rule}/<id>`.

| Field | Meaning |
|---|---|
| `ref` / `kind` / `node_id` | The resolved node |
| `props` | Node properties from the case graph |
| `neighbors` | One-hop neighbors as further `evidence://` refs — never the whole chain |
| `source_ref` | For facts with a source line: `ctx://` of a small slice of that file |
