# RoutingDecision/v1

Persisted deterministic routing trace containing candidate assessments, the
optional canonical `RiskComplexityAssessment/v1`, the optional canonical
`GraphImpactAssessment/v1`, the optional canonical
`ScorecardRoutingAssessment/v1`, optional canonical
`ScorecardShadowEvaluation/v1`, selected capability, fallback order, evidence
and unresolved gaps.

The assessment is computed once before ranking. Its objective order controls
ranking, while its verification depth and required roles are consumed by plan
construction. Scorecard lane assignment is computed once and persisted inside
the decision. Runtime, CLI/TUI and governance projections read this persisted
decision; they do not reclassify the task or scorecard history. The shadow
evaluation compares the static and adaptive proposals without executing either
capability.

When graph inputs are present, the same stored graph assessment supplies the
additive gate effect and explicit candidate preference. A graph match cannot
make an otherwise ineligible capability eligible; an unmapped or unresolved
candidate retains the static A/B order and remains visible as unresolved.
