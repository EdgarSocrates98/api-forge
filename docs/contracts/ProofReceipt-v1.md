# ProofReceipt/v1

`ProofReceipt/v1` is a proof a deterministic task step produced, carried in the
step's `proofs` list. The economy ladder stops at L0 only when every
`expected_proofs` entry equals the `kind` or `proof_id` of a receipt whose
artifact lies inside the allowed roots and re-hashes to `sha256`. A textual
mention of a proof is at most L1 (`AF-ECONOMY-PROOF-UNSTRUCTURED`).

| Field | Meaning |
|---|---|
| `proof_id` | Stable identity of the proof |
| `kind` | Proof kind matched against `TaskSpec.expected_proofs` |
| `sha256` | Digest of the artifact bytes |
| `artifact_ref` | Path of the artifact, resolved inside the project or declared workspace roots |
