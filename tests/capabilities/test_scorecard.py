from pathlib import Path

from apiforge.capabilities.registry import capability_index
from apiforge.capabilities.scorecard import build_scorecard, load_scorecards, save_scorecard
from apiforge.contracts.routing import ObservedSignal
from apiforge.evals.suite import EvalCase, evaluate_case
from apiforge.runtime.registry import load_capabilities, load_profiles, select_eligible_capabilities


def test_profile_scorecard_is_persisted_and_reloaded(tmp_path: Path) -> None:
    profile = load_profiles()["api-contract-review"]
    case = EvalCase(
        case_id="scorecard",
        domain="runtime",
        input_ref="fixture",
        expected="REVIEW",
        required_evidence=("facts",),
        mutation="none",
        quality_axes=("status",),
    )
    result = evaluate_case(case, observed="REVIEW", evidence=("facts",), axes={"status": True})
    scorecard = build_scorecard(profile, (result,))
    save_scorecard(tmp_path, scorecard)
    assert load_scorecards(tmp_path)[0].quality_score == 1.0


def test_scorecard_orders_only_eligible_capabilities(tmp_path: Path) -> None:
    profiles = load_profiles()
    capabilities = load_capabilities()
    result = evaluate_case(
        EvalCase(
            case_id="routing",
            domain="runtime",
            input_ref="fixture",
            expected="REVIEW",
            required_evidence=(),
            mutation="none",
            quality_axes=(),
        ),
        observed="REVIEW",
        axes={},
    )
    scorecard = build_scorecard(profiles["api-contract-review"], (result,))
    save_scorecard(tmp_path, scorecard)
    selected = select_eligible_capabilities(
        capabilities,
        profiles,
        risk="read_only",
        available_evidence=("task_spec",),
        scorecards=load_scorecards(tmp_path),
    )
    assert selected
    assert all(item.name in profiles for item in selected)
    assert all(item.state == "supported" for item in selected)
    assert capability_index()


def test_scorecard_keeps_observations_additive_and_explicit() -> None:
    profile = load_profiles()["api-contract-review"]
    scorecard = build_scorecard(
        profile,
        (),
        observations=(
            ObservedSignal(
                name="cost",
                value=2.5,
                status="observed",
                unit="cost",
                evidence_refs=("run-1",),
            ),
        ),
    )
    assert scorecard.observed_cost == 2.5
    assert scorecard.observation_refs == ("run-1",)
    assert scorecard.quality_promoted is False


def test_unsupported_runtime_capability_is_not_routed(tmp_path: Path) -> None:
    path = tmp_path / "runtime.yaml"
    path.write_text(
        """runtime:
  capabilities:
    api-contract-review:
      agent: api-contract-architect
      kind: specialist
      risk: read_only
      state: unsupported
      prerequisites: [task_spec]
""",
        encoding="utf-8",
    )
    selected = select_eligible_capabilities(
        load_capabilities(path),
        load_profiles(),
        risk="read_only",
        available_evidence=("task_spec",),
    )
    assert selected == ()
