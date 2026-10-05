---
sdd: 1
feature: API_FORGE_RUNTIME_CONVERGENCE_HARDENING2
phase: verify
profile: critical
status: done
results:
  - gate: full-test-suite
    state: pass
    evidence: 1751 passed, 2 skipped after release-parity fix
  - gate: static-quality
    state: pass
    evidence: ruff check, ruff format check and mypy strict
  - gate: focused-evals
    state: pass
    evidence: retrieval 1/1, model-routing 3/3, AgentOps 4/4, memory 9/9, security 9/9
  - gate: runtime-lab
    state: pass
    evidence: six local vertical probes and 21/21 scenario cells
  - gate: release
    state: pass
    evidence: scripts/check_release.py and supply_chain_audit.py
upstream:
  path: build.md
  sha256: "47d0b9f14d7dce7a7977bebe837c55a022d77a220922fe9feaa971cd4ad75963"
---

# verify

Verification includes unit, deterministic integration, runtime-path and
eval/Lab evidence. External provider and production behavior remain explicitly
unresolved.
