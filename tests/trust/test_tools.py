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
