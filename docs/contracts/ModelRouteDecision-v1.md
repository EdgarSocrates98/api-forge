# ModelRouteDecision/v1

§33 the routing answer — `routing_kind: model` keeps it apart from the
capability and agent planes.

| Field | Meaning |
|---|---|
| `selected` | `"provider/model"` of the top eligible candidate, or `null` |
| `ranked` | Every candidate: `eligible`, weighted `score`, and `reasons` (constraint refusals or `scorecard-missing`) |
| `code` | `AF-ROUTE-NO-ELIGIBLE-MODEL` when nothing survives |
| `unresolved` | Input signals never supplied |

Score = declared weighted mean over quality history, latency, cost and
availability; terms never observed are dropped, not zeroed.

When `task_class` is declared, only scorecards for that class contribute.
Missing scorecards remain an unresolved signal and do not become a fabricated
quality value. `route_model_shadow` records candidate-vs-legacy output through
the Decision Control Plane; shadow mode always returns `governing=legacy`.
