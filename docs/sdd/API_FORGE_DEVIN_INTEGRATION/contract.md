---
sdd: 1
feature: API_FORGE_DEVIN_INTEGRATION
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "021d3342790520940968e8bf5b091ccfcb4636a551f907ef022c8f8a39f050fa"
covers: [DevinPayload/v1, DevinLaunch/v1, DevinCheck/v1, DevinCliProbe/v1]
api_ir:
  input: objective, surface, task kind and safety options
  output: prompt, launch metadata, checks, evidence limits and prohibitions
---
# contract

Contracts are frozen, closed and evidence-aware. Generation never executes a
check or proves account, Desktop, Cloud or organization state.
