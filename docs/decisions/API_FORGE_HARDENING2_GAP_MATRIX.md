# API Forge — Runtime Convergence Hardening II Gap Matrix

Baseline: `docs/decisions/API_FORGE_HARDENING2_BASELINE.md`

| Concern | Exists | Runtime integrated | Governing now | Observed baseline | Classification | Wave action |
|---|---:|---:|---:|---:|---|---|
| Governor / gain / stop | yes | partial | partial | yes | INTEGRATE | preserve current planes; make receipts and stop/recovery precedence explicit |
| Recovery | yes | partial | no | post-flight | FIX | classify before retry; scheduler executes only an authorized action |
| Loop detection | yes | no | no | current-only | FIX | persist bounded strategy history and enforce policy in execution |
| Model router | yes | shadow/plan | no | eval regression | CONVERGE | task-class scorecards, shadow route receipt, no active promotion |
| Decision control plane | yes | partial | partial | yes | CONVERGE | canonicalize promotion/demotion/fallback ownership |
| Tool authorization | yes | gateway/adapter | partial | yes | HARDEN | role/effective-authority context and target-tool authorization |
| Trust / taint | yes | data paths partial | partial | yes | HARDEN | preserve data-only taint through context admission and promotion |
| Token ledger / AgentOps | yes | partial | partial | regression | FIX | unresolved/partial token coverage; calls remain correlated by `model_call_id` |
| Context quality | yes | yes | yes | pass with unresolved metrics | KEEP + EXTEND | separate recall from utilization and preserve missing required evidence |
| Adaptive retrieval | yes | yes | partial | pass but graph/sufficiency gap | FIX | explicit per-level score basis and graph contribution |
| Memory | yes | yes | partial | `9/9` local evals | HARDEN | freshness, runtime matching and conflicts remain policy-driven |
| AgentOps | yes | yes | partial | one regression | EXTEND | coverage/timeline/waste outputs without zero-filling |
| MCP | yes | static/legacy | partial | audit pass | HARDEN | modern discovery/list/call proof and target auth boundary |
| Forge Protocol | yes | yes | yes | local contract | KEEP | preserve v1; A2A remains adapter-only |
| Lab | yes | fixtures + proofs | partial | `13/13` catalog | EXTEND | executable runtime-convergence scenarios, local-only claims |
| Supply chain / CI | yes | yes | partial | local gates pass | KEEP + EXTEND | local release receipt; CI failures stay correctly classified |

The default strategy is `adapter -> shadow -> assisted -> active -> retire`.
No new runtime or kernel is introduced, and no external capability is
promoted from a fixture or static probe.

