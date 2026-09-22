---
sdd: 1
feature: API_FORGE_TOOL_ADAPTER_REGISTRY_B
phase: build
profile: standard
status: done
upstream:
  path: plan.md
  sha256: "2beab539604d950fbb5f47e408746fa2c2f5836f65b72996de6646d5b8ba1f21"
tasks:
  - id: typed-registry
    status: done
    evidence: sdd/API_FORGE_TOOL_ADAPTER_REGISTRY_B/evidence/tool-tests.txt
  - id: cli
    status: done
    evidence: sdd/API_FORGE_TOOL_ADAPTER_REGISTRY_B/evidence/tool-tests.txt
claims:
  - ToolAdapter list is derived from TOOL_REGISTRY
  - k6 is classified as network_or_credentialed
  - unknown adapter names are refused
---

# build

Implementado em `apiforge.agentops.tools` com `agentops tools` e
`agentops tool <name>`.
