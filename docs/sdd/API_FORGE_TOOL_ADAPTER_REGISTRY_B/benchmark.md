---
sdd: 1
feature: API_FORGE_TOOL_ADAPTER_REGISTRY_B
phase: benchmark
profile: standard
status: draft
upstream:
  path: secure.md
  sha256: "56718c375ed49ee265fa50e48fa66658ec27f22f0298a334f997641433c4c884"
baseline: "TOOL_REGISTRY raw dictionaries"
results:
  - artifact: sdd/API_FORGE_TOOL_ADAPTER_REGISTRY_B/evidence/tool-tests.txt
    outcome: measured-by-test
    note: "Schema lookup latency is local and not a performance target yet."
---

# benchmark

Esta feature mede descoberta e classificação, não execução das ferramentas.
