# MCP Tool-Risk Inventory

Canonical inventory for dynamic MCP target authorization (final-runtime
convergence, Phase 7). Generated from `src/apiforge/rules/tool_risk.yaml`
crossed with the gateway registry (`apiforge.mcp.gateway.full_tools()`:
TOOLS + OBSERVABILITY_TOOLS + GRPC_TOOLS + MIGRATION_TOOLS).

## Authorization contract

A dynamic `apiforge_call(target)` dispatch is authorized only when **all**
of the following hold:

1. the calling subject carries `apiforge_call` in `allowed_tools`
   (gateway permission — checked separately);
2. the target is present in the declared registry (`known_targets`);
3. a `ToolRiskProfile` exists for the target — **unknown profile denies
   closed** with `AF-TOOL-PROFILE-MISSING`;
4. the target is not in the subject's `denied_tools` (`AF-TOOL-DENIED`);
5. the target is allowlisted for the subject, by name or `allowed_targets=["*"]`
   (`AF-TOOL-AUTHZ-DENIED`) — the wildcard is a **name** grant only;
6. every risk class of the target's real profile is inside the subject's
   `allowed_risk_classes` (`AF-TOOL-RISK-DENIED`).

On allow, the returned `ToolAuthorization.risk_classes` reports the
target's real profile — targets are never auto-classified as read-only.

The default `mcp-gateway` permission grants `allowed_targets=["*"]` with
`allowed_risk_classes=[read_only]`: every read-only target below dispatches,
every `write`/`security_impact`/`external_side_effect` target denies.
Elevated dispatch requires an explicit role with a declared risk grant.

## Matrix

tool | risk classes | reversible | domain gate | MCP exposed
--- | --- | --- | --- | ---
| agent_span_append | write | yes | core | yes |
| agent_span_query | read_only | yes | core | yes |
| agentops_compare | read_only | yes | core | yes |
| agentops_inspect | read_only | yes | core | yes |
| agentops_projection | read_only | yes | core | yes |
| agentops_timeline | read_only | yes | core | yes |
| agentops_waste | read_only | yes | core | yes |
| agents_audit | read_only | yes | core | yes |
| analyze | write | yes | core | yes |
| autonomy_status | read_only | yes | core | yes |
| blackboard_append | write | yes | core | yes |
| blackboard_query | read_only | yes | core | yes |
| brief_show | read_only | yes | core | yes |
| budget_check | read_only | yes | core | yes |
| budget_plan | write | yes | core | yes |
| budget_spend | write | yes | core | yes |
| cache_invalidate | write | yes | core | yes |
| cache_stats | read_only | yes | core | yes |
| capabilities_list | read_only | yes | core | yes |
| capabilities_verify | read_only | yes | core | yes |
| change_control_collect | read_only, external_side_effect | yes | core | yes |
| change_control_publish | write | yes | core | yes |
| change_control_run | read_only | yes | core | yes |
| change_control_surface | read_only | yes | core | yes |
| context_capsule | read_only | yes | core | yes |
| context_delta | read_only | yes | core | yes |
| context_expand | read_only | yes | core | yes |
| context_funnel | read_only | yes | core | yes |
| context_gc | write | yes | core | yes |
| context_resolve | read_only | yes | core | yes |
| contract_list | read_only | yes | core | yes |
| contract_show | read_only | yes | core | yes |
| control_routes | read_only | yes | core | yes |
| control_shadow | read_only | yes | core | yes |
| control_triggers | read_only | yes | core | yes |
| debate_packet | read_only | yes | core | yes |
| decision_check | read_only, security_impact | yes | core | yes |
| diff_contract | read_only | yes | core | yes |
| discover | read_only | yes | core | yes |
| economy_doctor | read_only | yes | core | yes |
| economy_explain | read_only | yes | core | yes |
| economy_ledger | read_only | yes | core | yes |
| economy_phase_budget | read_only | yes | core | yes |
| economy_pricing | read_only | yes | core | yes |
| economy_reconcile | read_only | yes | core | yes |
| economy_report | read_only | yes | core | yes |
| economy_roi | read_only | yes | core | yes |
| economy_stats | read_only | yes | core | yes |
| economy_tier | read_only | yes | core | yes |
| evals_agentic_quality | read_only | yes | core | yes |
| evals_economy_hardening | read_only | yes | core | yes |
| evals_gate | read_only | yes | core | yes |
| evals_replay | read_only | yes | core | yes |
| evidence_gate | read_only, security_impact | yes | core | yes |
| evidence_resolve | read_only | yes | core | yes |
| field_annotate | write | yes | core | yes |
| field_record | write | yes | core | yes |
| field_report | read_only | yes | core | yes |
| field_verify | write, security_impact | yes | core | yes |
| forge_capabilities | read_only | yes | core | yes |
| forge_evidence | read_only | yes | core | yes |
| forge_health | read_only | yes | core | yes |
| forge_inspect | read_only | yes | core | yes |
| forge_result | read_only | yes | core | yes |
| governor_decide | read_only | yes | core | yes |
| governor_recover | read_only | yes | core | yes |
| governor_stop | read_only | yes | core | yes |
| graph_coverage | read_only | yes | core | yes |
| graph_impact | read_only | yes | core | yes |
| graph_query | read_only | yes | core | yes |
| graph_trace | read_only | yes | core | yes |
| grpc_analyze | read_only | yes | grpc | yes |
| grpc_benchmark | read_only | yes | grpc | yes |
| grpc_capabilities | read_only | yes | grpc | yes |
| grpc_codegen | read_only | yes | grpc | yes |
| grpc_diff | read_only | yes | grpc | yes |
| grpc_gateway | read_only | yes | grpc | yes |
| grpc_verify | read_only | yes | grpc | yes |
| index_status | read_only | yes | core | yes |
| integration_github_issues | read_only, external_side_effect | yes | core | yes |
| integration_health | read_only, external_side_effect | yes | core | yes |
| integration_json | read_only, external_side_effect | yes | core | yes |
| judge | read_only | yes | core | yes |
| knowledge_adaptive | read_only | yes | core | yes |
| knowledge_check | read_only | yes | core | yes |
| knowledge_drift | read_only | yes | core | yes |
| knowledge_impact | read_only | yes | core | yes |
| knowledge_list | read_only | yes | core | yes |
| knowledge_search | read_only | yes | core | yes |
| knowledge_select | read_only | yes | core | yes |
| knowledge_show | read_only | yes | core | yes |
| knowledge_watch | read_only | yes | core | yes |
| lab_scenarios | read_only | yes | core | yes |
| mcp_audit | read_only | yes | core | yes |
| mcp_benchmark | read_only | yes | core | yes |
| mcp_disclose | read_only | yes | core | yes |
| mcp_surface | read_only | yes | core | yes |
| memory_persist | write, security_impact | yes | core | yes |
| memory_propose | write | yes | core | yes |
| memory_quarantine_list | read_only | yes | core | yes |
| memory_quarantine_resolve | write, security_impact | yes | core | yes |
| memory_rank | read_only | yes | core | yes |
| memory_search | read_only | yes | core | yes |
| migration_analyze | read_only | yes | migration | yes |
| migration_plan | write | yes | migration | yes |
| migration_verify | write | yes | migration | yes |
| model_api_gateway | read_only | yes | core | yes |
| model_build | read_only | yes | core | yes |
| model_dump | read_only | yes | core | yes |
| model_otel | read_only | yes | core | yes |
| model_redis | read_only | yes | core | yes |
| model_resilience | read_only | yes | core | yes |
| next_step | read_only | yes | core | yes |
| observability_capabilities | read_only | yes | observability | yes |
| observability_ingest | read_only | yes | observability | yes |
| perf_chaos | read_only | yes | core | yes |
| perf_compare | read_only | yes | core | yes |
| perf_memory_search | read_only | yes | core | yes |
| perf_scenario | read_only | yes | core | yes |
| perf_suggest | read_only | yes | core | yes |
| perf_verdict | read_only | yes | core | yes |
| plan_architecture | read_only | yes | core | yes |
| platform_verify_runtime | write | yes | core | yes |
| playbook | read_only | yes | core | yes |
| portable_doctor | read_only | yes | core | yes |
| portable_init | write | yes | core | yes |
| portable_inspect | read_only | yes | core | yes |
| portable_status | read_only | yes | core | yes |
| route_model | read_only | yes | core | yes |
| rules_list | read_only | yes | core | yes |
| rules_lookup | read_only | yes | core | yes |
| run_list | read_only | yes | core | yes |
| runtime_approve | write, security_impact | yes | core | yes |
| runtime_checkpoint | read_only | yes | core | yes |
| runtime_debate | write | yes | core | yes |
| runtime_resume | write | yes | core | yes |
| runtime_run | write | yes | core | yes |
| runtime_status | read_only | yes | core | yes |
| slice_log | read_only | yes | core | yes |
| slice_tests | read_only | yes | core | yes |
| task_compile | write | yes | core | yes |
| task_plan | write | yes | core | yes |
| task_status | read_only | yes | core | yes |
| task_verify | write, security_impact | yes | core | yes |
| telemetry_export | read_only | yes | core | yes |
| telemetry_validate | read_only | yes | core | yes |
| verify_escalate | read_only | yes | core | yes |
| verify_plan | read_only | yes | core | yes |
| workspace_add | write | yes | core | yes |
| workspace_discover | read_only | yes | core | yes |
| workspace_graph | read_only | yes | core | yes |
| workspace_status | read_only | yes | core | yes |
