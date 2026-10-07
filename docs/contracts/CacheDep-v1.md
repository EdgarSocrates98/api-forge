# CacheDep/v1

`CacheDep/v1` names one source a cache entry was computed from.

| Field | Meaning |
|---|---|
| `path` | Root-relative POSIX path; roots never leak into shared entries |
| `sha256` | Hash recorded at build time; `null` when the source was missing |
| `span` | Inclusive `[start, end]` lines: only that slice is hashed (handlers, models) |
| `pointers` | JSON pointers into a YAML/JSON document (e.g. `/paths/~1payments/post`, `/components/schemas/Money`); only those subtrees are hashed |

Whole-file hashing applies when neither `span` nor `pointers` is set. A probe
that returns a different hash invalidates the entry regardless of TTL.
