from __future__ import annotations

from pathlib import Path

import pytest

from apiforge.contracts.base import ContractError
from apiforge.integrations.devin import build_devin_declaration, build_devin_payload


def test_cli_planning_payload_is_read_only_and_routed() -> None:
    payload = build_devin_payload(
        objective="Map the next safe slice",
        surface="cli",
        task_kind="planning",
    )

    assert payload.launch.executable == "devin"
    assert payload.launch.slash_commands == ("/plan",)
    assert payload.permission_mode == "normal"
    assert payload.evidence_level == "declared"
    assert any(check.name == "routing" for check in payload.checks)
    assert "force-push" in " ".join(payload.prohibited_actions)


def test_desktop_payload_uses_desktop_paste_boundary() -> None:
    payload = build_devin_payload(
        objective="Review the API contract",
        surface="desktop",
        task_kind="review",
        root=Path("workspace"),
    )

    assert payload.launch.executable == "Devin Desktop"
    assert payload.launch.prompt_transport == "desktop-paste"
    assert payload.working_directory == "workspace"
    assert payload.launch.slash_commands == ("/plan",)


def test_cloud_handoff_payload_is_explicitly_human_reviewed() -> None:
    payload = build_devin_payload(
        objective="Continue the approved work in Cloud",
        surface="cloud",
        task_kind="handoff",
    )

    assert payload.launch.args == ("--cloud",)
    assert payload.launch.slash_commands == ("/handoff",)
    assert payload.requires_human_confirmation
    assert "CI green-validation" in payload.prompt


def test_native_windows_sandbox_is_refused() -> None:
    with pytest.raises(ContractError, match="AF-DEVIN-SANDBOX-UNAVAILABLE"):
        build_devin_payload(
            objective="Run unattended checks",
            surface="cli",
            task_kind="verification",
            sandbox=True,
            platform="windows",
        )


def test_empty_objective_is_refused() -> None:
    with pytest.raises(ContractError, match="AF-DEVIN-OBJECTIVE"):
        build_devin_payload(objective="   ")


def test_devin_declaration_keeps_product_claims_declared() -> None:
    declaration = build_devin_declaration()

    assert declaration.host == "devin"
    assert declaration.evidence_level == "declared"
    desktop = next(item for item in declaration.capabilities if item.capability == "devin-desktop")
    assert desktop.evidence_level == "declared"
