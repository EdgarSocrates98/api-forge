from pathlib import Path

import pytest

from apiforge.agentops.activation import build_activation_plan


def test_activation_is_plan_only_for_every_host() -> None:
    for host in ("claude", "gpt-codex", "devin", "copilot"):
        plan = build_activation_plan(host, str(Path(__file__).parents[2]))
        assert plan.ready_for_core is True
        assert plan.execution_mode == "plan_only"
        assert plan.approval_required is True
        assert plan.mutation_required is True


def test_activation_rejects_unknown_host() -> None:
    with pytest.raises(ValueError, match="AF-HOST-ACTIVATION-HOST"):
        build_activation_plan("unknown", str(Path(__file__).parents[2]))
