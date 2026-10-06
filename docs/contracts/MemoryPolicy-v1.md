# MemoryPolicy/v1

`MemoryPolicy/v1` is the fail-closed persistence policy for memory. It bounds
allowed scopes, minimum trust, evidence requirements, model-generated and
external-untrusted promotion, and result count. Refusals expose an `AF-*` code,
field and safe unlock.

Canonical schema: `apiforge contract show MemoryPolicy/v1`.
