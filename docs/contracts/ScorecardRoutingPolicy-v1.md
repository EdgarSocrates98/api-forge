# ScorecardRoutingPolicy/v1

Local, versioned policy for determining whether scorecard history is trusted
as champion evidence and how many eligible challengers receive a bounded
routing opportunity.

| Field | Meaning |
|---|---|
| `policy_version` | Replay identity for the adaptive policy |
| `min_evaluations` | Minimum scorecard history for champion eligibility |
| `min_quality_score` | Minimum promoted quality value for champion eligibility |
| `challenger_slots` | Maximum selected challenger candidates |
| `require_quality_promoted` | Requires the existing evidence-gated promotion flag |
| `stale_behavior` | Explicit stale/unresolved handling; MVP permits `unresolved` |

The policy is read-only configuration. It cannot execute shadow work, authorize
external mutation or bypass the risk/complexity assessment and existing
fallback bounds.
