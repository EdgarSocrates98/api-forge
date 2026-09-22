"""Declarative goldens, mutation probes and holdout checks."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    domain: str
    input_ref: str
    expected: str
    required_evidence: tuple[str, ...]
    mutation: str
    quality_axes: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.case_id,
            "domain": self.domain,
            "input": self.input_ref,
            "expected": self.expected,
            "required_evidence": list(self.required_evidence),
            "mutation": self.mutation,
            "quality_axes": list(self.quality_axes),
        }


@dataclass(frozen=True)
class EvalResult:
    case_id: str
    verdict: str
    score: float
    missing_evidence: tuple[str, ...] = ()
    failed_axes: tuple[str, ...] = ()
    holdout_digest: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "verdict": self.verdict,
            "score": self.score,
            "missing_evidence": list(self.missing_evidence),
            "failed_axes": list(self.failed_axes),
            "holdout_digest": self.holdout_digest,
        }


def load_cases(path: Path) -> tuple[EvalCase, ...]:
    """Load only the closed declarative case shape; no model is invoked."""
    document = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    raw_cases = document.get("cases", []) if isinstance(document, dict) else []
    cases: list[EvalCase] = []
    for raw in raw_cases:
        if not isinstance(raw, dict):
            continue
        cases.append(
            EvalCase(
                case_id=str(raw["id"]),
                domain=str(raw["domain"]),
                input_ref=str(raw["input"]),
                expected=str(raw["expected"]),
                required_evidence=tuple(str(item) for item in raw.get("required_evidence", ())),
                mutation=str(raw.get("mutation", "none")),
                quality_axes=tuple(str(item) for item in raw.get("quality_axes", ())),
            )
        )
    return tuple(cases)


def mutation_probe(payload: Any, mutation: str) -> dict[str, object]:
    """Create a deterministic holdout mutation without changing the input."""
    digest = hashlib.sha256(repr(payload).encode("utf-8")).hexdigest()
    return {"mutation": mutation, "source_digest": digest, "changed": mutation != "none"}


def evaluate_case(
    case: EvalCase,
    *,
    observed: str,
    evidence: tuple[str, ...] = (),
    axes: dict[str, bool] | None = None,
    holdout_payload: Any = None,
) -> EvalResult:
    missing = tuple(item for item in case.required_evidence if item not in evidence)
    failed_axes = tuple(name for name in case.quality_axes if not (axes or {}).get(name, False))
    score_parts = [observed == case.expected, not missing, not failed_axes]
    score = round(sum(score_parts) / len(score_parts), 3)
    verdict = "PASS" if score == 1 else "BLOCKED" if missing else "REVIEW"
    digest = None
    if holdout_payload is not None:
        digest = str(mutation_probe(holdout_payload, case.mutation)["source_digest"])
    return EvalResult(case.case_id, verdict, score, missing, failed_axes, digest)


def list_case_dicts(path: Path) -> list[dict[str, object]]:
    return [case.to_dict() for case in load_cases(path)]
