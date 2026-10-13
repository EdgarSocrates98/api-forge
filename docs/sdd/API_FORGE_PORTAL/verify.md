---
sdd: 1
feature: API_FORGE_PORTAL
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "bc4e94ce01feb82b6908fc59727c05d8e1f7494fab104ad34608624b4cd16219"
results:
  - gate: tests/test_portal_adapter.py
    outcome: "20 passed (bootstrap, health, hosts, mcp, skills, agents, install lifecycle, tasks, analyze E2E, docs)"
  - gate: tests/test_command_rationale.py
    outcome: "4 passed — rationale do verbo portal resolvido"
  - gate: ruff nos arquivos novos
    outcome: "clean"
  - gate: E2E manual HTTP real (workspace scratch)
    outcome: "BOOT 200 / HEALTH NOT_INSTALLED / HOSTS 4 / SKILLS 14 / AGENTS 26 / DOCS hits / GRAPHS no_graph / intent ambígua 400 AF-PORTAL-AMBIGUOUS"
  - gate: regen_docs
    outcome: "commands.generated.json com portal; 0 undocumented_commands"
evidence_ref:
  - tests/test_portal_adapter.py
---

# verify

Gates de teste, lint, docs-drift e um E2E HTTP real contra o servidor
stdlib — todos verdes no HEAD.
