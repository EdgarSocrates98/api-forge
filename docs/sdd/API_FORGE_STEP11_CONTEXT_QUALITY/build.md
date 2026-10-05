---
sdd: 1
feature: API_FORGE_STEP11_CONTEXT_QUALITY
phase: build
profile: critical
status: done
upstream:
  path: plan.md
  sha256: "755ef4c8fdd6614e82c3fc681e33623fb06527aa4c0e0e6a4cbf3c3310b3a4e2"
tasks:
  - contracts
  - engine
  - sufficiency
  - role-v2
  - evals-cli
claims:
  - 13 metric kinds emitted on every report; unresolved basis carries no value
  - strict gate keeps evidence-kind refs even when unused; permissive does not
  - required_kinds violations fire only on present-but-undelivered kinds
  - v1 role_context.yaml files load unchanged; v2 adds the policies block
---

# build

Implemented as planned. Notes:

- `RoleContextQuality` registered alongside the report row contracts.
- `uses_from_ledger` maps `context *` verbs to `loaded`, `runtime role:*` to
  `assigned`, `context expand` to `expanded`; `cited`/`artifact` remain
  caller-supplied and stay unresolved when absent.
- The yaml loader validates `policies:` rows through the contract and refuses
  unknown role names (`AF-ROLE-CONTEXT-POLICY`).
