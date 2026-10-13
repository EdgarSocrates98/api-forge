# CacheEntry/v1

`CacheEntry/v1` is the freshness metadata of one cached payload. Entries live at
`<tier>/entries/<layer>/<key>.json`; payloads at `<tier>/objects/<sha256>`.

| Field | Meaning |
|---|---|
| `layer` | `parse`, `graph`, `impact`, `capsule`, `knowledge`, `routing`, `validation` or `model_response` (policy in `rules/cache_policies.yaml`) |
| `key` | 64-hex request key; root-independent so the shared tier can serve another root |
| `subject` | Human handle, e.g. the capsule target `POST /payments` |
| `object_uri` | `ctx://sha256/<hex>` of the payload; re-hashed on every read |
| `inputs_sha` / `policy_sha` / `expertise_sha` | Digests of the inputs, cache policy file and expertise packs (null until packs are cached) |
| `created_at` / `expires_at` | UTC timestamps; `expires_at` = created + layer TTL |
| `deps_files` | `CacheDep/v1` rows (file, span or pointer hashes) |
| `deps_nodes` / `neighborhood_sha` | Graph node ids and the hash of their node hashes plus every touching edge (except `described_by`) |
| `symbols` | `model:<Name>[@path:start-end]` definitions and `test:<handler>` mentions scanned in changed sources |
| `manifest_uri` | Object holding the project source manifest at build time |
