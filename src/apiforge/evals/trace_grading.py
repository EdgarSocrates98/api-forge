"""§23 deterministic trace grading: recorded AgentSpan sets scored
against the declared rubric in ``rules/trace_rubric.yaml``.

No model call, no inference — every dimension is a measured signal over
the spans the case supplies, and every unresolved state carries a reason.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.agent_telemetry import AgentSpan
from apiforge.contracts.base import ContractError
from apiforge.contracts.eval_plane import (
    TraceGrade,
    TraceGradeDimension,
    TraceGradingReport,
    TraceVerdict,
)
from apiforge.runtime.agent_telemetry import build_span

RUBRIC_FILE = Path(__file__).resolve().parent.parent / "rules" / "trace_rubric.yaml"


def load_rubric(path: Path = RUBRIC_FILE) -> dict[str, Any]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if (
        raw.get("version") != 1
        or not raw.get("rubric_id")
        or not isinstance(raw.get("dimensions"), dict)
    ):
        raise ContractError(
            "AF-EVALS-TRACE-RUBRIC",
            "trace rubric must declare version, rubric_id and a dimensions map",
        )
    total = sum(float(d.get("weight", 0)) for d in raw["dimensions"].values())
    if total <= 0:
        raise ContractError("AF-EVALS-TRACE-RUBRIC", "dimension weights must sum > 0")
    return raw


def load_cases(corpus: Path) -> list[dict[str, Any]]:
    cases = [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [case.get("id") for case in cases]
    if not cases or len(ids) != len(set(ids)):
        raise ContractError(
            "AF-EVALS-INVALID", f"trace-grading corpus {corpus} empty or duplicated"
        )
    return cases


def _spans(case: dict[str, Any]) -> list[AgentSpan]:
    """Build the case's spans through ``build_span`` — ids and content
    hashes are derived, never supplied by the corpus."""
    spans: list[AgentSpan] = []
    span_ids: list[str] = []
    for index, raw in enumerate(case.get("spans") or ()):
        raw = dict(raw)
        parent_index = raw.pop("parent", None)
        if parent_index is not None:
            if not (0 <= int(parent_index) < len(span_ids)):
                raise ContractError(
                    "AF-EVALS-TRACE-SPAN",
                    f"{case.get('id')} span[{index}]: parent index {parent_index} out of range",
                )
            raw["parent_span_id"] = span_ids[int(parent_index)]
        try:
            span = build_span(
                trace_id=str(case.get("trace_id", case["id"])),
                task_id=str(case.get("task_id", case["id"])),
                run_id=str(case.get("run_id", case["id"])),
                **raw,
            )
        except (TypeError, ValueError) as exc:
            raise ContractError(
                "AF-EVALS-TRACE-SPAN", f"{case.get('id')} span[{index}]: {exc}"
            ) from exc
        spans.append(span)
        span_ids.append(span.span_id)
    return spans


def _dim(
    name: str,
    weight: float,
    score: float | None,
    *,
    found: list[str] | None = None,
    missing: list[str] | None = None,
    detail: str = "",
) -> TraceGradeDimension:
    return TraceGradeDimension(
        dimension=name,
        weight=weight,
        score=score,
        state="observed" if score is not None else "unresolved",
        signals_found=tuple(found or ()),
        signals_missing=tuple(missing or ()),
        detail=detail,
    )


def _evidence_coverage(spans: list[AgentSpan], spec: dict[str, Any]) -> TraceGradeDimension:
    weight = float(spec.get("weight", 0))
    applies = set(spec.get("applies_to") or ())
    scoped = [s for s in spans if s.operation in applies]
    if not scoped:
        return _dim(
            "evidence_coverage",
            weight,
            None,
            detail="no spans in applies_to operations — nothing to score",
        )
    carrying = [s for s in scoped if s.evidence_refs]
    missing = [f"{s.operation}:{s.span_id}" for s in scoped if not s.evidence_refs]
    return _dim(
        "evidence_coverage",
        weight,
        len(carrying) / len(scoped),
        found=[f"{s.operation}:{s.span_id}" for s in carrying],
        missing=missing,
    )


def _status_honesty(spans: list[AgentSpan], spec: dict[str, Any]) -> TraceGradeDimension:
    weight = float(spec.get("weight", 0))
    errors = [s for s in spans if s.status == "error"]
    if not errors:
        return _dim("status_honesty", weight, 1.0, detail="no error spans")
    honest = [s for s in errors if s.status_message]
    missing = [s.span_id for s in errors if not s.status_message]
    return _dim(
        "status_honesty",
        weight,
        len(honest) / len(errors),
        found=[s.span_id for s in honest],
        missing=missing,
    )


def _unresolved_reporting(
    spans: list[AgentSpan], spec: dict[str, Any], case: dict[str, Any]
) -> TraceGradeDimension:
    weight = float(spec.get("weight", 0))
    expected = set(case.get("expected_unresolved") or ())
    if not expected:
        unexpected = [s.span_id for s in spans if s.unresolved]
        score = 1.0 if not unexpected else 0.5
        return _dim(
            "unresolved_reporting",
            weight,
            score,
            missing=unexpected,
            detail="no expected_unresolved declared"
            if not unexpected
            else "unexpected unresolved entries present",
        )
    found_ops = {s.operation for s in spans if s.unresolved}
    missing = sorted(expected - found_ops)
    extra = sorted(found_ops - expected)
    score = len(expected & found_ops) / len(expected) if expected else 1.0
    if extra:
        score = max(0.0, score - 0.25 * len(extra))
    return _dim(
        "unresolved_reporting",
        weight,
        score,
        found=sorted(expected & found_ops),
        missing=missing + [f"unexpected:{op}" for op in extra],
    )


def _operation_coverage(spans: list[AgentSpan], spec: dict[str, Any]) -> TraceGradeDimension:
    weight = float(spec.get("weight", 0))
    required = list(spec.get("require_operations") or ())
    if not required:
        return _dim("operation_coverage", weight, 1.0, detail="nothing required")
    present = {s.operation for s in spans}
    found = [op for op in required if op in present]
    return _dim(
        "operation_coverage",
        weight,
        len(found) / len(required),
        found=found,
        missing=[op for op in required if op not in present],
    )


def _is_retry(span: AgentSpan) -> bool:
    if (span.attributes or {}).get("retry"):
        return True
    return any("retry" in event for event in span.events)


def _retry_justification(spans: list[AgentSpan], spec: dict[str, Any]) -> TraceGradeDimension:
    weight = float(spec.get("weight", 0))
    retries = [s for s in spans if _is_retry(s)]
    if not retries:
        return _dim("retry_justification", weight, 1.0, detail="no retry spans")
    justified = [
        s
        for s in retries
        if s.parent_span_id and (s.status_message or (s.attributes or {}).get("reason"))
    ]
    missing = [s.span_id for s in retries if s not in justified]
    return _dim(
        "retry_justification",
        weight,
        len(justified) / len(retries),
        found=[s.span_id for s in justified],
        missing=missing,
    )


_DIMENSIONS = {
    "evidence_coverage": _evidence_coverage,
    "status_honesty": _status_honesty,
    "operation_coverage": _operation_coverage,
    "retry_justification": _retry_justification,
}


def grade_trace(
    spans: list[AgentSpan], rubric: dict[str, Any], *, case: dict[str, Any] | None = None
) -> TraceGrade:
    case = case or {}
    trace_ids = {s.trace_id for s in spans}
    trace_id = min(trace_ids) if trace_ids else "unresolved"
    if not spans:
        return TraceGrade(
            trace_id=trace_id,
            rubric_id=str(rubric["rubric_id"]),
            verdict="unresolved",
            unresolved=("trace carries no spans — nothing to grade",),
        )
    if len(trace_ids) > 1:
        return TraceGrade(
            trace_id=trace_id,
            rubric_id=str(rubric["rubric_id"]),
            verdict="unresolved",
            unresolved=(f"trace mixes {len(trace_ids)} trace_ids — cannot grade as one",),
        )
    dimensions: list[TraceGradeDimension] = []
    for name, spec in rubric["dimensions"].items():
        if name == "unresolved_reporting":
            dimensions.append(_unresolved_reporting(spans, spec, case))
        else:
            scorer = _DIMENSIONS.get(name)
            if scorer is None:
                dimensions.append(
                    _dim(name, float(spec.get("weight", 0)), None, detail="unknown dimension")
                )
                continue
            dimensions.append(scorer(spans, spec))
    observed = [d for d in dimensions if d.state == "observed" and d.score is not None]
    if not observed:
        return TraceGrade(
            trace_id=trace_id,
            rubric_id=str(rubric["rubric_id"]),
            dimensions=tuple(dimensions),
            verdict="unresolved",
            unresolved=("every dimension is unresolved",),
        )
    total_weight = sum(d.weight for d in observed)
    score = sum(d.weight * (d.score or 0.0) for d in observed) / total_weight
    pass_score = float(rubric.get("pass_score", 0.8))
    review_score = float(rubric.get("review_score", 0.5))
    verdict: TraceVerdict = (
        "pass" if score >= pass_score else "review" if score >= review_score else "fail"
    )
    unresolved = tuple(d.dimension for d in dimensions if d.state == "unresolved")
    return TraceGrade(
        trace_id=trace_id,
        rubric_id=str(rubric["rubric_id"]),
        dimensions=tuple(dimensions),
        score=round(score, 4),
        verdict=verdict,
        evidence_refs=tuple(ref for s in spans for ref in s.evidence_refs),
        unresolved=unresolved,
    )


def run_trace_grading(corpus: Path, *, rubric: Path = RUBRIC_FILE) -> dict[str, Any]:
    policy = load_rubric(rubric)
    cases = load_cases(corpus)
    grades: list[TraceGrade] = []
    results: list[dict[str, Any]] = []
    for case in cases:
        problems: list[str] = []
        try:
            spans = _spans(case)
        except ContractError as exc:
            results.append({"id": case.get("id"), "passed": False, "failures": [str(exc)]})
            continue
        grade = grade_trace(spans, policy, case=case)
        grades.append(grade)
        expect = case.get("expect") or {}
        if expect.get("verdict") and grade.verdict != expect["verdict"]:
            problems.append(f"verdict {grade.verdict} != {expect['verdict']}")
        if "min_score" in expect and (
            grade.score is None or grade.score < float(expect["min_score"])
        ):
            problems.append(f"score {grade.score} < {expect['min_score']}")
        if "max_score" in expect and (
            grade.score is None or grade.score > float(expect["max_score"])
        ):
            problems.append(f"score {grade.score} > {expect['max_score']}")
        for dim_name, dim_expect in (expect.get("dimensions") or {}).items():
            dim = next((d for d in grade.dimensions if d.dimension == dim_name), None)
            if dim is None:
                problems.append(f"dimension {dim_name} absent")
                continue
            if "min_score" in dim_expect and (
                dim.score is None or dim.score < float(dim_expect["min_score"])
            ):
                problems.append(f"{dim_name} {dim.score} < {dim_expect['min_score']}")
            if "state" in dim_expect and dim.state != dim_expect["state"]:
                problems.append(f"{dim_name} state {dim.state} != {dim_expect['state']}")
        results.append({"id": case["id"], "passed": not problems, "failures": problems})
    report = TraceGradingReport(
        rubric_id=str(policy["rubric_id"]),
        grades=tuple(grades),
        unresolved=tuple(
            result["failures"][0] for result in results if result["failures"] and not grades
        ),
    )
    failed = [result["id"] for result in results if not result["passed"]]
    return {
        "schema": "apiforge/trace-grading-evals/v1",
        "corpus": str(corpus),
        "rubric_id": report.rubric_id,
        "report": report.model_dump(mode="json"),
        "cases": results,
        "totals": {"cases": len(results), "failed": len(failed), "failed_ids": failed},
        "passed": not failed,
    }


__all__ = ["grade_trace", "load_cases", "load_rubric", "run_trace_grading"]
