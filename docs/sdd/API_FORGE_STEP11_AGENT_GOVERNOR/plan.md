---
sdd: 1
feature: API_FORGE_STEP11_AGENT_GOVERNOR
phase: plan
profile: critical
status: done
tasks:
  - id: G1
    covers: [governor-decision-contracts, governor-policy-engine, information-gain-stop]
    test: sdd/API_FORGE_STEP11_AGENT_GOVERNOR/evidence/G1.txt
  - id: G2
    covers: [recovery-ladder, loop-detection, cli-mcp-surface]
    test: sdd/API_FORGE_STEP11_AGENT_GOVERNOR/evidence/G2.txt
  - id: G3
    covers: [eval-corpus, cli-smoke]
    test: sdd/API_FORGE_STEP11_AGENT_GOVERNOR/evidence/G3.txt
upstream:
  path: architecture.md
  sha256: "493ebb940ae9021df859936976971f985c810ac144f2f53c65bb690cd52fc136"
---

# plan
