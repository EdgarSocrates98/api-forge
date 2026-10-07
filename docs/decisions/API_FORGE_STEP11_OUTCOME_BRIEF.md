# API Forge Step 11 — Outcome Brief

Date: 2026-10-08
Branch: `evo/step11-agentic-closure`
Status: REVIEW — the governed agentic closure wave is shipped; every
external/provider boundary remains declared and unresolved by policy.

## 1. Architecture assessment

API Forge is now an evidence-driven, context-engineered Agentic
Engineering Operating System for APIs: a deterministic control plane
around probabilistic agents. The step-11 wave added twelve phases on
top of the existing offline-first platform without rewriting it —
every plane composes with what already existed:

- **Context Plane** — capsule/CAS substrate plus measured quality,
  sufficiency gates and `RoleContextPlan` v2 policies (phase 1).
- **Trust Plane** — `TrustUnit`/`TrustedRef`, taint propagation and
  memory security gates; "data is not instruction" is enforced by
  validators, not prose (phase 2).
- **Economy Plane** — unified token economics, declared provider
  pricing and budget reconciliation over observed receipts (phase 3).
- **Governance Plane** — agent governor (Information Gain v2, stop
  policy, recovery, loop detection) and the decision control plane
  lifecycle `SHADOW → ASSISTED → ACTIVE` with `FALLBACK` triggers
  (phases 4–5).
- **Routing/Retrieval** — adaptive model router with hard constraints
  and champion/challenger scorecards, L0–L4 retrieval ladder and gated
  query rewriting (phase 6).
- **Observability** — OTLP/GenAI export, W3C correlation ids and a real
  collector acceptance job (phase 7).
- **AgentOps** — run inspection, run-to-run comparison and a declared
  token-waste detector (phase 8).
- **Tool surface** — MCP audit (0 findings), declared exceptions,
  pagination/disclosure engineering and the §44 compliance matrix
  (phase 9).
- **Public boundary** — Forge Protocol `forge-protocol/v1`, a governed
  facade over the runtime: 8 verbs, human-gated mutations, persisted
  tasks and honest `unresolved` where no data exists (phase 10).
- **Eval plane** — rubric trace grading, synthesized adversarial
  security and memory corpora, quality×cost×latency frontier and a
  declared live-eval layer whose provider tier is `deferred_external`
  (phase 11).
- **Lab/Knowledge/Supply chain** — §28 scenario catalog (13 kinds),
  7-state knowledge freshness with drift rollups and a declared-edge
  impact graph, `doctor --agentic` over 8 planes, CI parity/wheel-smoke
  and a deterministic supply-chain audit (phase 12).

## 2. Changes implemented

| Phase | Commit | Delivery |
|---|---|---|
| 0 | `a2a89d9` | baseline, CI, capability gap matrix |
| 1 | `f634494` | context quality engine, sufficiency, RoleContext v2 |
| 2 | `2e4ec8d` | trust plane, taint, memory security v2 |
| 3 | `665354c` | token economics, provider pricing, budget reconciliation |
| 4 | `c928193` | agent governor, IG v2, stop/recovery/loop detection |
| 5 | `008b925` | decision control plane lifecycle |
| 6 | `0c05fd9` | adaptive retrieval, model router, scorecard |
| 7 | `ae9916f` | OTLP/GenAI export, correlation, collector gate |
| 8 | `3e64990` | AgentOps inspect/compare/waste |
| 9 | `bcbbaa5` | MCP audit/engineering/compliance, bounded collections |
| 10 | `ded3292` | Forge Protocol public boundary + kernel-boundary doc |
| 11 | `8e9d457` | eval plane: grading, adversarial, memory, frontier, live |
| 12 | `6e268aa` | lab catalog, knowledge engine, CI/supply chain, doctor |

Aggregate diff on the branch: **492 files, +27,418 / −161** across the
12 commits. New public contracts are frozen `VersionedContract`s with
registry entries, contract docs and `AF-*` refusal codes cataloged in
`docs/catalog-contract.md`.

## 3. Remaining gaps

Explicit, declared — never hidden:

- **Live provider tier** — `evals live` reports `deferred_external`;
  no provider adapter exists by design (human-gated boundary).
- **CVE/advisory scanning** — the supply-chain audit names it
  `unresolved`; no offline stub fabricates assurance.
- **agent → knowledge edge** — the impact graph names it `unresolved`;
  no declared carrier exists in `agents/*.md` and none was inferred.
- **5 of 13 lab scenario kinds** — latency regression, auth migration,
  rate limit, event contract and pagination are declared gaps, not
  fabricated coverage.
- **pip check inside uv venvs** — no pip module; the CI job covers it
  where pip exists.
- **provider-accounted cost** — frontier `cost_state` stays
  `unresolved` without provider cost data; tokens are never inferred
  from bytes.
- **Dependency locking** — declared ranges + vendored assets per
  ADR-011; Spark Forge's hashed lockfile model is a named difference,
  not an adopted one.

## 4. Test evidence

- Full suite on `evo/step11-agentic-closure`: **1707 passed,
  2 skipped** in ~361s (`pytest -q`, external basetemp on this Windows
  host — `%TEMP%\pytest-of-edgar` is ACL-corrupted, recorded quirk).
- Static gates: `ruff check` clean, `ruff format` 986 files, `mypy
  src/apiforge` no issues in 557 files.
- Platform gates: release gate PASS; `capabilities verify` 21/21;
  `agents check` drift `[]`; skills mirrors ok; vendor parity 127
  files; `sdd check` ok over 70 features.
- Per-phase focused suites and regression re-runs are recorded in each
  SDD feature's `evidence/` under `docs/sdd/API_FORGE_STEP11_*`.

## 5. Eval evidence

29 corpora / 195 deterministic cases, all offline:

- `evals knowledge-drift` 5/5 (verified, stale, conflicted,
  deprecated, unresolved — conflict pairs named).
- `evals trace-grading` 5/5; `security-adversarial` 9/9 (3 contained,
  6 refused, 0 escaped); `memory-evals` 9/9 over the §24 axes.
- `evals frontier` — Pareto over declared profiles; cost unresolved
  without provider data.
- `evals live` — deterministic tier green; provider tier
  `deferred_external`.
- `evals economy` — 12-case benchmark green; `economy-hardening` and
  `agentic-quality` waves preserved from earlier phases.
- `lab scenarios` — 13 kinds: 8 covered via real fixture/eval/proof,
  5 declared gaps.
- `mcp audit` — 0 findings, 1 declared exception, 151 tools.
- `supply_chain_audit` — dependency inventory, vendor parity, corpus
  consistency, surface lock 151; CVE + uv-venv pip unresolved.

## 6. Context/token/cost results

- `evals economy` measured on the recorded corpus: **median byte
  reduction 0.477 vs baseline** (per-case reductions 0.39–0.55),
  **evidence recall 1.0 on all 12 cases**, quality floor met.
- Token figures remain `unresolved` by contract — provider tokens are
  only ever read from a host transcript, never inferred from bytes
  (same rule as Spark Forge).
- Frontier cost axes stay `unresolved` where no provider-accounted
  input exists; no cost claim is made.
- The full wave ran at zero model spend: every eval, doctor probe,
  drift rollup and graph build is deterministic and offline.

## 7. Security assessment

- Trust plane: `evaluate_gates` pipeline (scope → origin → evidence →
  trust → outcome → freshness), allowlist-first `authorize` over
  `rules/tool_risk.yaml`, propagation with union taint and
  weakest-source trust, `trust_unit` for tool output.
- The `security-adversarial` corpus drives 9 synthesized attacks
  against these shipped defenses: 3 contained, 6 refused, 0 escaped.
- `docs/security/agentic-threat-model.md` maps every §10–§11 attack
  class to its defense module and eval evidence.
- Memory: candidate → persist/quarantine/reject gates, advisory
  invalidation, quarantine backlog surfaced by `doctor --agentic`.
- All mutation surfaces stay human-gated: Forge Protocol `attach`/
  `handoff` prepare records only; MCP ships read-only projections.
- Freshness widening is strictly conservative: `conflicted`/
  `deprecated` joined every untrusted set; `verified` is the only new
  trusted state and is stronger than `fresh`.

## 8. MCP compliance status

- Surface: 151 tools full, 6 gateway operations compact
  (`apiforge_discover`, `apiforge_call`, ...); spec pinned at
  2025-11-25 per `docs/mcp-compliance.md` §44 matrix.
- `mcp audit`: **0 findings, 1 declared exception** (`accepted` for
  the `perf_memory_search` overlap, declared in policy, never
  suppressed).
- Bounded collections: `limit` parameters on real collection tools and
  matching `--limit` CLI verbs; docstring honesty on aggregate tools.
- Surface lock: `supply_chain_audit` counts `full_tools()` (151) so a
  silent tool addition fails the audit.
- 3 new read-only tools this phase (`knowledge_drift`,
  `knowledge_impact`, `lab_scenarios`) — mutations stay CLI-only.

## 9. API Forge vs Spark Forge comparison

Compared against the local `spark-forge-aws` checkout (evidence-based,
not claimed parity):

| Axis | API Forge (this wave) | Spark Forge (observed) | Verdict |
|---|---|---|---|
| Domain | API engineering (contracts, migrations, data access, messaging, observability) | PySpark/Glue/EMR/Iceberg data engineering on AWS | different specialization, same method |
| Deterministic evidence | `fact_id`/`rule_id`, `AF-*` refusal codes, `unresolved` in every contract | `Fact`/`Finding` with `fact_id`/`rule_id`, `SF-*` rules, refused expected_gain | equivalent discipline |
| SDD | 10-phase cascade (discover→ship) + sha256 stamps + `sdd check` over 70 features | 6-phase (explore→ship) + `sdd check` | equivalent, deeper chain here |
| Context economy | capsule/CAS + quality engine + profiles; median byte reduction 0.477, recall 1.0 | Context Gateway profiles with byte caps (6k/16k/30k); measured payload_bytes | equivalent approach, different mechanisms |
| Agent governance | governor + IG v2 + stop/recovery/loop + decision lifecycle SHADOW→ASSISTED→ACTIVE→FALLBACK | Decision Plane shadow mode + receipts (23 cases, `activation_ready: false`) | AF lifecycle deeper (ACTIVE promotion exists) |
| Memory/trust | governed memory, taint, quarantine, 8-axis evals, trust_units | case-local state; no governed memory plane observed | AF ahead |
| Eval plane | 29 corpora/195 cases: grading, adversarial, memory, frontier, live layer | token_efficient suite + decision seed (23 cases) + eval harness | AF broader coverage axes |
| MCP surface | 151 tools, audit 0 findings + declared exceptions, bounded collections, disclosure/page | 141 tools, 52 detail_level, surface.lock.json gate | comparable, AF adds audit/benchmark |
| Lab | declared scenario catalog (13 kinds; 8 covered, 5 honest gaps) | executable lab: scenario/run/receipt v1 contracts + golden + generators/probes/compose | Spark ahead (executable vs declared) |
| Locking/supply chain | declared ranges + vendor manifest + audit; CVE boundary unresolved | `uv pip compile` hashed lockfiles per python + `pip-audit` job | Spark ahead (real lock + live audit) |
| CI parity/wheel | windows-parity + wheel-smoke jobs (added this wave) | py3.10–3.12 matrix + wheel job ubuntu+windows | comparable after this wave; Spark covers more python minors |
| Observability | OTLP/GenAI export + W3C correlation + real collector gate | `telemetry export` verb | AF ahead (interoperable export + gate) |
| Public protocol | Forge Protocol `forge-protocol/v1` (8 verbs, human-gated) | none observed | AF ahead |
| Coordination | 25 coordinators, 9-section contract, 3 generated mirrors + Devin layer | 14 coordinators + 5 executors, playbook floor on all platforms | comparable, different shapes |
| Token honesty | bytes measured; provider tokens `unresolved` without transcript | same rule (bytes never imply tokens) | identical honesty contract |

**Honest verdict**: equivalent engineering discipline with different
domain specializations. API Forge is ahead on governed memory/trust,
decision lifecycle depth, eval-plane breadth, observability export and
the governed public boundary. Spark Forge is ahead on the executable
lab, hashed dependency locking and a live `pip-audit` job — the two
latter are named gaps in §3 and §10, not hidden.

## 10. Next roadmap

Ordered by evidence value:

1. **Executable lab** — lift the 5 declared-gap scenario kinds into
   real fixtures/evals (Spark's `lab/` contracts are the reference
   shape: scenario-v1 + run-v1 + receipt-v1).
2. **Hashed dependency locking** — evaluate `uv pip compile` lockfiles
   per ADR-011's revisit trigger; the `uv.lock` residue exists but
   stays uncommitted until the ADR is revisited.
3. **CVE scanning** — wire `pip-audit` (or equivalent) as a separate
   non-blocking CI job like Spark's `audit`, keeping the offline
   core untouched.
4. **agent → knowledge carrier** — extend the agent contract with a
   declared `knowledge_packs` field so the impact-graph edge resolves.
5. **Provider tier** — the live-eval provider adapter remains a
   human-gated boundary; when approved, it lands behind the same
   receipt/unresolved discipline.
6. **Forge kernel** — `docs/architecture/forge-kernel-boundary.md`
   records the analysis; extraction stays deferred until a second
   consumer exists.

## Proof

- Full suite: `1707 passed, 2 skipped` on the branch.
- Evals: `knowledge-drift` 5/5, `trace-grading` 5/5,
  `security-adversarial` 9/9 (0 escaped), `memory-evals` 9/9,
  `economy` median reduction 0.477 recall 1.0, `live` deterministic
  tier green + provider `deferred_external`.
- Gates: release gate PASS, capabilities 21/21, agents drift `[]`,
  skills mirrors ok, vendor 127 files, `sdd check` ok (70 features),
  `mcp audit` 0 findings, `supply_chain_audit` ok with 2 named
  unresolved, ruff+format+mypy clean (557 files).
- SDD: `docs/sdd/API_FORGE_STEP11_*` — 7 feature bundles with hash
  chains and G1–G3 evidence.
