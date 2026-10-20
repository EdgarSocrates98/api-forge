---
sdd: 1
feature: API_FORGE_CYCLE12_PORTABLE_DIST
phase: architecture
profile: standard
status: done
upstream:
  path: contract.md
  sha256: "25c8315428b9e47b189cb942c8b6720fcf189501a57d390c1ec22d97580ce538"
files:
  - src/apiforge/evals/paths.py
  - src/apiforge/knowledge/selector.py
  - src/apiforge/cli.py
  - src/apiforge/mcp/tools.py
  - pyproject.toml
decisions:
  - force-include _data/* + host_assets/portal_assets in the wheel
  - importlib.resources + as_file/ExitStack for zipimport safety
  - dotdot/absolute paths refused, never remapped
---

# architecture

Design notes for wheel-portable resources.
