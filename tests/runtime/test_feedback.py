from pathlib import Path

import pytest

from apiforge.contracts.base import ContractError
from apiforge.contracts.routing import ObservedSignal
from apiforge.evals.suite import EvalCase, evaluate_case
from apiforge.runtime.feedback import update_scorecard
from apiforge.runtime.registry import load_profiles


def _result() -> object:
    return evaluate_case(
        EvalCase(
            case_id="feedback-case",
            domain="runtime",
            input_ref="fixture",
            expected="PASS",
            required_evidence=("eval-proof",),
            mutation="none",
            quality_axes=("quality",),
        ),
        observed="PASS",
        evidence=("eval-proof",),
        axes={"quality": True},
    )


def test_feedback_updates_scorecard_only_after_passing_gate(tmp_path: Path) -> None:
    feedback, scorecard = update_scorecard(
        tmp_path,
        load_profiles()["api-contract-review"],
        (_result(),),
        observations=(
            ObservedSignal(
                name="duration",
                value=12,
                status="observed",
                unit="ms",
                evidence_refs=("run-1",),
            ),
        ),
        gate={"status": "PASS"},
    )
    assert feedback.status == "updated"
    assert scorecard is not None
    assert scorecard.quality_promoted is True
    assert scorecard.observed_duration_ms == 12
    assert feedback.scorecard_path is not None


def test_feedback_preserves_non_pass_without_persisting_promotion(tmp_path: Path) -> None:
    feedback, scorecard = update_scorecard(
        tmp_path,
        load_profiles()["api-contract-review"],
        (_result(),),
        gate={"status": "BLOCKED"},
    )
    assert feedback.status == "blocked"
    assert scorecard is not None
    assert scorecard.quality_promoted is False
    assert scorecard.quality_score == 0
    assert not (tmp_path / ".apiforge" / "scorecards").exists()


def test_feedback_refuses_missing_result_evidence(tmp_path: Path) -> None:
    result = evaluate_case(
        EvalCase(
            case_id="missing-evidence",
            domain="runtime",
            input_ref="fixture",
            expected="PASS",
            required_evidence=(),
            mutation="none",
            quality_axes=(),
        ),
        observed="PASS",
    )
    with pytest.raises(ContractError, match="AF-RUNTIME-EVAL-GATE"):
        update_scorecard(
            tmp_path,
            load_profiles()["api-contract-review"],
            (result,),
            gate={"status": "PASS"},
        )
