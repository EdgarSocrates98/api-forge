# Field validation — pre-registered hypothesis

Registered before the first field run. Changing this file after
`cycle_started_at` is set in `corpus.yaml` invalidates the cycle.

## H1

The most frequent reason users leave the API Forge flow on real repositories
is a **graph gap**: API Forge does not know how services, operations and events
relate across repositories, so the user explains it by hand
(`exit_reason: graph_gap`, usually with `manual_context_required: true`).

## Refutation

H1 is **refuted** when, over verified baseline runs, `graph_gap` does not
qualify (≥5 tasks across ≥2 distinct repos) while another `exit_reason` does,
or when `graph_gap` qualifies but another qualified theme is more frequent.

H1 is **inconclusive** when no theme qualifies. The action is to extend the
corpus; no new feature opens.

## Competing expectations recorded up front

- `context_gap` — right knowledge exists but the wrong context was loaded.
- `integration_gap` — runtime telemetry (traces/metrics/logs) is not
  connected to code, i.e. the Contract-to-Runtime bet.
- `ux_gap` — capability exists but was not discoverable.

## Isolation

Baseline runs never use `workspace graph --infer`. The inference track is
compared only in the A/B phase (`--phase ab_on`) over multi-repo tasks.
