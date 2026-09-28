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
3. Scenarios: `maintenance`, `evolution`, `security`, `multi_repo`,
   `incident`, `performance` — at least 5 tasks each, at least 3 repos.

## Per task

```text
apiforge field record   --task T001 --run <run_id> [--run ...] --phase baseline \
                        --started 2026-10-02T10:00:00Z --ended 2026-10-02T10:30:00Z
apiforge field annotate --task T001 --completed --exit-reason graph_gap \
                        --manual-context --no-human-intervention \
                        --false-positives 0 --false-negatives 1
apiforge field verify   --task T001 --verdict agree|disagree|unresolved
```

- `record` joins the economy ledger, `summary.json` and
  `economy_checkpoint.json` of the linked runs. Missing sources stay `null`
  with a reason in `unresolved`; nothing is estimated.
- `--started/--ended` are wall-clock task bounds, human time included; every
  linked checkpoint must fall inside them (±60s).
- `exit_reason`: `knowledge_gap | capability_gap | context_gap | graph_gap |
  tool_gap | ux_gap | evaluation_gap | integration_gap | none`.
- The verifier (`api-verification-engineer` or a human other than the
  executor) judges against `ground_truth` **without** seeing the human
  labels. `verify` never prints them.

## Cycle end

Stop at `gate.max_runs` (30) or `gate.max_weeks` (4), whichever comes first.

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
