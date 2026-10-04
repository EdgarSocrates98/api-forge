---
sdd: 1
feature: API_FORGE_EVOLUTION1_DECISION_GOVERNANCE
phase: discover
profile: critical
status: done
approaches:
  - id: implicit-approval
    summary: treat model text or a plan as authorization
    verdict: refused -- confused deputy and unsafe side effect boundary
  - id: policy-approval-gate
    summary: evaluate request, evidence, policy and human ApprovalGate separately
    verdict: chosen -- deterministic and fail-closed
chosen: policy-approval-gate
---

# discover

API Forge already has `AgenticPolicy` and `ApprovalGate/v1`; the gap is a
single reusable decision admission service and audit record.
