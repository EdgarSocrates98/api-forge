# MemoryTrust/v1

`MemoryTrust/v1` is the trust metadata attached to a memory record. It keeps
trust level, taint, evidence references and a human-readable reason separate
from the memory payload. `instruction_authority` is closed to `none` so trust
metadata cannot turn stored data into an instruction channel.

Canonical schema: `apiforge contract show MemoryTrust/v1`.
