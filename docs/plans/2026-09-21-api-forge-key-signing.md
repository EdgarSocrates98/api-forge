# Plan 18 — Ed25519 report signing

**Goal:** `report keygen` creates an Ed25519 keypair under a keys dir;
`report sign --key` adds `algorithm`, `signature_b64` and
`public_key_sha256` to the signature block; `report verify --pubkey`
cryptographically verifies and names `signature_crypto` on divergence.
Without `--key` the hash-bound behavior is unchanged. A valid signature
proves the report was signed by whoever holds the key — never identity.
`cryptography` is confined to `apiforge/report/`.

- [ ] T1: pin cryptography; `report/keys.py` — keygen, sign over canonical(body)+hashes, verify
- [ ] T2: CLI `--key`/`--pubkey`/`keygen` + tests + docs/gate parity (AF-KEY-*)
