---
sdd: 1
feature: API_FORGE_STEP11_CONTEXT_QUALITY
phase: secure
profile: critical
status: done
upstream:
  path: verify.md
  sha256: "95f59f431ff6227dbf0b36cc73e24b124de70a9bd421b4bee6037b56515cff32"
threat_model:
  - metrics compute only from recorded inputs; unresolved basis carries no
    value and the contract rejects it
  - denied kinds and origin floors apply after class kinds; yaml naming an
    unknown role or overlapping required/denied kinds refuses at load
  - policies are yaml.safe_load data validated by closed contracts, never code
  - the quality verb reads a caller-declared local capsule; failures carry
    AF-CONTEXT-QUALITY-CAPSULE with an unlock
---

# secure

The plane is read-only over recorded artifacts. It never expands context, never
executes tool calls and never asserts trust — `minimum_origin_rank` is a
deterministic ordering over declared provenance. Policy files remain data.
