---
sdd: 1
feature: API_FORGE_EVOLUTION1_GOVERNED_BUDGETS
phase: ship
profile: critical
status: ready
deviations:
  - host MCP major-version mismatch may keep full mypy unresolved
evidence:
  - path: sdd/API_FORGE_EVOLUTION1_GOVERNED_BUDGETS/evidence/G3.txt
    sha256: "f5432e70dfc8790b1c34d2327ae762c3e8c444dfedee652f36afd0d7a2c4ad5b"
upstream:
  path: benchmark.md
  sha256: "32035c50cf00730bdd536e6f658116d81a0152a44c226cc22c638354ca1cbbff"
---

# ship

Ship only after focused tests, release gate, Ruff, mypy focused sources and
SDD hash validation pass. The host MCP version mismatch, if present, remains
an unresolved environment gap rather than a false green.
