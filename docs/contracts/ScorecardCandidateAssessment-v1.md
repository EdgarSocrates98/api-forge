# ScorecardCandidateAssessment/v1

Explainable scorecard lane assignment for one candidate in a
`ScorecardRoutingAssessment/v1`.

| Field | Meaning |
|---|---|
| `candidate` | Capability identity being assessed |
| `profile_id` | Local scorecard profile used, when one exists |
| `lane` | `champion`, `challenger` or `unresolved` |
| `eligible` | Existing routing eligibility result |
| `quality_score` | Promoted quality value when available; missing history remains null |
| `evaluation_count` | Scorecard evaluation history used for the decision |
| `freshness_state` | Freshness of the scorecard observations |
| `quality_promoted` | Whether existing evidence gates promoted quality |
| `evidence` / `computed_from` | Scorecard provenance and evaluation refs |
| `gaps` | Scorecard evidence or failed-axis gaps |
| `reason_codes` | Stable explanation for the assigned lane |

`champion` is valid only for an eligible candidate with fresh promoted history.
Missing or unpromoted history is a challenger signal. Stale or unresolved
history remains visible as `unresolved` and cannot authorize champion status.

The contract is frozen, versioned and read-only; it does not execute agents or
promote external state.
