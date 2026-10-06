# MemoryOutcome/v1

`MemoryOutcome/v1` is the auditable result of a memory persistence or
invalidation operation. It distinguishes accepted, rejected, invalidated and
deduplicated actions; rejected operations carry the refused field and a safe
unlock rather than silently changing state.

Canonical schema: `apiforge contract show MemoryOutcome/v1`.
