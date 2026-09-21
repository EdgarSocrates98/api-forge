# Plan 13 — GraphQL + protobuf/gRPC adapters

**Goal:** `model graphql --path schema.graphql` (graphql-core, confined to
`adapters/graphql_`) and `model proto --path dir/` (pure-python .proto
reader — no protoc). Facts `graphql.type`/`graphql.field`,
`proto.file`/`proto.service`/`proto.rpc`/`proto.message`; malformed input →
named diagnostics, never exceptions.

- [ ] T1: pin graphql-core; `adapters/graphql_` — type/operation-field facts, `AF-GQL-INVALID`
- [ ] T2: `adapters/protobuf` — comment-stripped mini-parser, brace tracking, streaming flags, `AF-PROTO-PARSE`
- [ ] T3: CLI + tests + docs/gate parity (AF-GQL/AF-PROTO); graphql-core boundary check
