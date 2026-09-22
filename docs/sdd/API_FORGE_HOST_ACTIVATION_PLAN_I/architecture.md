---
sdd: 1
feature: API_FORGE_HOST_ACTIVATION_PLAN_I
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "680f9787a3bb6cce4bbde9dc9fb7dd7f77fb7920ea429a57c64db0879ea47f84"
files: [src/apiforge/agentops/activation.py, src/apiforge/cli.py]
decisions:
  - id: no-silent-mutation
    decision: somente plano com approval_required=true
    rollback: remover activation-plan mantendo parity
---
# architecture

O plano compõe sobre a auditoria de paridade e o manifest vendorizado.
