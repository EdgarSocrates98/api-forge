# WorkspaceManifest-v1

[Português (Brasil)](WorkspaceManifest-v1.pt-BR.md) · [Portable distribution guide](../guides/API_FORGE_PORTABLE_DISTRIBUTION.md)

`.apiforge/workspace.yaml` registers independent repositories under a virtual
workspace. It does not change Git metadata or require a monorepo.

```yaml
schema: apiforge/workspace/v1
workspace_id: workspace:platform
name: platform
root: C:/work/platform
repositories:
  - repository_id: repository:orders
    name: orders
    root: ../orders
    repository_type: service
    evidence_level: observed
relations: []
evidence_refs: []
```

Repository membership and explicit relations are `declared`. Missing roots are
retained as unresolved with `AF-WORKSPACE-REPO-MISSING`; names and directory
layout never promote a heuristic relationship to a confirmed fact.
