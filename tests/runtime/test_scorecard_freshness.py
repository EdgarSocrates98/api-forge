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
            case_id="freshness-case",
            domain="routing",
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


def test_stale_observation_blocks_quality_promotion(tmp_path: Path) -> None:
    feedback, scorecard = update_scorecard(
        tmp_path,
        load_profiles()["api-contract-review"],
        (_result(),),
        observations=(
            ObservedSignal(
                name="duration",
                value=100,
                status="observed",
                unit="ms",
                evidence_refs=("receipt-1",),
                freshness_state="stale",
            ),
        ),
        gate={"status": "PASS"},
    )

    assert feedback.status == "updated"
    assert scorecard is not None
    assert scorecard.quality_promoted is False
    assert scorecard.freshness_state == "stale"
    assert "AF-RUNTIME-SCORECARD-FRESHNESS" in feedback.gaps


def test_observed_signal_requires_a_receipt(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="AF-RUNTIME-SCORECARD-OBSERVATION"):
        update_scorecard(
            tmp_path,
            load_profiles()["api-contract-review"],
            (_result(),),
            observations=(
                ObservedSignal(name="duration", value=100, status="observed", unit="ms"),
            ),
            gate={"status": "PASS"},
        )
