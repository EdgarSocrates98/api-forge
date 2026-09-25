# ContextScope-v1

Context resolution is internal to API Forge; a separate `apiforge here`
command is intentionally deferred. The closed scopes are:

- `repo`: current repository/project context;
- `workspace`: declared virtual workspace context;
- `target`: one observed workspace target, selected by stable id, label or root.

`impact` is optional and accepts `direct`, `transitive` or `all`. The result
contains selected targets, included repositories, graph payload, measured
funnel, evidence, gaps and unresolved diagnostics. Presentation surfaces must
project this payload without changing evidence or status.
