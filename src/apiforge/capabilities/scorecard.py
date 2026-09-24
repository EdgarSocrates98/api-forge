"""Deterministic agent quality scorecards derived from evaluation results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, cast

from apiforge.contracts.agentic import AgentCapabilityProfile, AgentScorecard
from apiforge.contracts.base import ContractError
from apiforge.evals.suite import EvalResult


def build_scorecard(
    profile: AgentCapabilityProfile,
    results: tuple[EvalResult, ...],
) -> AgentScorecard:
    scores = tuple(result.score for result in results)
    passed = sum(result.verdict == "PASS" for result in results)
    gaps = tuple(
        sorted(
            {
                *(item for result in results for item in result.missing_evidence),
                *(item for result in results for item in result.failed_axes),
            }
        )
    )
    last = cast(
        Literal["unknown", "PASS", "REVIEW", "BLOCKED"],
        results[-1].verdict if results else "unknown",
    )
    return AgentScorecard(
        agent=profile.agent,
        profile_id=profile.profile_id,
        evaluation_count=len(results),
        passed_count=passed,
        quality_score=round(sum(scores) / len(scores), 3) if scores else 0.0,
        last_verdict=last,
        evidence=tuple(sorted({item for result in results for item in result.evidence})),
        gaps=gaps,
        computed_from=tuple(result.case_id for result in results),
    )


def save_scorecard(root: Path, scorecard: AgentScorecard) -> Path:
    directory = Path(root) / ".apiforge" / "scorecards"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{scorecard.profile_id}.json"
    path.write_text(
        json.dumps(scorecard.model_dump(mode="json"), sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def load_scorecards(root: Path) -> tuple[AgentScorecard, ...]:
    directory = Path(root) / ".apiforge" / "scorecards"
    if not directory.is_dir():
        return ()
    records: list[AgentScorecard] = []
    for path in sorted(directory.glob("*.json")):
        try:
            records.append(
                AgentScorecard.model_validate(json.loads(path.read_text(encoding="utf-8")))
            )
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            raise ContractError("AF-SCORECARD-INVALID", f"{path}: {exc}") from exc
    return tuple(records)
