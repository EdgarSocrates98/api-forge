import pytest

from apiforge.contracts.routing_evolution import EvolutionPolicy
from apiforge.runtime.promotion import decide_promotion, load_evolution_policy


def _policy(mode: str, *, rollback: bool = True) -> EvolutionPolicy:
    return EvolutionPolicy(mode=mode, require_rollback_ref=rollback)  # type: ignore[arg-type]


def test_default_policy_is_local_and_bounded() -> None:
    policy = load_evolution_policy()
    assert policy.mode == "local"
    assert policy.active_wave == 0
    assert policy.adaptive_plan_enabled is False


def test_local_complete_evidence_becomes_active() -> None:
    gate = decide_promotion(
        decision_id="routing:local",
        policy=_policy("local"),
        required_evidence=("task_spec", "routing_decision"),
        available_evidence=("routing_decision", "task_spec"),
        rollback_ref="run:local:static-routing",
    )
    assert gate.state == "active"
    assert gate.gaps == ()


@pytest.mark.parametrize(
    ("mode", "state"),
    [("replay", "simulated"), ("shadow", "observed"), ("external-read", "observed")],
)
def test_non_local_modes_never_authorize_active_execution(mode: str, state: str) -> None:
    gate = decide_promotion(
        decision_id=f"routing:{mode}",
        policy=_policy(mode),
        required_evidence=("task_spec",),
        available_evidence=("task_spec",),
        rollback_ref="run:mode:static-routing",
    )
    assert gate.state == state


def test_missing_evidence_blocks_even_local_mode() -> None:
    gate = decide_promotion(
        decision_id="routing:missing",
        policy=_policy("local"),
        required_evidence=("task_spec", "rollback"),
        available_evidence=("task_spec",),
        rollback_ref="run:missing:static-routing",
    )
    assert gate.state == "blocked"
    assert gate.coverage.missing == ("rollback",)


def test_active_local_mode_requires_rollback_reference() -> None:
    gate = decide_promotion(
        decision_id="routing:no-rollback",
        policy=_policy("local"),
        required_evidence=("task_spec",),
        available_evidence=("task_spec",),
    )
    assert gate.state == "blocked"
    assert "rollback reference is required for active promotion" in gate.gaps
