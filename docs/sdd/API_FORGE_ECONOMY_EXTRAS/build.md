---
sdd: 1
feature: API_FORGE_ECONOMY_EXTRAS
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "56e7c063ab25145779009e60ea758011e36decdd24705d85f877c17cf40c77ee"
tasks:
- id: contracts
  status: done
  evidence: sdd/API_FORGE_ECONOMY_EXTRAS/evidence/economy-extras-tests.txt
- id: verbs
  status: done
  evidence: sdd/API_FORGE_ECONOMY_EXTRAS/evidence/economy-extras-tests.txt
- id: eval
  status: done
  evidence: sdd/API_FORGE_ECONOMY_EXTRAS/evidence/economy-extras-eval.json
claims:
- verification-plan
- retrieval
- evidence-refs
- economy-doctor
- provider-tiers
- stable-prefix
- locality
- extras-eval
---
# build

Implemented `verify plan`, `knowledge search`, `evidence resolve`, `economy doctor|providers|tier`, `doctor --economy`, `agentops prompt`, `workspace locality` and `apiforge evals economy-extras`, with MCP parity for the read verbs.
