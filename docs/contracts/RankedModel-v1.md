# RankedModel/v1

One entry inside `ModelRouteDecision.ranked`.

| Field | Meaning |
|---|---|
| `provider` / `model` | Identity |
| `eligible` | `false` when a hard constraint or a scorecard rule refused it |
| `score` | Weighted score `0..1`, or `null` when nothing measurable existed |
| `reasons` | Every refusal (`reasoning-tier-insufficient`, `quality-below-floor`, `insufficient-evaluations`, …) or `scorecard-missing` |
