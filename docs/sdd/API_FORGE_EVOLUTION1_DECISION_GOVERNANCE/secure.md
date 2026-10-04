---
sdd: 1
feature: API_FORGE_EVOLUTION1_DECISION_GOVERNANCE
phase: secure
profile: critical
status: done
upstream:
  path: verify.md
  sha256: "3f9ea5ca36f569d5e8ea7ea6aa11aa36dfd463fdaddc2f6e61857f2b9f9e211a"
threat_model: [confused-deputy, implicit-approval, missing-evidence, external-mutation]
---

# secure

The evaluator is fail-closed and returns no execution capability. Approval is
an explicit artifact, and default policy disallows mutation.
