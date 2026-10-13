---
sdd: 1
feature: API_FORGE_TOOL_ADAPTER_REGISTRY_B
phase: verify
profile: standard
status: done
upstream:
  path: build.md
  sha256: "14e217b4cb67b1a312019d3a47805c6119cafda81c67b9c2f2921079aa2a4075"
results:
  - gate: "pytest tests/agentops/test_tools.py"
    outcome: pass
    evidence: "2 passed"
  - gate: "ruff check src/apiforge tests/agentops"
    outcome: pass
    evidence: "All checks passed"
  - gate: "mypy src/apiforge"
    outcome: pass
    evidence: "no issues found"
---

# verify

Paridade, safety class, parser, evidence producer e recusa de ferramenta
desconhecida possuem cobertura focada.
