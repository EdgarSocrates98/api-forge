# Economy-routing corpus

Fifteen cases: five TaskSpec shapes × three requested profiles.

| Shape | Risk | Size | Risk floor | Minimum roles |
|---|---|---|---|---|
| small | read_only | S | economy | reviewer |
| moderate | read_only | M | economy | reviewer |
| complex | read_only | L | balanced | critic, reviewer |
| sensitive | sensitive | M | balanced | critic, reviewer |
| critical | irreversible | S | deep | critic, referee, reviewer |

Each case compares the pre-economy routing plan and fake-adapter run
(`economy_enabled=False`) with the requested profile. The baseline is computed
live from the same code path, so it cannot drift from current behavior.

Gates:

- **role_invariant** — every reviewer/critic/referee kind in the pre-economy
  plan is still present, and the plan's minimum roles match the ground truth;
- **effective_profile** — effective profile equals `max(requested, floor)`;
- **critical_is_deep** — critical shapes are `deep` for every requested profile;
- **economy_cheaper_low_risk** — for small/moderate with `economy`, fanout is
  strictly lower and calls are not higher than the baseline.

Critical TaskSpecs are refused by runtime review before routing; their call
counts are reported as `review-blocked`, never estimated.

```text
apiforge evals economy-routing   # exit 1 when a gate fails
```
