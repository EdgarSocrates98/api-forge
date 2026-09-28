# DeltaSlice/v1

`DeltaSlice/v1` is the delta-first entry point: what changed, what it impacts and
which capsules to build.

| Field | Meaning |
|---|---|
| `source` | `git` (read-only `git diff --name-status`) or `explicit` (`--changed`) |
| `base` / `head` | Refs when `source` is `git`; `head` null means the worktree |
| `changed_files` | `{path, status}` rows, root-relative |
| `changed_nodes` | Graph fact nodes whose source file changed |
| `impacted_operations` / `capsule_targets` | Operations implemented by changed facts, touched by a contract subtree change (operation plus `$ref` closure), or whose cached selection depends on a changed file |
| `invalidated` | `CacheDecision/v1` rows when `--invalidate` dropped selections |
| `unresolved` | `unmapped:<path>`, `graph-unavailable`, `contract-diff-unavailable:<path>` |
| `status` | `unresolved` when anything but unmapped files is unresolved |
