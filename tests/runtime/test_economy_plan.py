from pathlib import Path

import pytest

from apiforge.contracts.base import ContractError
from apiforge.contracts.risk_complexity import RiskComplexityAssessment
from apiforge.contracts.routing import RoutingDecision, RoutingPlan
from apiforge.contracts.task import TaskRisk, TaskSize
from apiforge.runtime.economy import (
    EconomyError,
    allows,
    apply_economy,
    build_economy_plan,
    deterministic_proof,
    load_economy_config,
    manifest_profile,
    needs_escalation,
    reserve_calls,
    resolve_profile,
)
from tests.runtime.economy_support import economy_task, record_deterministic_run

KINDS = {
    "api-architecture-review": "specialist",
    "api-contract-review": "specialist",
    "api-data-review": "specialist",
    "task-review": "reviewer",
    "adversarial-critic": "critic",
    "debate-referee": "referee",
}


def _decision(complexity: str = "moderate", risk: str = "read_only", roles=("reviewer",)):
    assessment = RiskComplexityAssessment(
        assessment_id="a",
        task_id="t",
        revision=1,
        policy_id="p",
        policy_version="1",
        risk=risk,
        complexity=complexity,
        objective_order=("efficiency", "quality"),
        verification_depth="standard",
        required_roles=roles,
    )
    return RoutingDecision(
        decision_id="d",
        task_id="t",
        revision=1,
        policy_id="p",
        risk_complexity=assessment,
        fallback_order=("api-architecture-review", "api-contract-review", "task-review"),
    )


def _plan(**updates) -> RoutingPlan:
    values = {
        "plan_id": "p",
        "decision_id": "d",
        "task_id": "t",
        "revision": 1,
        "primary": "api-architecture-review",
        "parallel": ("api-contract-review", "api-data-review"),
        "reviewers": ("task-review",),
        "max_fallbacks": 2,
    }
    values.update(updates)
    return RoutingPlan(**values)


def test_default_profile_is_balanced_from_policy() -> None:
    assert resolve_profile(None, None, load_economy_config()) == ("balanced", "policy")


def test_flag_wins_over_manifest() -> None:
    assert resolve_profile("economy", "deep", load_economy_config()) == ("economy", "flag")
    assert resolve_profile(None, "deep", load_economy_config()) == ("deep", "manifest")


def test_invalid_profile_is_refused_with_field_and_unlock() -> None:
    with pytest.raises(EconomyError) as error:
        resolve_profile("cheap", None, load_economy_config())
    assert error.value.code == "AF-ECONOMY-PROFILE-INVALID"
    assert error.value.field == "profile"
    assert "--profile" in error.value.unlock


def test_manifest_profile_is_read_from_project_yaml(tmp_path: Path) -> None:
    (tmp_path / ".apiforge").mkdir()
    (tmp_path / ".apiforge" / "project.yaml").write_text(
        "schema: apiforge/project/v1\nproject_id: p\nroot: .\neconomy_profile: deep\n",
        encoding="utf-8",
    )
    assert manifest_profile(tmp_path) == "deep"


@pytest.mark.parametrize(
    ("complexity", "risk", "requested", "effective"),
    [
        ("simple", "read_only", "economy", "economy"),
        ("complex", "read_only", "economy", "balanced"),
        ("moderate", "sensitive", "economy", "balanced"),
        ("critical", "irreversible", "economy", "deep"),
        ("critical", "irreversible", "balanced", "deep"),
        ("simple", "read_only", "deep", "deep"),
    ],
)
def test_risk_escalates_but_never_downgrades(
    tmp_path: Path, complexity, risk, requested, effective
) -> None:
    spec = economy_task(tmp_path, risk=TaskRisk(risk))
    plan = build_economy_plan(_decision(complexity, risk), spec, flag=requested, manifest=None)
    assert plan.effective == effective
    assert (plan.escalation_reason is not None) is (effective != requested)
    if effective != requested:
        assert plan.diagnostics[0].startswith("AF-ECONOMY-ESCALATED")


def test_trim_keeps_required_roles_and_lists_removed(tmp_path: Path) -> None:
    spec = economy_task(tmp_path)
    economy = build_economy_plan(_decision(), spec, flag="economy", manifest=None)
    kept, economy = apply_economy(
        _plan(parallel=("api-contract-review",), fallbacks=("api-data-review",)),
        economy,
        _decision(),
        KINDS,
    )
    assert kept.reviewers == ("task-review",)
    assert kept.parallel == ()
    assert kept.fallbacks == ()
    assert set(economy.trimmed_roles) == {"api-contract-review", "api-data-review"}


def test_escalation_reviewer_is_an_unused_reviewer(tmp_path: Path) -> None:
    spec = economy_task(tmp_path, size=TaskSize.S)
    decision = _decision("simple", roles=())
    economy = build_economy_plan(decision, spec, flag="balanced", manifest=None)
    _, economy = apply_economy(_plan(reviewers=()), economy, decision, KINDS)
    assert economy.escalation_reviewer == "task-review"


def test_trim_refuses_to_change_risk_roles(tmp_path: Path, monkeypatch) -> None:
    spec = economy_task(tmp_path)
    economy = build_economy_plan(_decision(), spec, flag="economy", manifest=None)
    answers = iter([set(), {"reviewer"}])
    monkeypatch.setattr("apiforge.runtime.economy.role_kinds", lambda plan, kinds: next(answers))
    with pytest.raises(ContractError) as error:
        apply_economy(_plan(), economy, _decision(), KINDS)
    assert error.value.code == "AF-ECONOMY-ROLE-INVARIANT"


def test_reserve_and_ceiling_helpers(tmp_path: Path) -> None:
    spec = economy_task(tmp_path)
    economy = build_economy_plan(_decision(), spec, flag="economy", manifest=None)
    assert reserve_calls(economy.envelope, 4) == 1
    assert allows(economy, "L3") and not allows(economy, "L4")


def test_escalation_triggers() -> None:
    assert needs_escalation([0.5], [], ["a"], 0.7) == ("low_confidence",)
    assert needs_escalation([0.9], ["gap"], ["a", "b"], 0.7) == ("unresolved", "conflict")
    assert needs_escalation([0.9], [], ["a"], 0.7) == ()


def test_deterministic_proof_levels(tmp_path: Path) -> None:
    spec = economy_task(tmp_path)
    assert deterministic_proof(tmp_path, spec).level is None
    record_deterministic_run(tmp_path, output="partial evidence only")
    assert deterministic_proof(tmp_path, spec).level is None
    record_deterministic_run(tmp_path, output="specialist artifact")
    textual = deterministic_proof(tmp_path, spec)
    assert textual.level == "L1"
    assert any(note.startswith("AF-ECONOMY-PROOF-UNSTRUCTURED") for note in textual.diagnostics)
    record_deterministic_run(tmp_path, output="done", proof_kind="specialist artifact")
    assert deterministic_proof(tmp_path, spec).level == "L0"
    record_deterministic_run(tmp_path, output="done", proof_kind="specialist artifact", tamper=True)
    forged = deterministic_proof(tmp_path, spec)
    assert forged.level != "L0"
    assert any(note.startswith("AF-ECONOMY-PROOF-HASH-MISMATCH") for note in forged.diagnostics)
    record_deterministic_run(
        tmp_path, output="done", proof_kind="specialist artifact", terminal="blocked"
    )
    assert deterministic_proof(tmp_path, spec).level == "L1"
