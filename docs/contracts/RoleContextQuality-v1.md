# RoleContextQuality/v1

Per-role rollup inside a `ContextQualityReport`.

| Field | Meaning |
|---|---|
| `role` | Role name (`_` for un-attributed uses) |
| `refs_assigned` / `refs_used` | Refs delivered vs refs consumed |
| `bytes_assigned` / `bytes_used` | Same in bytes |
| `efficiency` | `refs_used / refs_assigned`; `null` when neither was recorded |
