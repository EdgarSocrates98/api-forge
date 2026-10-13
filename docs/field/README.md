# Field validation protocol

Evidence-driven cycle: real tasks on real repositories, recorded so the next
roadmap theme comes from measured frequencies, not intuition.

## Before the first run

1. Register every task in `corpus.yaml` (`id`, `scenario`, `repo_ref`,
   `registered_at`, `prompt`, `ground_truth`). Own repositories use
   `sha256:<hex>` refs; map them to local paths in the git-ignored
   `repos.local.yaml`:

   ```yaml
   'sha256:<hex>':
     name: my-service
     path: E:/work/my-service
   ```

2. Commit `corpus.yaml` and `hypothesis.md`. The git commit time is the
   independent proof of pre-registration in the ship evidence.
3. The first `field record` seals the cycle: it sets `cycle_started_at` and
   writes `cycle.lock.json` (`apiforge/field-cycle-identity/v1`) with sha256
   of the corpus (without `cycle_started_at`), the LF-normalized hypothesis,
   the gate, the task set and the repo set, plus `git_commit` when available.
   Commit the lock with the next run. From then on every `field` command
   recomputes the identity; any edit, a moved `cycle_started_at` or a missing
   lock is refused with `AF-FIELD-CYCLE-MUTATED` (`field=cycle.<component>`).
   There is no unlock command: restore the sealed commit or start a new cycle
   with a new corpus. The lock is tamper-evident, not tamper-proof — a
   consistent rewrite of corpus and lock is visible only in git history.
4. Scenarios: `maintenance`, `evolution`, `security`, `multi_repo`,
   `incident`, `performance` — at least 5 tasks each, at least 3 repos.

## Per task

```text
apiforge field record   --task T001 --run <run_id> [--run ...] --phase baseline \
                        --started 2026-10-02T10:00:00Z --ended 2026-10-02T10:30:00Z \
                        --executor agent:api-orchestrator
apiforge field annotate --task T001 --completed --exit-reason graph_gap \
                        --manual-context --no-human-intervention \
                        --false-positives 0 --false-negatives 1
apiforge field verify   --task T001 --verdict agree|disagree|unresolved \
                        --verifier human:sha256:<64 hex>
```

- `record` joins the economy ledger, `summary.json` and
  `economy_checkpoint.json` of the linked runs. Missing sources stay `null`
  with a reason in `unresolved`; nothing is estimated.
- `--started/--ended` are wall-clock task bounds, human time included; every
  linked checkpoint must fall inside them (±60s).
- `exit_reason`: `knowledge_gap | capability_gap | context_gap | graph_gap |
  tool_gap | ux_gap | evaluation_gap | integration_gap | none`.
- Actors are `agent:<roster-name>` or `human:sha256:<64 hex>`; raw human
  names are refused with `AF-FIELD-ACTOR-INVALID`.
- The verifier (`api-verifier` or a human other than the
  executor) judges against `ground_truth` **without** seeing the human
  labels. `verify` never prints them. A verifier equal to the executor is
  refused with `AF-FIELD-VERIFIER-NOT-INDEPENDENT`.
- `verify` stores a `VerificationReceipt` bound to a digest of the task,
  phase, run ids, executor and human labels. Any later `annotate` or
  re-`record` that changes them makes the receipt `stale`: the run leaves the
  verified counts and appears under `stale_runs` until it is verified again.

## Cycle end

`field report` derives `cycle_status` from `coverage_gate`:

| status | condition | H1 / recommendation |
|---|---|---|
| `collecting` | some scenario has fewer than `min_tasks_per_scenario` agreed runs, inside the timebox | `h1_verdict=inconclusive`; "continue collecting" |
| `ready` | every scenario covered, `runs_total ≤ max_runs` (40) and before `cycle_started_at + max_weeks` (4) | `h1_verdict` decided; ≤2 follow-up SDDs |
| `expired` | not ready and `runs_total ≥ max_runs` or deadline passed | `inconclusive`; extend the corpus, open no feature |

`provisional_h1` always shows the verdict the current data would give, so
progress is visible without being actionable. After `expired`, `field record`
is refused with `AF-FIELD-CYCLE-EXPIRED`; a ready cycle at `max_runs` refuses
new baseline records but allows re-recording existing ones.

```text
apiforge field report            # Wilson 95% CI, qualified themes, H1 verdict
apiforge field report --ab       # after the A/B phase
apiforge field export            # anonymized verified tasks -> evals/corpus/field/
```

A theme qualifies with ≥5 verified tasks across ≥2 distinct repos. At most
two qualified themes become follow-up SDDs; none → `inconclusive`, extend the
corpus. `api-adversarial-critic` reviews the report before any SDD opens.

## A/B phase (inference track)

Re-run every `multi_repo` task with inference and record it as `ab_on`:

```text
apiforge workspace graph --infer --run-id <run_id>
apiforge field record --task T010 --run <run_id> --phase ab_on --started .. --ended ..
```

`--infer` appends a `workspace.infer` ledger row; a baseline record whose runs
contain that row is refused with `AF-FIELD-FLAG-CONTAMINATION`.

Inference quality gate on the OpenTelemetry Demo: precision ≥ 0.80 and
recall ≥ 0.60 against `ground-truth/otel-demo-relations.yaml`, pinned to a
commit before inference is tuned.
