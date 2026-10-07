# PromotionDecision/v1

The answer to "may this route move one lifecycle step?" — never skips a
stage.

| Field | Meaning |
|---|---|
| `from_mode` / `to_mode` | The single step attempted |
| `allowed` | Whether the transition was applied to the modes overlay |
| `missing` | §31 requirements that were not met |
| `code` | `AF-GOV-PROMOTION-INCOMPLETE`, `AF-GOV-PROMOTION-NOT-APPROVED`, `AF-GOV-MODE-TRANSITION-INVALID` |

Promoting an already-active route refuses `AF-GOV-MODE-TRANSITION-INVALID`.
