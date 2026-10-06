"""Tool authorization (§13): declared risk + allowlist-first, default deny."""

from __future__ import annotations

from apiforge.trust.tools import authorize, load_tool_risk


def _grants():
    profiles, permissions = load_tool_risk()
    return profiles, permissions


def test_every_registry_runner_has_a_risk_profile() -> None:
    from apiforge.run_tools import TOOLS

    profiles, _ = _grants()
    missing = [name for name in TOOLS if name not in profiles]
    assert missing == []


def test_default_deny_when_tool_or_subject_unknown() -> None:
    profiles, permissions = _grants()
    unknown_tool = authorize("reviewer", "shady-tool", profiles=profiles, permissions=permissions)
    assert unknown_tool.decision == "deny"
    assert unknown_tool.code == "AF-TOOL-PROFILE-MISSING"

    unknown_subject = authorize(
        "rogue-agent", "semgrep", profiles=profiles, permissions=permissions
    )
    assert unknown_subject.decision == "deny"
    assert unknown_subject.code == "AF-TOOL-AUTHZ-DENIED"


def test_explicit_deny_wins_over_allowlist() -> None:
    profiles, permissions = _grants()
    # critic has semgrep-class tools only; memory_persist is explicitly denied
    decision = authorize("critic", "memory_persist", profiles=profiles, permissions=permissions)
    assert decision.decision == "deny"
    assert decision.code == "AF-TOOL-DENIED"


def test_unlisted_tool_is_denied_even_at_matching_risk() -> None:
    profiles, permissions = _grants()
    # referee allows read_only risk; semgrep is read_only but not allowlisted
    decision = authorize("referee", "semgrep", profiles=profiles, permissions=permissions)
    assert decision.decision == "deny"
    assert decision.code == "AF-TOOL-AUTHZ-DENIED"


def test_risk_class_outside_grant_is_denied() -> None:
    # synthetic grant: tool allowlisted but its risk classes exceed the role's
    from apiforge.contracts.trust import AgentPermissionSet, ToolRiskProfile

    profiles = {
        "k6": ToolRiskProfile(tool="k6", risk_classes=("external_side_effect", "production_impact"))
    }
    permissions = {
        "operator": AgentPermissionSet(
            subject="operator",
            allowed_tools=("k6",),
            allowed_risk_classes=("read_only", "write"),
        )
    }
    decision = authorize("operator", "k6", profiles=profiles, permissions=permissions)
    assert decision.decision == "deny"
    assert decision.code == "AF-TOOL-RISK-DENIED"
    assert decision.field == "risk_classes"


def test_allow_inside_grant() -> None:
    profiles, permissions = _grants()
    decision = authorize("runner", "semgrep", profiles=profiles, permissions=permissions)
    assert decision.decision == "allow"
    assert decision.code is None


def test_every_denial_carries_code_field_unlock() -> None:
    profiles, permissions = _grants()
    for subject, tool in (
        ("rogue", "semgrep"),
        ("critic", "unknown-tool"),
        ("specialist", "k6"),
        ("referee", "blackboard_append"),
    ):
        decision = authorize(subject, tool, profiles=profiles, permissions=permissions)
        assert decision.decision == "deny"
        assert decision.code and decision.field and decision.unlock


def test_delegation_scope_is_fail_closed() -> None:
    profiles, permissions = _grants()
    decision = authorize(
        "reviewer",
        "semgrep",
        profiles=profiles,
        permissions=permissions,
        delegated_from="api-orchestrator",
        delegated_scope=("trivy",),
    )
    assert decision.decision == "deny"
    assert decision.field == "delegated_scope"


def test_mcp_target_requires_registry_and_target_grant() -> None:
    profiles, permissions = _grants()
    allowed = authorize(
        "mcp-gateway",
        "rules_list",
        profiles=profiles,
        permissions=permissions,
        target=True,
        known_targets=("rules_list",),
    )
    assert allowed.decision == "allow"
    unknown = authorize(
        "mcp-gateway",
        "unknown_tool",
        profiles=profiles,
        permissions=permissions,
        target=True,
        known_targets=("rules_list",),
    )
    assert unknown.decision == "deny"
    assert unknown.code == "AF-MCP-TOOL-UNKNOWN"


def test_every_mcp_dispatchable_tool_has_a_risk_profile() -> None:
    from apiforge.mcp.gateway import full_tools

    profiles, _ = _grants()
    missing = [name for name in full_tools() if name not in profiles]
    assert missing == []


def test_mcp_target_wildcard_does_not_bypass_risk_classes() -> None:
    # §43: allowed_targets=["*"] is a name grant, never a risk grant —
    # a write/security target still denies for the read-only gateway role.
    profiles, permissions = _grants()
    for write_target in ("memory_persist", "runtime_run", "budget_spend"):
        decision = authorize(
            "mcp-gateway",
            write_target,
            profiles=profiles,
            permissions=permissions,
            target=True,
            known_targets=(write_target,),
        )
        assert decision.decision == "deny", write_target
        assert decision.code == "AF-TOOL-RISK-DENIED"
        assert decision.field == "risk_classes"
        assert "read_only" not in decision.risk_classes


def test_mcp_target_allowed_reports_real_profile() -> None:
    profiles, permissions = _grants()
    decision = authorize(
        "mcp-gateway",
        "rules_list",
        profiles=profiles,
        permissions=permissions,
        target=True,
        known_targets=("rules_list",),
    )
    assert decision.decision == "allow"
    assert decision.risk_classes == profiles["rules_list"].risk_classes


def test_mcp_target_registered_but_unprofiled_denies() -> None:
    # fail-closed: registry presence without a declared profile denies.
    profiles, permissions = _grants()
    decision = authorize(
        "mcp-gateway",
        "undeclared_target",
        profiles=profiles,
        permissions=permissions,
        target=True,
        known_targets=("undeclared_target",),
    )
    assert decision.decision == "deny"
    assert decision.code == "AF-TOOL-PROFILE-MISSING"
    assert decision.field == "target"
    assert decision.unlock


def test_mcp_target_specific_grant_is_respected() -> None:
    from apiforge.contracts.trust import AgentPermissionSet

    profiles, permissions = _grants()
    permissions["gateway-elevated"] = AgentPermissionSet(
        subject="gateway-elevated",
        allowed_tools=("apiforge_call",),
        allowed_risk_classes=("read_only", "write"),
        allowed_targets=("workspace_add",),
    )
    allowed = authorize(
        "gateway-elevated",
        "workspace_add",
        profiles=profiles,
        permissions=permissions,
        target=True,
        known_targets=("workspace_add",),
    )
    assert allowed.decision == "allow"
    assert allowed.risk_classes == ("write",)

    # explicit grant for one target never leaks to another write target
    leaked = authorize(
        "gateway-elevated",
        "runtime_run",
        profiles=profiles,
        permissions=permissions,
        target=True,
        known_targets=("runtime_run",),
    )
    assert leaked.decision == "deny"
    assert leaked.code == "AF-TOOL-AUTHZ-DENIED"
    assert leaked.field == "target"


def test_mcp_target_denied_tools_win_over_wildcard() -> None:
    from apiforge.contracts.trust import AgentPermissionSet

    profiles, permissions = _grants()
    permissions["gateway-fenced"] = AgentPermissionSet(
        subject="gateway-fenced",
        allowed_tools=("apiforge_call",),
        allowed_risk_classes=("read_only", "write"),
        allowed_targets=("*",),
        denied_tools=("memory_persist",),
    )
    decision = authorize(
        "gateway-fenced",
        "memory_persist",
        profiles=profiles,
        permissions=permissions,
        target=True,
        known_targets=("memory_persist",),
    )
    assert decision.decision == "deny"
    assert decision.code == "AF-TOOL-DENIED"


def test_mcp_gateway_boundary_and_target_authorization_are_both_required() -> None:
    # a role without apiforge_call in allowed_tools cannot reach dispatch at all
    profiles, permissions = _grants()
    gate = authorize("critic", "apiforge_call", profiles=profiles, permissions=permissions)
    assert gate.decision == "deny"
    # and even a role carrying the gateway tool still needs the target grant
    target = authorize(
        "mcp-gateway",
        "rules_list",
        profiles=profiles,
        permissions=permissions,
        target=True,
        known_targets=("rules_list",),
    )
    assert target.decision == "allow"
