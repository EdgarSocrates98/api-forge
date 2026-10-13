# Forge kernel boundary analysis (prompt §49)

Status: **analysis only** — `forge-kernel` is deliberately *not* created.
This document maps which abstractions are generic enough to become a shared
contract between API Forge, Spark Forge and The Forger, and which must stay
inside this repository.

Method: each candidate is judged on three axes — *generic* (usable without
API-domain semantics), *shared-contract* (safe to freeze as a wire
contract), *extractable* (does not drag repo-specific types with it).

## Candidate abstractions

| Abstraction | Home today | Generic? | Shared contract? | Verdict |
|---|---|---|---|---|
| Context (capsules, `ctx://`, funnel) | `context/`, `contracts/context.py` | mostly — the ref scheme is portable | yes, the `ctx://` ref + `ContextCapsule` shape could cross engines | **candidate for shared contract** — but the *funnel policy* stays local (it encodes our economy model) |
| Evidence (`EvidenceRecord`, bundles, sha256 artifacts) | `evidence/`, `contracts/evidence.py` | yes | yes — evidence is inherently a wire concern | **shared contract** — `ForgeEvidenceBundle/v1` already projects it |
| Memory (agentic memory, trust levels, quarantine) | `memory/`, `contracts/agentic_memory.py` | partially | the *shape* is generic; the *trust taxonomy* is our security model | **not yet** — the trust taxonomy must stabilize across engines first |
| Blackboard | `blackboard/` | yes | yes, but low value — other engines have their own | **shared contract optional** — expose via events, not shared storage |
| Budget (`Budgets`, envelopes, ledgers) | `contracts/task.py`, `economy/` | yes | partially — `Budgets` is tiny and portable; token ledgers are ours | **`Budgets` shared**; ledgers stay local |
| Runtime (taskspec runner, sandbox) | `taskspec/`, `sandbox/` | no — it IS the engine | no | **do not extract** — the runner is API Forge's identity |
| Governor (gain, stop, recovery, loop) | `governance/governor*` | partially | the *decision contract* could be shared; the policies are ours | **shared contract for GovernorDecision only** — policies stay |
| Decision (control plane, lifecycle) | `governance/control_plane.py` | partially | route lifecycle is generic, routes are ours | **not now** — too young to freeze |
| Security (gates, taint, quarantine) | `memory/security.py`, `trust/` | no — it is our threat model | no | **do not extract** — never weaken a boundary for reuse |
| Trust (units, propagation) | `trust/plane.py` | partially | `TrustUnit` annotation could cross engines | **watch** — one contract at most, later |
| Observability (spans, OTLP export) | `runtime/agent_telemetry.py`, `otel_export.py` | yes — OTel is already the shared contract | OTLP/GenAI *is* the contract | **already shared** — no kernel needed |
| Economy (token accounting, pricing, reconciliation) | `economy/` | yes | `TokenAccounting` basis is portable; pricing catalog is ours | **`TokenAccounting` shared candidate**; rest stays |
| Evals (corpora, gates, scorecards) | `evals/` | partially | corpus *format* could be shared; cases are ours | **format shared, content local** |
| Handoff | `contracts/task.py` + `forge/` | yes | yes — `ForgeHandoff/v1` is exactly this | **shared contract** — delivered |

## What is generic?

- The **wire lifecycle** (`ForgeTask*` states, evidence bundles, handoff,
  health, capability descriptors) — engine-neutral by design.
- **Content addressing** (`ctx://`, sha256 artifact refs) — portable by
  construction.
- **Budgets and token accounting shapes** — small, closed, honest about
  basis (`observed`/`estimated`/`unresolved`).
- **OTLP/GenAI telemetry** — an external standard already does this job.

## What remains domain-specific?

- API-IR, discovery, contract diff/compatibility, gRPC/REST/GraphQL/
  AsyncAPI modeling, data-access IRs, vertical capabilities — the reason
  API Forge exists.
- The governed runtime (TaskSpec lifecycle, sealing, supervision,
  acceptance) — the engine itself.
- The trust/security taxonomy — our threat model, not a shared one.

## What could become a shared contract?

Already delivered as versioned wire contracts in `contracts/forge_protocol.py`:

- `ForgeCapabilityDescriptor/v1`
- `ForgeTaskRequest/v1` · `ForgeTaskStatus/v1` · `ForgeTaskResult/v1`
- `ForgeEvidenceBundle/v1` (+ `ForgeEvidenceArtifact/v1`)
- `ForgeHandoff/v1`
- `ForgeHealth/v1`

Future candidates, when a second engine actually exists to test them:

- `ctx://` reference resolution rules (context portability)
- `TokenAccounting` basis taxonomy (cost comparability)
- `GovernorDecision` shape (why a run stopped/continued)

## What should NOT be extracted?

- The runtime, sandbox, taskspec machine — extraction would make the
  engine a library dependency of itself.
- The security/trust taxonomy — a shared security contract is a shared
  compromise; keep ours strict and local.
- The pricing catalog, provider tiers and routing scorecards — operator
  policy, not protocol.
- Anything whose only consumer is a hypothetical engine — the kernel must
  earn its existence from at least two real speakers of the protocol.

## Rule for the future kernel

A `forge-kernel` package may be created **when The Forger or Spark Forge
implements `forge-protocol/v1` against this repo**. Until then the shared
surface lives in `contracts/forge_protocol.py` + `forge/protocol.py` —
versioned, tested, and owned by this repository. Premature extraction
would freeze guesses instead of observed interop.
