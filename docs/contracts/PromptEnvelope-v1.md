# PromptEnvelope/v1

`PromptEnvelope/v1` is `apiforge agentops prompt --capability C [--task T] [--expertise P]`.

| Field | Meaning |
|---|---|
| `prefix` / `prefix_sha256` / `prefix_bytes` | Canonical JSON of the protocol digest, capability, output contract and expertise pack versions — identical across runs of the same capability |
| `suffix` / `suffix_bytes` | Run-specific part: capsule id, refs and task |

Runtime requests carry `prompt_prefix_sha256` so hosts can reuse provider prompt caches.
