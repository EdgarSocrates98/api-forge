# RecoveryReceipt/v1

§26 proof that a governed recovery decision actually changed runtime
behavior. A [`RecoveryDecision/v1`](RecoveryDecision-v1.md) says *what should
happen*; the receipt records *who owned the action* and *what ran*, so a
decision can never look silently enforced.

| Field | Meaning |
|---|---|
| `receipt_id` | Deterministic id over run, sequence, capability, decision, attempt and action |
| `run_id` / `invocation_id` / `capability` | The failure this receipt answers, and the invocation a retry/fallback spawned when applicable |
| `failure_class` / `decision` / `attempt` | Carried verbatim from the governing `RecoveryDecision` |
| `owner` | `scheduler` (observed), `supervisor` (executed runtime work), `human` (escalation boundary), `none` (terminal stop) |
| `action_taken` | The concrete effect — `retried:<cap>`, `fallback:<cap>`, `replanned:<decision_id>`, `escalated:human_gate`, `stopped` |
| `outcome` | `executed` (real runtime effect), `refused` (governance blocked it, `code` names why), `skipped` (depth bound — see `AF-GOV-RECOVERY-DEPTH`), `observed` (scheduler-side action) |
| `code` | The `AF-*` that blocked or qualified the action (`AF-GOV-RECOVERY-NO-FALLBACK`, `AF-GOV-RECOVERY-REPLAN-REFUSED`, `AF-GOV-RECOVERY-DEPTH`, `AF-BUDGET-EXHAUSTED`, `AF-GOV-LOOP-DETECTED`) |
| `policy_id` / `policy_version` / `policy_hash` | §86 anchor to `rules/recovery_policy.yaml`: declared schema plus `sha256:` content hash, so a verdict binds to policy content, not a file name |
| `evidence` | `capability:<name>`, `invocation:<id>`, `routing_decision:<id>`, `plan:<id>`, `artifact:produced`/`artifact:none` |
| `unresolved` | Named gaps — the failed capability, the exhausted budget — never silent |

Receipts are persisted per run in `recovery-receipts.json`, embedded in the
`RunGovernanceContext` (`receipts`), listed in the `governance_postflight`
trajectory event and replayed by `resume_existing_run` — the resumed path
emits the same receipts for decisions observed during resumed work.
