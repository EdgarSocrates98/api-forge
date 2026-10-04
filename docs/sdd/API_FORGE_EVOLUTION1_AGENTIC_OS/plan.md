---
sdd: 1
feature: API_FORGE_EVOLUTION1_AGENTIC_OS
phase: plan
profile: critical
status: ready
upstream:
  path: architecture.md
  sha256: "8e9292a1079188231d02504231ba69eac981c4401e8a69ad82c3763378fc6ade"
tasks:
  - id: M1
    covers: [memory-contracts, governed-memory-store, trust-taint-gate]
    test: sdd/API_FORGE_EVOLUTION1_AGENTIC_OS/evidence/M1.txt
  - id: B1
    covers: [blackboard-store]
    test: sdd/API_FORGE_EVOLUTION1_AGENTIC_OS/evidence/B1.txt
  - id: C1
    covers: [semantic-checkpoint]
    test: sdd/API_FORGE_EVOLUTION1_AGENTIC_OS/evidence/C1.txt
  - id: S1
    covers: [cli-mcp-parity]
    test: sdd/API_FORGE_EVOLUTION1_AGENTIC_OS/evidence/S1.txt
  - id: D1
    covers: [deterministic-evals, documentation-and-evidence]
    proof: sdd/API_FORGE_EVOLUTION1_AGENTIC_OS/evidence/D1.txt
---

# plan

Wave 1 implements M1/B1/C1 in dependency order, then S1 and D1. Each task is
local and reversible; external provider and model work is intentionally
excluded. Verification must include focused tests, registry conformance,
Ruff/mypy and the SDD check. Remaining prompt phases become separate specs
with their own benchmarks and promotion evidence.
