---
sdd: 1
feature: API_FORGE_STEP11_FORGE_PROTOCOL
phase: intent
profile: critical
status: done
risk_class: medium
problem: the governed runtime has no versioned public boundary — external
  callers and interop peers have no declared capability matrix, no task
  lifecycle surface, no evidence bundle contract and no honest refusal
  semantics for unknown capabilities, undeclared engines or unacknowledged
  risk
success: "forge capabilities|health|submit|status|inspect|attach|result|
  evidence|handoff emit forge-protocol/v1 contracts; capability/engine/
  risk gates refuse with AF-FORGE-* codes; tasks persist under
  .apiforge/forge/ and project governed state only through attach;
  unresolved/gaps stay explicit; 5 read-only MCP tools mirror the read
  plane; docs/architecture/forge-kernel-boundary.md records the §49
  analysis"
out_of_scope:
  - kernel extraction into a standalone package (analysis only, per §49)
  - network transport / remote handoff delivery (prepared records only)
  - task execution or agent dispatch through the forge surface
  - MCP mutation tools (read plane only)
upstream:
  path: discover.md
  sha256: "ba86cacb2bf4efa50c9c1601815dd85b74c26e8d619e9fefe555fd65b44b57b8"
---

# intent

A facade over the governed runtime, never a second runtime. Submit
validates and persists; attach links to a governed TaskSpec; result and
evidence project only observed artifacts and name their gaps.
