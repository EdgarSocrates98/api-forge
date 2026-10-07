# BRAINSTORM: API Forge Economy — Freshness Watch, Live Gating, Progressive Verification and Resume Checkpoint (Onda 8)

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_FRESHNESS_RESUME |
| **Date** | 2026-09-28 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |
| **Source** | `prompt_evo_economy.md` §95–99, §104 (last four gaps after waves 0–7) |

---

## Initial Idea

Close the four remaining gaps of the economy program:

1. §96 Freshness Watch — compare every pack's declared upstream fingerprint,
   version and expiry with a locally recorded upstream manifest and say
   `refresh_needed` only when stale.
2. §97 Live evidence only when needed — classify the question; a static
   question never reaches AWS/Datadog/CloudWatch/GitHub.
3. §99 Progressive external verification — static → test → stop; only an
   inconclusive test escalates to read-only runtime evidence.
4. §104 Economic checkpoint on resume and per-SDD-phase budgets.

## Grounding (existing code)

| Existing | Reuse |
|---|---|
| `knowledge/freshness.py::verify_pack_freshness` (one pack, one receipt) | watch iterates it over every pack, adds fingerprint/version/expiry |
| `PackFreshness` (`window_days`, `source_hash`, `authority`) | add optional `source_version`, `expires_at`, `upstream` |
| `AdapterMode` `static → fixture → live_read_only → live_mutation` (§98) | live gate and escalation never go past `live_read_only` |
| `TestSlice/v1` (wave 5) | escalation reads a saved slice to decide confirmed / passed / inconclusive |
| `ControlRun.calls_used` persisted per run | checkpoint carries it plus profile, ladder, phase spend |
| `BudgetEnvelope` per profile | phase budgets split its calls and context bytes |

## Approaches

### A. Four small deterministic verbs + one supervisor hook (chosen)

`knowledge watch`, `evidence gate`, `verify escalate`, `economy phase-budget`,
`runtime checkpoint`; resume reads/writes `economy_checkpoint.json`.
Pros: each gap is separately testable and gated; no provider; matches waves 5–7.
Cons: one more rules file per concern.

### B. Fold everything into `economy doctor`

Pros: one verb. Cons: doctor is diagnostic; watch/gate/escalate are decisions
agents call mid-task. Rejected.

### C. Live fetch of upstream fingerprints

Rejected: §95 says refresh is a separate workflow; runtime uses validated
local knowledge. The manifest is produced elsewhere and only read here.

## YAGNI

- No network, no provider SDK, no scheduler for the watch.
- No mutation mode anywhere; `live_mutation` is refused by the gate.
- Phase usage comes from a supplied usage JSON or the run ledger, not a new store.

## Validated decisions

1. Upstream manifest is a local JSON (`{source: {fingerprint, version, observed_at}}`).
2. Question classification is keyword-declared in `rules/live_evidence_triggers.yaml`; runtime wins only on explicit runtime terms.
3. Escalation stops at `live_read_only`; runtime inconclusive → unresolved.
4. Resume pins the checkpoint's effective profile (never lower) and reports cumulative spend.
5. `verify` and `secure` phases are protected: over-budget is reported, never cut (§100).

## Next Step

`/define .claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_FRESHNESS_RESUME.md`
