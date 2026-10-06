---
sdd: 1
feature: API_FORGE_STEP11_FORGE_PROTOCOL
phase: discover
profile: critical
status: done
approaches:
  - id: kernel-extraction
    summary: extract a standalone forge kernel package and re-implement
      task lifecycle there
    verdict: refused -- §49 asks for a boundary analysis, not extraction;
      duplicating the governed runtime would split the evidence chain
  - id: wire-only-a2a
    summary: model Forge as a network A2A protocol with transport and
      remote delivery
    verdict: refused -- nothing in the platform performs network calls;
      handoff must stay a prepared-record boundary, not a fake transport
  - id: governed-facade
    summary: versioned public facade (forge-protocol/v1) over the
      governed runtime — submit validates + persists, attach links to a
      governed TaskSpec, inspect/result/evidence project only what exists
    verdict: chosen -- honest, additive, reuses TaskSpec/Brief/ledger
      evidence and keeps refusal semantics in AF-FORGE-* codes
chosen: governed-facade
---

# discover

§46–§49 asks for a Forge Protocol: public capability/task/evidence
contracts, a minimal governed task surface, interop handoff records and
a kernel-boundary analysis without extraction. The governed runtime
(TaskSpec store, ledger, brief pipeline) already provides state and
evidence; what is missing is the versioned public boundary, the declared
capability/engine/risk policy, and honest projections of unresolved
states.
