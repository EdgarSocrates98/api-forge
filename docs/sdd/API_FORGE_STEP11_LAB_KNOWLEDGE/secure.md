---
sdd: 1
feature: API_FORGE_STEP11_LAB_KNOWLEDGE
phase: secure
profile: critical
status: done
threat_model:
  - "CVE stub as fabricated assurance — the supply-chain audit names CVE
    scanning an unresolved external boundary instead of shipping an
    always-clean stub; no vulnerability claim is made offline"
  - "inferred impact edges as fabricated provenance — the graph derives
    edges only from declared data (pack.yaml, source_authority,
    evals.yaml, rule catalog, skill manifests); agent->knowledge stays
    unresolved and the contract documents that the edge is named, never
    inferred"
  - "receipt forgery path — drift consumes explicit SourceObservation
    receipts passed by the caller; the module performs no fetch and no
    persistence, so a forged receipt is an input-integrity question
    answered by the existing trust plane, not silently trusted"
  - "conflict suppression — disagreeing receipts surface as `conflicted`
    with the pairs named in the verdict; nothing is averaged or
    majority-voted"
  - "lab cell inflation — a cell declaring both coverage and a gap
    refuses AF-LAB-CELL-CONFLICT; a cell with neither refuses
    AF-LAB-CELL-UNDECLARED; generated or phantom coverage cannot pass"
  - "doctor as mutation vector — the agentic doctor is read-only: it
    parses persisted state and reports; no write path exists in the
    module"
  - "freshness downgrade — widening FreshnessState is additive;
    conflicted/deprecated join every untrusted set so a stricter new
    state cannot slip through a stale-only filter"
  - "wheel smoke as supply-chain check — the CI job builds the wheel,
    installs it into a clean venv and runs the CLI, catching
    missing-package-data failures before publish"
upstream:
  path: verify.md
  sha256: "e2f675fc3940d88cf55f8178865ac8aaefcb22c588f3aba841db6ed562df13ec"
---

# secure

The phase adds no provider call, network path, secret access or write
surface beyond the CLI verbs' existing governed writes. Every new
module is offline and deterministic; every external boundary (CVE
database, agent->knowledge carrier, pip in uv venvs) is reported as
unresolved rather than simulated.
