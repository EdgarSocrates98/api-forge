---
sdd: 1
feature: API_FORGE_AGENTIC_PLATFORM
phase: intent
profile: critical
status: done
upstream:
  path: discover.md
  sha256: "a05cb5a0ac3b587944443b796891ed238a9e8e047ee3dd98d9f073e28f91962a"
problem: >
  API Forge analyzes APIs deterministically but cannot yet represent a unit
  of agentic work (TaskSpec), close an operation with an auditable outcome
  (OutcomeBrief), answer provenance/impact questions (Graphify), or reuse
  deterministic extraction across calls (TokenSave indexes).
success:
  - contracts-v1
  - task-verbs
  - brief-done-refusal
  - graph-verbs
  - extractor-cache
  - e2e-slice
out_of_scope:
  - database adapters (Redis/Mongo/Dynamo/Neptune) -- later spec
  - telemetry/OTel pipeline -- later spec
  - autonomy modes and runbooks -- later spec
  - knowledge packs and eval matrix -- later spec
  - remaining AWS collectors -- later spec
  - merge/push automation -- never
---

# intent

Turn the deterministic analysis core into a bounded agentic platform:
agentic work is expressed as sealed tasks, closed by briefs, connected by a
provenance graph, and made cheap by deterministic indexes -- never by
unrestricted execution.

## Success criteria

- **contracts-v1**: every canonical artifact has a versioned contract with
  conformance tests.
- **task-verbs**: a task can be created, reviewed, sealed, run and accepted
  through distinct verbs; acceptance is separate from execution.
- **brief-done-refusal**: `brief show` emits
  Status/Outcome/Human action/Proof/Gaps/Next/Open and refuses DONE while
  mandatory gaps exist.
- **graph-verbs**: `graph build/query/impact/trace/coverage/export` answer
  the prompt's use cases over a canonical JSONL store.
- **extractor-cache**: extractor output is cached by sha256 and cache hits
  land in the economy ledger.
- **e2e-slice**: one end-to-end slice -- discover -> API-IR -> finding ->
  task -> sandbox -> test -> evidence -> brief.
