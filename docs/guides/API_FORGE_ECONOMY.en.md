# API Forge Economy — spend only what is needed, with proof

[Português](API_FORGE_ECONOMY.md) · [Code catalog](../catalog-contract.md) · [Platform usage](API_FORGE_PLATFORM_USAGE.en.md)

The economy program (`prompt_evo_economy.md`, waves 0–8, then three hardening
rounds from `prompt_evo_new_economy_arch.md`, `prompt_evo_new_economy.md` and
`prompt_evo_new_economy_final.md`; the program is closed) cuts context, calls,
tools and verification down to the smallest sufficient amount **without
economizing on safety or evidence**. Everything is deterministic, offline and
read-only; no verb calls a provider, executes tests or mutates infrastructure.

## Invariants that never enter the budget

- contract verification, breaking-change checks, auth/security when relevant;
- provenance, critical policy, post-change verification and `unresolved` reporting;
- an exhausted budget becomes `unresolved` with an `AF-*` code, never a silent downgrade;
- SDD phases `contract`, `verify` and `secure` are protected: overruns are reported, never cut.

## Map by question

| Question | Command | Contract |
|---|---|---|
| What did this run spend and why? | `apiforge economy report`, `economy stats [--run-id R]`, `economy explain <run>` | `RunLedgerEntry/v1` |
| Smallest context for one operation? | `apiforge context capsule --target "POST /orders"`, `context expand ctx://sha256/<hex>` | `ContextCapsule/v1` |
| Which profile? | `apiforge runtime run <task> --profile economy\|balanced\|deep`, `sdd classify` | `EconomyPlan/v1`, `BudgetEnvelope/v1` |
| What changed since the last analysis? | `apiforge context delta`, `cache stats\|invalidate`, `context gc`, `--no-cache` | `CacheEntry/v1`, `DeltaSlice/v1` |
| Which knowledge pack to load? | `apiforge knowledge select --intent "..."`, `knowledge search --query "..."` | `ExpertiseSelection/v1`, `RetrievalResult/v1` |
| How to slim debate and agents? | `apiforge debate packet`, `agents audit` | `RefereePacket/v1`, `AgentUniqueness/v1` |
| How to shrink tool output? | `apiforge --output compact <verb>`, `slice tests\|log`, `mcp surface`, `apiforge-mcp --surface compact` | `TestSlice/v1`, `ErrorSlice/v1`, `ToolSurface/v1` |
| Which tests to run? | `apiforge verify plan --changed F --risk R` | `VerificationPlan/v1` |
| Test inconclusive — now what? | `apiforge verify escalate --static likely --test inconclusive` (or `--test-slice`) | `VerificationEscalation/v1` |
| Do I need production evidence? | `apiforge evidence gate --question "..." [--offline]` | `LiveEvidenceDecision/v1` |
| Cite evidence without pulling everything? | `apiforge evidence resolve evidence://finding/<id>` | `EvidenceNode/v1` |
| Is any knowledge pack stale? | `apiforge knowledge watch --manifest upstream.json --now <iso>` | `FreshnessWatch/v1` |
| What may each SDD phase spend? | `apiforge economy phase-budget --profile P [--usage U]` | `PhaseBudgetPlan/v1` |
| What did the run spend before resume? | `apiforge runtime checkpoint <task> <run>` | `EconomyCheckpoint/v1` |
| Is the setup overpaying? | `apiforge economy doctor`, `economy tier`, `economy roi` | `EconomyDoctor/v1`, `TierDecision/v1`, `RoleROI/v1` |

## Recommended agent flow

1. `sdd classify` sets the risk; risk sets the profile floor.
2. `context capsule` instead of the whole case; `context expand` only on demand.
3. `knowledge select` loads only triggered packs; `knowledge search --tier 1` first.
4. Before calling AWS/Datadog/CloudWatch/GitHub: `evidence gate`. Artifact
   questions stay local; only runtime effects get `live_read_only` (with a receipt).
5. After a change: `verify plan` picks V0–V5 and the impacted tests.
6. Inconclusive result: `verify escalate`. A conclusive test stops; read-only
   runtime only after an inconclusive test; never a mutation.
7. Resume: `runtime resume` keeps at least the `economy_checkpoint.json`
   profile and adds the calls already spent.

## Knowledge freshness (refresh separate from runtime)

Runtime uses validated local knowledge. A separate workflow writes a local
manifest `{"sources": {"<upstream>": {"fingerprint", "version", "observed_at"}}}`.
Packs declare in `pack.yaml`:

```yaml
freshness:
  upstream: openapi-spec
  source_hash: "sha256-of-the-validated-upstream"
  source_version: "3.1.0"
  expires_at: "2027-01-01T00:00:00+00:00"
  window_days: 180
```

`knowledge watch` reports `refresh_needed` only when fingerprint, version,
expiry or window (measured from `verified`) says the pack is stale.

## Cache

`APIFORGE_CACHE=off` disables the cache layers (any other value is the cache
directory); `--no-cache` does the same per command with identical output.
`APIFORGE_CACHE_HOME` enables the tier shared across repositories; every
object is re-hashed on read.

## Three kinds of evidence

Keep claims in their own class:

| Class | Where | What it proves |
|---|---|---|
| Deterministic benchmark | `evals economy`, `economy-routing`, `cache`, `economy-matrix` (`claim_scope: deterministic-safety-economy`), `economy-hardening` | contract correctness, mandatory roles, bytes and invariants on this corpus |
| Provider/token | `economy stats` with `token_coverage`, `economy report --transcript`, `economy ledger --run-id` | tokens only where measured; only model-facing rows (`rules/token_eligibility.yaml`) are eligible; `partial` is never an observed total; rollups keep observed/estimated/unresolved apart |
| End-to-end agentic quality | `evals agentic-quality` (`recorded-agentic-outputs`, `--responses-dir`, `--min-accuracy`, `--baseline`) | recorded specialist verdicts against ground truth under each profile; passes only above an absolute floor and without regressing vs deep or a baseline of the same benchmark (`BenchmarkIdentity/v1`) |

## Hard invariants

- Case, fact and graph paths are confined to the project and declared
  workspace repositories (`AF-PATH-OUTSIDE-ROOT` per ref); cases are read only
  through verified artifacts (`AF-CASE-HASH-MISMATCH`).
- `context_bytes` is global: class pools split across instances; a plan above
  the envelope cannot be built.
- Every provider call, including shadow challengers, is counted by the
  ControlPlane, so checkpoints and resumes see real spend.
- L0 early stop needs a structured, re-hashed `ProofReceipt`.
- Hardening evals run production code (`plan_roles`, `build_delta`); an oracle
  never re-implements the logic it guards.

## Changing economic policy

Before changing profiles, routing or trims:

```bash
apiforge evals economy-matrix --out before.json
# apply the change
apiforge evals economy-matrix --out after.json
apiforge evals gate --baseline before.json --candidate after.json
```

Any safety regression rejects. Per-wave benchmarks: `evals economy`,
`economy-routing`, `cache`, `selective-agentics`, `tool-economy`,
`economy-extras`, `economy-freshness`, `replay`.

## Unified token economics (phase 3)

Pipeline §19: Provider Usage -> Token Ledger -> Agent/Task/Run budgets ->
Provider Cost -> Economy Report.

- `economy record-usage --run-id R [--transcript t.jsonl] [--estimate N
  --method m]` appends `TokenLedgerEntry/v1` rows (append-only) under
  `.apiforge/economy/token_usage/<run>.jsonl`.
- `economy ledger --run-id R` rolls the ledger up: `observed` and
  `estimated` totals kept apart per run/task/agent; `unresolved` rows are
  counted in `unresolved_entries`, never summed.
- `economy pricing` lists the `rules/provider_pricing.yaml` catalog
  (`ProviderPricing/v1`). The shipped catalog is intentionally empty —
  the project does not assert live provider prices; callers declare
  their own via `--pricing <yaml>`.
- `economy cost --provider p --model m --accounting <json>` prices a
  `TokenAccounting` under the latest effective row; missing rates land in
  `missing_rates`, unreported fields land in `unresolved`, and a
  provider/model outside the catalog refuses
  `AF-ECONOMY-PRICING-MISSING`.
- `economy reconcile --run-id R --estimate <json> [--observed-cost X]`
  compares estimated vs observed tokens/cost/tool_calls/elapsed_ms with
  `calibration_error` per axis; an axis missing on either side stays
  `unresolved` — gain is never declared without measurement.
- `evals token-economics` runs `evals/corpus/token-economics` (basis
  rollups, pricing, calibration, unresolved axes).

## Limitations

- Tokens are `observed` only with a transcript; otherwise `unresolved`.
- `economy reconcile` compares what the ledger measured: observed `cost`
  exists only when priced via a declared catalog; `tool_calls` counts
  attribution rows carrying tool bytes.
- Question classification and test selection are term/symbol-declared;
  recall first, the ladder floor bounds cost.
- Per-SDD-phase usage is supplied as JSON; automatic attribution from the
  ledger is future work.
