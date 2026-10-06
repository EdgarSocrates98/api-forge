# security-adversarial corpus

§25 synthesized attacks against the platform's own defense surfaces —
`memory_gate` (evaluate_gates), `memory_conflict` (real store: conflicting
trusted records under destructive-risk queries must quarantine, never
prefer), `tool_authorize` (allowlist-first authz, including
`delegated_from`/`delegated_scope` confused-deputy checks and
`target`/`known_targets` MCP dynamic-target risk resolution),
`trust_propagate` (taint/authority propagation) and `data_promotion`
(data-is-not-instruction). All local, no external calls. A case passes
when the observed defense verdict (`refused`/`contained`/`escaped`)
matches `expect.verdict` and `expect.code` (when declared).

Attack classes covered: authority forgery, confused deputy (undeclared
delegation, delegated-scope escape), cross-agent injection, evidence-free
persist, instruction laundering (model output → instruction), MCP dynamic
target escalation (risk-class escape, unknown target), memory conflict
destructive action, memory poisoning, privilege escalation, scope
violation, tainted tool output → agent, tool output injection, trust
laundering, unknown tool.
