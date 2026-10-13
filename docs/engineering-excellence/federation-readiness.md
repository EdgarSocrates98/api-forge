# API Forge federation readiness

Status: **ready with limitations** for local, evidence-backed interoperability.
This document records what API Forge already exposes, how to prove it locally,
and what is still missing before a cross-Forge wire contract can be treated as
interoperable. It is an audit of the current repository, not a declaration that
another Forge or a production provider has implemented the protocol.

## Executive summary

API Forge already has the main shapes needed for a federated boundary:

- versioned capability, task, status, result, evidence, handoff and health
  contracts under `docs/contracts/`;
- a deterministic local Forge Protocol façade under `src/apiforge/forge/`;
- bounded TaskSpec/runtime execution with risk gates, evidence and unresolved
  outcomes;
- content-addressed context references (`ctx://sha256/...`) and evidence
  artifacts;
- SDD phase/hash/gate validation;
- measured economy and token-ledger semantics that preserve
  `observed`/`estimated`/`unresolved`;
- local golden, holdout, mutation and adversarial evaluation paths; and
- provider-neutral observability plans, normalized fixtures and host-owned
  export boundaries.

The existing Forge Protocol is therefore a strong local contract candidate, not
yet a complete federated protocol. `forge handoff` produces
`delivery: prepared`; it does not perform a live cross-engine call. The next
engine must implement the same wire contracts and participate in an
interoperability matrix before the boundary is proven.

## Capability evidence matrix

| Capability | Already exists | Command-level proof | Focused tests | Limits relevant to federation |
|---|---|---|---|---|
| **Contracts** | OpenAPI/gRPC contract intelligence, capability matrix, and `forge-protocol/v1`. The wire surface includes `ForgeCapabilityDescriptor/v1`, `ForgeTaskRequest/v1`, `ForgeTaskStatus/v1`, `ForgeTaskResult/v1`, `ForgeEvidenceBundle/v1`, `ForgeHandoff/v1` and `ForgeHealth/v1`. | `apiforge capabilities verify`  
`apiforge forge capabilities --detail-level summary`  
`apiforge evals forge-protocol` | `tests/contract_intel/test_contract_intel.py`  
`tests/contracts/test_conformance.py`  
`tests/forge/test_protocol.py` | The local matrix is evidence-backed, but a descriptor is not proof that another engine can execute the capability. There is no live transport, remote authentication handshake or second-engine compatibility test in this repository. |
| **Runtime** | TaskSpec lifecycle, sealed/budgeted execution, sandboxed build path, append-only state, independent review/acceptance, recovery and explicit `blocked`/`failed`/`unresolved` states. `platform verify-runtime` executes committed allowlisted local probes and emits `af-platform-runtime-receipt/1`. | `apiforge task --help`  
`apiforge runtime --help`  
`apiforge platform verify-runtime --root . --detail-level summary` | `tests/taskspec/test_lifecycle.py`  
`tests/runtime/test_runtime.py`  
`tests/runtime/test_control_plane.py`  
`tests/application/test_platform_runtime.py` | Runtime receipts prove local fixtures and declared probes. They do not prove a remote provider, hosted CI, production deployment, production SLOs, rollback or cross-engine execution. |
| **Context** | `context resolve` scopes repository/workspace/target context; capsules carry hash-addressed `ctx://` refs, provenance, budgets and limitations; funnel and quality commands measure bytes and sufficiency. `ForgeHandoff` can carry context refs. | `apiforge context resolve --scope repo`  
`apiforge context funnel --case .apiforge/case`  
`apiforge context capsule --target "POST /orders"`  
`apiforge context quality --help` | `tests/contracts/test_context_capsule.py`  
`tests/context/test_quality.py`  
`tests/e2e/test_funnel.py`  
`tests/evals/test_context_quality.py` | `ctx://` is content-addressed, but cross-engine resolution, ownership, freshness negotiation and transport are not standardized here. Token metrics remain `unresolved` without observed usage/transcript data; context quality may correctly be `degraded` or `unresolved`. |
| **SDD** | Canonical `discover → intent → contract → architecture → plan → build → verify → secure → benchmark → ship` flow, strict frontmatter, upstream hash cascade, evidence gates, risk classification and named `AF-SDD-*` refusals. | `apiforge sdd check --root docs/sdd`  
`apiforge sdd status --root docs/sdd`  
`apiforge sdd classify --description "contract change" --path openapi.yaml` | `tests/sdd/test_checks.py`  
`tests/sdd/test_risk_classify.py`  
`tests/sdd/test_evidence.py` | SDD validates local artifacts, hashes and declared evidence. It does not make another Forge honor the same phases, gates or evidence meanings; federation needs a shared profile/version and compatibility rules. |
| **Economy** | Context budgets, phase budgets, cache/delta accounting, run ledgers, token ledgers, provider capability metadata and reconciliation keep measured bases separate. Safety, provenance, contract verification, `secure`, `verify` and `unresolved` are protected from trimming. | `apiforge economy report --root .`  
`apiforge economy stats --help`  
`apiforge evals economy-hardening`  
`apiforge evals economy-matrix --out before.json` | `tests/economy/test_report.py`  
`tests/economy/test_token_ledger.py`  
`tests/economy/test_reconciliation.py`  
`tests/evals/test_economy_eval.py`  
`tests/evals/test_economy_matrix.py` | `Budgets` and `TokenAccounting` are candidates for a shared contract, but the full ledger, pricing catalog and routing policy are local. Tokens are not observed without a transcript; the shipped pricing catalog does not assert live provider prices. |
| **Evals** | Declarative local corpora cover protocol lifecycle/refusals, context quality, runtime gates, economy hardening, observability, replay and adversarial behavior. Evals distinguish golden, holdout, mutation and unresolved evidence. | `apiforge evals forge-protocol`  
`apiforge evals context-quality`  
`apiforge evals economy-hardening`  
`apiforge evals list` / `apiforge evals validate` | `tests/evals/test_eval_plane.py`  
`tests/evals/test_runtime_evals.py`  
`tests/evals/test_context_quality.py`  
`tests/evals/test_economy_eval.py`  
`tests/evals/test_observability_evals.py` | These are local deterministic proofs over API Forge corpora. They do not establish model/provider parity, host parity or end-to-end behavior with another Forge. A declaration in YAML is not runtime proof. |
| **Observability** | OTel-aligned normalization, health/SLO correlation, vendor-specific read plans, explicit capabilities, redaction, bounded transport/circuit behavior and host-owned export readiness for OTel, Datadog and Dynatrace. | `apiforge observability health --source tests/fixtures/observability/otel.json --service orders`  
`apiforge observability read-plan --provider otel --service orders --start 2026-01-01T00:00:00Z --end 2026-01-01T01:00:00Z`  
`apiforge observability capabilities` | `tests/observability/test_contracts.py`  
`tests/observability/test_readiness.py`  
`tests/observability/test_read_plan.py`  
`tests/observability/test_host_export.py`  
`tests/evals/test_observability_evals.py` | The core never resolves secret values, opens provider sockets or installs SDKs. Export needs a host callback, allowlisted endpoint, credential broker and approval. CloudWatch export remains a future evolution; local telemetry does not prove production health. |

## Existing federated surface

The current wire surface is intentionally small and engine-neutral:

| Contract | Current guarantee |
|---|---|
| `ForgeCapabilityDescriptor/v1` | Projects a capability matrix row with state, risk, surfaces, evidence and limitations. `heuristic` is never upgraded on the wire. |
| `ForgeTaskRequest/v1` | Freezes task intent, JSON inputs, budgets, risk and provenance before persistence. |
| `ForgeTaskStatus/v1` | Exposes a small stable lifecycle while retaining the governed task id/state and unresolved diagnostics. |
| `ForgeTaskResult/v1` | Maps an `OutcomeBrief`; missing governed evidence becomes `unresolved`, never fabricated `ok`. |
| `ForgeEvidenceBundle/v1` | Carries artifact paths and SHA-256 digests; consumers verify correspondence by hash. |
| `ForgeHandoff/v1` | Packages request, status, evidence refs and context refs for a named peer; delivery remains `prepared`. |
| `ForgeHealth/v1` | Reports engine identity, protocol version, measured capability count, task counts and degraded state. |

The local policy declares `api-forge` as the engine, `forge-protocol/v1` as the
protocol and `spark-forge`/`the-forger` as known peers. This is a declaration
for validation and refusal behavior, not evidence that those peers currently
speak the protocol.

Relevant implementation and contracts:

- [`src/apiforge/contracts/forge_protocol.py`](../../src/apiforge/contracts/forge_protocol.py)
- [`src/apiforge/forge/protocol.py`](../../src/apiforge/forge/protocol.py)
- [`src/apiforge/rules/forge_protocol.yaml`](../../src/apiforge/rules/forge_protocol.yaml)
- [`docs/architecture/forge-kernel-boundary.md`](../architecture/forge-kernel-boundary.md)
- [`docs/capabilities/API_FORGE_CAPABILITY_MATRIX.md`](../capabilities/API_FORGE_CAPABILITY_MATRIX.md)

## Gaps before calling it a federated contract

These are gaps, not hidden capabilities. They should be closed only when a
second real engine and an interop fixture provide evidence.

1. **Peer implementation and transport.** Add a second implementation of
   `forge-protocol/v1`, a transport/endpoint contract, timeout/retry behavior,
   idempotency and replay protection. Current handoff is a prepared bundle.
2. **Capability negotiation.** Define protocol/schema version negotiation,
   supported/required feature sets, downgrade rules and incompatibility
   refusals. `protocol_version` alone is not negotiation.
3. **Identity and trust.** Define peer identity, authentication, authorization,
   request provenance and trust boundaries. Local risk gates do not authorize a
   remote caller.
4. **Portable context resolution.** Specify how a peer resolves `ctx://` refs,
   which engine owns the bytes, how freshness is checked, and what happens when
   a ref is unavailable or outside the declared workspace.
5. **Shared budget semantics.** Freeze the portable subset of `Budgets` and
   `TokenAccounting`; keep provider pricing, routing tiers and local ledgers
   behind engine-owned extensions until comparability is proven.
6. **Cross-engine evidence and receipts.** Define evidence exchange,
   verification responsibility, freshness, signature/attestation needs and
   whether a receipt proves correspondence only or also an external action.
7. **Correlation and observability.** Carry stable task/run/trace/context ids
   across the boundary and define redaction, retention and failure semantics
   for peer-to-peer telemetry.
8. **Interop matrix and CI gate.** Add a versioned matrix covering discovery,
   submit, risk refusal, lifecycle projection, evidence verification, handoff,
   health degradation and malformed/unknown inputs against at least one real
   peer. Local protocol evals are necessary but not sufficient.
9. **External lifecycle ownership.** Keep merge, push, deployment, provider
   mutation and production rollback outside the offline core. A federated
   contract must name the host/provider owner and require an approval and
   independent receipt for those actions.

## Recommended minimum contract additions

When federation work starts, extend the existing protocol rather than creating
a second registry. The minimum review should cover:

```text
handshake:
  engine_id, protocol_versions, contract_versions, capabilities, auth_mode
request:
  task_id, idempotency_key, capability_id, intent, inputs, budgets, risk,
  origin, requested_by, requested_at, context_refs
result:
  status, payload, evidence_refs, gaps, limitations, unresolved, error_code
evidence:
  artifact_ref, sha256, kind, produced_at, freshness, verifier
correlation:
  task_id, run_id, trace_id, parent_ref
```

The fields above are a gap checklist, not an implemented schema. Add them only
with versioning, fixtures, refusal codes, security review and independent
verification.

## Local proof run

The following focused test set exercises the current local boundary and the
seven capability areas without changing code:

```bash
uv run --no-sync pytest -q \
  tests/forge/test_protocol.py \
  tests/application/test_platform_runtime.py \
  tests/e2e/test_funnel.py \
  tests/context/test_quality.py \
  tests/evals/test_context_quality.py \
  tests/evals/test_runtime_evals.py \
  tests/economy/test_report.py \
  tests/economy/test_hardening_reporting.py \
  tests/evals/test_economy_eval.py \
  tests/evals/test_economy_matrix.py \
  tests/evals/test_observability_evals.py \
  tests/observability/test_readiness.py \
  tests/observability/test_host_export.py \
  tests/observability/test_contracts.py
```

Repository-level governance checks:

```bash
apiforge capabilities verify
apiforge sdd check --root docs/sdd
git diff --check
```

## Limits and non-claims

- A fixture, golden, parser, prompt or local receipt is not production proof.
- Static API analysis does not execute application code; runtime probes execute
  only committed local fixtures.
- `ForgeHandoff/v1` prepares a bundle; no live cross-engine delivery exists in
  this branch.
- `ForgeEvidenceBundle/v1` proves artifact correspondence by hash; it does not
  prove authorship, permission, deployment safety or rollback.
- `observed`, `estimated`, `heuristic` and `unresolved` must remain distinct;
  absent evidence is not a successful result.
- Provider freshness, credentials, hosted execution, production SLOs, live
  database/broker behavior and external mutations require explicit host-owned
  adapters and independent receipts.
- This document does not add a shared kernel, change a contract, claim peer
  parity or authorize network/external actions.
