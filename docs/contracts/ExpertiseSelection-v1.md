# ExpertiseSelection/v1

`ExpertiseSelection/v1` is the lazy-expertise answer (`knowledge select`): the
packs a declared trigger names, and nothing else.

| Field | Meaning |
|---|---|
| `intent` / `capability` / `frameworks` | Inputs matched against `rules/expertise_triggers.yaml` |
| `selected` | `{pack_id, pack_version, reasons, bytes}` rows; `reasons` are `keyword:<trigger>:<match>`, `framework:<name>` or `capability:<name>` |
| `loaded_bytes` / `catalog_bytes` / `catalog_packs` | Bytes of the selected packs versus the whole local catalog |
| `unresolved` | `no-expertise-trigger` when nothing matched — the selector never loads the whole catalog |
