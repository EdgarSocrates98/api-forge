"""Tool authorization: risk profiles + allowlist-first permission sets (§13).

The primitive is deliberately offline and deterministic — `authorize()` is
the control-plane decision an orchestrator makes before invoking a tool on
behalf of an agent role. Default is DENY.
"""

from __future__ import annotations

from collections.abc import Collection
from pathlib import Path
from typing import Any, cast

import yaml

from apiforge.contracts.trust import (
    AgentPermissionSet,
    ToolAuthorization,
    ToolRiskProfile,
)

TOOL_RISK_FILE = Path(__file__).resolve().parents[1] / "rules" / "tool_risk.yaml"


def load_tool_risk(
    path: Path = TOOL_RISK_FILE,
) -> tuple[dict[str, ToolRiskProfile], dict[str, AgentPermissionSet]]:
    """Parse rules/tool_risk.yaml into profiles and permission sets."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    profiles = {
        name: ToolRiskProfile(
            tool=name,
            risk_classes=tuple(cast(Any, spec.get("risk_classes", ()))),
            reversible=bool(spec.get("reversible", True)),
            notes=str(spec.get("notes", "")),
        )
        for name, spec in (raw.get("tools") or {}).items()
    }
    permissions = {
        name: AgentPermissionSet(
            subject=name,
            allowed_tools=tuple(spec.get("allowed_tools", ())),
            allowed_risk_classes=tuple(spec.get("allowed_risk_classes", ())),
            denied_tools=tuple(spec.get("denied_tools", ())),
            allowed_targets=tuple(spec.get("allowed_targets", ())),
            delegates_to=tuple(spec.get("delegates_to", ())),
            notes=str(spec.get("notes", "")),
        )
        for name, spec in (raw.get("permissions") or {}).items()
    }
    return profiles, permissions


def authorize(
    subject: str,
    tool: str,
    *,
    profiles: dict[str, ToolRiskProfile],
    permissions: dict[str, AgentPermissionSet],
    delegated_from: str | None = None,
    delegated_scope: tuple[str, ...] = (),
    target: bool = False,
    known_targets: Collection[str] = (),
) -> ToolAuthorization:
    """Decide whether `subject` may invoke `tool`. Every refusal carries an
    AF code, the denied field and a safe unlock — never a silent block."""
    if target:
        if tool not in known_targets:
            return ToolAuthorization(
                subject=subject,
                tool=tool,
                decision="deny",
                code="AF-MCP-TOOL-UNKNOWN",
                field="target",
                unlock="select a target returned by the declared MCP registry",
                reason=f"target tool {tool!r} is not present in the MCP registry",
            )
        grants = permissions.get(subject)
        if grants is None or "*" not in grants.allowed_targets:
            return ToolAuthorization(
                subject=subject,
                tool=tool,
                decision="deny",
                risk_classes=("read_only",),
                code="AF-TOOL-AUTHZ-DENIED",
                field="target",
                unlock="declare the target in the effective role permission set",
                reason=f"target {tool!r} is not allowlisted for {subject!r}",
            )
        return ToolAuthorization(
            subject=subject,
            tool=tool,
            decision="allow",
            risk_classes=("read_only",),
            reason="target is present in the registry and allowlisted for the role",
        )
    profile = profiles.get(tool)
    if profile is None:
        return ToolAuthorization(
            subject=subject,
            tool=tool,
            decision="deny",
            code="AF-TOOL-PROFILE-MISSING",
            field="tool",
            unlock="declare a risk profile for the tool in rules/tool_risk.yaml",
            reason=f"no risk profile declared for {tool!r}",
        )
    grants = permissions.get(subject)
    if grants is None:
        return ToolAuthorization(
            subject=subject,
            tool=tool,
            decision="deny",
            risk_classes=profile.risk_classes,
            code="AF-TOOL-AUTHZ-DENIED",
            field="subject",
            unlock="declare a permission set for the role in rules/tool_risk.yaml",
            reason=f"no permission set declared for {subject!r}",
        )
    if delegated_from is not None:
        delegator = permissions.get(delegated_from)
        if delegator is None or subject not in delegator.delegates_to:
            return ToolAuthorization(
                subject=subject,
                tool=tool,
                decision="deny",
                risk_classes=profile.risk_classes,
                code="AF-TOOL-AUTHZ-DENIED",
                field="delegated_from",
                unlock="declare an explicit delegation from the original authority",
                reason=f"{delegated_from!r} may not delegate authority to {subject!r}",
            )
        if delegated_scope and tool not in delegated_scope:
            return ToolAuthorization(
                subject=subject,
                tool=tool,
                decision="deny",
                risk_classes=profile.risk_classes,
                code="AF-TOOL-AUTHZ-DENIED",
                field="delegated_scope",
                unlock="request only tools inside the delegated scope",
                reason=f"{tool!r} is outside the delegated scope",
            )
    if tool in grants.denied_tools:
        return ToolAuthorization(
            subject=subject,
            tool=tool,
            decision="deny",
            risk_classes=profile.risk_classes,
            code="AF-TOOL-DENIED",
            field="tool",
            unlock="have a human remove the tool from the role's denied_tools",
            reason=f"{tool!r} is explicitly denied for {subject!r}",
        )
    if tool not in grants.allowed_tools:
        return ToolAuthorization(
            subject=subject,
            tool=tool,
            decision="deny",
            risk_classes=profile.risk_classes,
            code="AF-TOOL-AUTHZ-DENIED",
            field="tool",
            unlock="have a human add the tool to the role's allowed_tools",
            reason=f"{tool!r} is not allowlisted for {subject!r}",
        )
    blocked = sorted(set(profile.risk_classes) - set(grants.allowed_risk_classes))
    if blocked:
        return ToolAuthorization(
            subject=subject,
            tool=tool,
            decision="deny",
            risk_classes=profile.risk_classes,
            code="AF-TOOL-RISK-DENIED",
            field="risk_classes",
            unlock="have a human widen allowed_risk_classes or pick a safer tool",
            reason=f"{tool!r} carries risk classes outside the grant: {blocked}",
        )
    return ToolAuthorization(
        subject=subject,
        tool=tool,
        decision="allow",
        risk_classes=profile.risk_classes,
        reason="tool and risk classes inside the role's grant",
    )


__all__ = ["TOOL_RISK_FILE", "authorize", "load_tool_risk"]
