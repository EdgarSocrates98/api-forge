"""Tool authorization: risk profiles + allowlist-first permission sets (§13).

The primitive is deliberately offline and deterministic — `authorize()` is
the control-plane decision an orchestrator makes before invoking a tool on
behalf of an agent role. Default is DENY.
"""

from __future__ import annotations

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
) -> ToolAuthorization:
    """Decide whether `subject` may invoke `tool`. Every refusal carries an
    AF code, the denied field and a safe unlock — never a silent block."""
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
