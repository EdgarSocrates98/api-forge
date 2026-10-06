---
sdd: 1
feature: API_FORGE_AGENT_PROTOCOL_2_CAVEMAN_RTK_INTEGRATION
phase: build
profile: standard
status: done
upstream:
  path: plan.md
  sha256: "f37b86f4607c40a5fd9214b1560ca8a684a672a6e7ea11a04d72692da42adb50"
tasks:
  - id: compactor
    status: done
    evidence: tests/agentops/test_compact.py
  - id: cli
    status: done
    evidence: tests/agentops/test_compact.py
  - id: evals
    status: done
    evidence: tests/agentops/test_compact.py
claims:
  - compact_text is deterministic and read-only
  - critical lines and source hash are retained in CompactedOutput
  - context compact emits JSON without executing the input artifact
---

# build

O slice foi implementado em `apiforge.agentops.compact` e exposto por
`apiforge context compact`. A implementação não instala nem chama Caveman/RTK.
