---
sdd: 1
feature: API_FORGE_DEVIN_INTEGRATION
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "6203295071dd1793b2517d090282c95944d108f63c42e5dd4726e991facbee65"
tasks:
  - id: payload-contract
    status: done
    evidence: sdd/API_FORGE_DEVIN_INTEGRATION/evidence/devin-tests.txt
  - id: runtime-observation
    status: done
    evidence: sdd/API_FORGE_DEVIN_INTEGRATION/evidence/devin-tests.txt
  - id: native-guardrails
    status: done
    evidence: sdd/API_FORGE_DEVIN_INTEGRATION/evidence/devin-tests.txt
claims: [desktop-cli-cloud-payloads, local-probe, fail-closed-hook]
---
# build

Implemented `apiforge devin payload|probe|capabilities` and the repository
`.devin/` layer.
