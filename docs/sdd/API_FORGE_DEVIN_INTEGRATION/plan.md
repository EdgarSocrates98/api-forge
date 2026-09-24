---
sdd: 1
feature: API_FORGE_DEVIN_INTEGRATION
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "c53a591c0ae7dc949896a5eb72d236f0f8b13d04dcf0686e6bcef30750bf5a2f"
tasks:
  - id: payload-contract
    covers: [DevinPayload/v1, DevinLaunch/v1, DevinCheck/v1, desktop-cli-cloud-payloads]
    test: sdd/API_FORGE_DEVIN_INTEGRATION/evidence/devin-tests.txt
    risk: low
    rollback: remove Devin payload contracts
  - id: runtime-observation
    covers: [DevinCliProbe/v1, declared-observed-boundary, local-cli-observation]
    test: sdd/API_FORGE_DEVIN_INTEGRATION/evidence/devin-tests.txt
    risk: low
    rollback: remove local CLI probe
  - id: native-guardrails
    covers: [devin-config, devin-hook, devin-skill, devin-reviewer, devin-guardrails, docs]
    test: sdd/API_FORGE_DEVIN_INTEGRATION/evidence/devin-tests.txt
    risk: medium
    rollback: remove .devin integration assets
---
# plan

Implement contract, CLI projection, local probe, native Devin assets and docs.
