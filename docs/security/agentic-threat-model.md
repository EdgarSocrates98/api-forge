# Agentic Threat Model

Scope: the API Forge agentic runtime — deterministic control plane,
probabilistic agents, governed memory, tool surface, MCP boundary and
the Forge Protocol. This document names the attack classes the platform
defends against, the defense that answers each, and the eval evidence
that proves the defense. It is a threat model, not an audit: claims are
tied to modules and to `evals/corpus/security-adversarial` cases that
run them.

## Prime invariant — data is not instruction

Content arriving from API specs, issues, GitHub, logs, documentation,
web pages, tool output, memory or other agents' responses can never
promote itself to system instruction. Enforced at the contract level:
`TrustUnit.instruction_authority` refuses `!= "none"` for every origin
outside `AUTHORITATIVE_ORIGINS = (system, governed_policy)` — a forged
authority field fails validation, it is never sanitized
(`contracts/trust.py::TrustUnit.authority_requires_authoritative_origin`).

## Trust boundaries (`TrustBoundary`)

`context_capsule`, `memory`, `blackboard`, `knowledge`, `tool_result`,
`mcp_response`, `agent_handoff`, `api_spec`, `external_content`, `log`,
`ci_output`, `documentation`. Every boundary is annotated by
`trust/plane.py::trust_unit` — origin fixes the base trust and the
origin taint set; `external_unit` handles explicitly external content.

## Attack classes and defenses (§11)

| Class | Defense | Evidence |
|---|---|---|
| prompt injection / indirect prompt injection | authority validator + `data_promotion` vector | `tool-output-injection`, `authority-forgery` |
| tool abuse / privilege escalation | allowlist-first `trust/tools.py::authorize` over `rules/tool_risk.yaml` — denied tool, unallowlisted tool, undeclared profile and missing permission set all refuse with AF codes | `privilege-escalation`, `unknown-tool` |
| cross-agent injection | `trust/propagation.py::propagate` — authority collapses to `none` whenever any source lacks it; `system_synthesis` keeps at most the weakest authority | `cross-agent-injection` |
| memory poisoning | `memory/security.py::evaluate_gates` — origin gate rejects `external_untrusted` unless the policy explicitly allows it; low-trust persists are quarantined for human review | `memory-poisoning`, `quarantine-held` (memory-evals) |
| evidence poisoning / trust laundering | propagation lifts trust at most one tier above the weakest source and only under `governed_verification` with evidence refs; `verified` cannot be manufactured | `trust-laundering` |
| context poisoning | taint union across sources; removable taints clear only via governed verification | propagation vectors |
| secret leakage | `AgentSpan.attributes` validator rejects sensitive keys (`AF-OTEL-SENSITIVE-ATTRIBUTE`); memory payloads are frozen JsonValue — no executable content | contract validators |
| data exfiltration | adapters are read-only; external reads emit receipts; no provider SDK imports in `src/` | architecture invariant |
| cross-task contamination | memory scope gate (`AF-MEMORY-SCOPE-DENIED`) + query scope filtering | `scope-violation`, `cross-task-leakage` (memory-evals) |
| confused deputy | tool authorization is per-subject allowlist, not ambient; Forge risk gate requires `--acknowledge-risk` recorded on the task row | `privilege-escalation`, forge gates |
| tool result poisoning | tool output enters context only as tainted `tool_result` origin — never authoritative | `tool-output-injection` |
| malicious artifact / malicious API description | OpenAPI/spec content is `api_spec`/`external_content` boundary data; persistent memory from it needs verified evidence (`AF-MEMORY-EVIDENCE-REQUIRED`) | `evidence-free-persist` |

## Trust propagation rules (§10)

`propagate()` derives a unit from sources under an explicit transform
(`verbatim`, `parse_extract`, `summarize`, `governed_verification`,
`system_synthesis`):

- taint is the union of source taints;
- trust is the weakest source's level — evidence may lift it one tier,
  never above `verified`;
- authority is `none` unless the transform is `system_synthesis` AND no
  source carries `none`;
- derived origin comes from the weakest source — a strong source cannot
  launder a weak one.

## Memory gate pipeline (§14)

`scope → origin → evidence → trust → outcome → freshness`, verdicts
`persist`/`quarantine`/`reject`, all with `AF-MEMORY-*` codes, field and
unlock. Quarantine is an explicit state with `list_quarantine` and
`review_quarantine` — rejected content never reaches the store and
quarantined content is human-resolved, never auto-promoted.

## Tool risk classes (§11)

Every tool profile in `rules/tool_risk.yaml` declares
`read_only`/`write`/`destructive`/`reversible`/`external_side_effect`/
`financial_impact`/`security_impact`/`production_impact` risk classes.
Authorization is allowlist-first per subject; every denial carries
`AF-TOOL-*`, the denied field and a safe unlock.

## Residual risks (explicitly open)

- Model-output correctness is not a security property this model covers —
  recorded-output evals score verdicts, not intent.
- A compromised `rules/tool_risk.yaml` weakens authorization — policy
  files are reviewed artifacts, not runtime input.
- The provider tier of `evals live` is `deferred_external`: live model
  probing (jailbreak suites) is out of scope until a declared adapter +
  human approval exist.
- MCP hosts decide what they load; disclosure advisories cannot hide
  capability (Phase 9 audit: 0 findings, 1 declared exception).
