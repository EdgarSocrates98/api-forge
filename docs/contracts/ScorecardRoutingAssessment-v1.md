# ScorecardRoutingAssessment/v1

Canonical, read-only assessment of how local scorecard history affects one
routing decision. The assessment does not execute a challenger, promote an
implementation or call an external provider.

| Field | Meaning |
|---|---|
| `assessment_id` | Stable hash of the policy and canonical candidate lane data |
| `policy_version` | Local scorecard adaptation policy identity |
| `candidates` | Per-candidate lane, freshness, quality, evidence and gaps |
| `champion_order` | Eligible candidates with fresh promoted history, in inherited objective order |
| `challenger_order` | Eligible candidates without champion evidence, in inherited objective order |
| `unresolved_order` | Candidates whose history is stale, unresolved or otherwise not safe for promotion |
| `ordered_candidates` | Champion-first, bounded-challenger, then remaining deterministic order |
| `selected_challengers` | The policy-bounded challenge opportunity |
| `challenger_slots` | Maximum selected challenger count |
| `evidence` / `unresolved` | Scorecard provenance and unresolved diagnostics retained end-to-end |

Champion eligibility requires an eligible candidate, fresh scorecard history,
quality promotion, the configured minimum evaluation history and the configured
quality threshold. Missing or unpromoted history is a challenger signal. Stale
or unresolved history remains visible but cannot become champion evidence.

The contract is frozen, versioned and local. It preserves the static routing
fallback and cannot authorize external mutation.
