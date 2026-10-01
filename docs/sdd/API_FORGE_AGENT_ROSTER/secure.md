---
sdd: 1
feature: API_FORGE_AGENT_ROSTER
phase: secure
profile: critical
status: draft
upstream:
  path: verify.md
  sha256: "a53b4dc907da97e57bfedf3ef76b4ab4781c8c6ffd3a5838d1852a0c4f9b26bf"
threat_model: docs/security/threat-model-mvp.md
---
# secure

Least privilege is declared per agent and projected per host: read-only agents get no Edit/Write on Claude and a read-only Codex sandbox; state-writers write only through `apiforge` commands; writers declare `write_scope`. Limitation: Claude `Bash` is not narrowed per command and Devin enforces only the body text. The renderer never deletes non-agent files.
