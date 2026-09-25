# ProjectManifest-v1

The optional `.apiforge/project.yaml` file connects one repository to API
Forge. It is not a copy of the Forge and must not contain knowledge, prompts,
tokens, credentials or provider payloads.

```yaml
schema: apiforge/project/v1
project_id: project:stable-id
root: C:/work/service
default_scope: repo
target: null
hosts: []
evidence_refs: []
```

Unknown keys and secret-like keys are refused. The loader normalizes `root`
and reports malformed input as `AF-MANIFEST-INVALID`.
