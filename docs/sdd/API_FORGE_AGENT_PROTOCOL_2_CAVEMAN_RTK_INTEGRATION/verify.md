---
sdd: 1
feature: API_FORGE_AGENT_PROTOCOL_2_CAVEMAN_RTK_INTEGRATION
phase: verify
profile: standard
status: done
upstream:
  path: build.md
  sha256: "e251050bcd2d5364327343f18a877180432e77df27947c5c8936c5c00aeb6271"
results:
  - gate: "pytest tests/agentops/test_compact.py"
    outcome: pass
    evidence: "5 passed"
  - gate: "pytest -q"
    outcome: pass
    evidence: "695 passed, 1 skipped"
  - gate: "ruff check src/apiforge tests/agentops/test_compact.py"
    outcome: pass
    evidence: "All checks passed"
  - gate: "mypy src/apiforge"
    outcome: pass
    evidence: "no issues found in 233 source files"
---

# verify

O compactador preserva erro crítico, hash de origem e o arquivo original sem
mutação. A suíte completa permanece verde.
