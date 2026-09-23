"""Orchestrate the governed API/Git/CI change-control flow."""

from __future__ import annotations

import time
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from apiforge.application.analyze import AnalysisError, analyze_project
from apiforge.application.artifacts import load_findings
from apiforge.application.change_errors import ChangeControlError
from apiforge.application.next_step import RoutingError, next_step
from apiforge.contracts.change_control import (
    ChangeBundle,
    ChangeControlResult,
    Recommendation,
)
from apiforge.contracts.task import BriefStatus, OutcomeBrief
from apiforge.core.io import sha256_file, write_json
from apiforge.core.models import FindingStatus, freeze_json
from apiforge.evals.change_control import evaluate_recommendation
from apiforge.evidence.build import EvidenceError, emit_receipt
from apiforge.graph.build import build_graph
from apiforge.observability.change_metrics import (
    ChangeRunMetrics,
    ChangeStageMetric,
    write_change_metrics,
)


def _path(value: str | None, field: str) -> Path:
    if not value:
        raise ChangeControlError("AF-CHANGE-INPUT-MISSING", f"bundle field {field!r} is required")
    result = Path(value)
    if not result.exists():
        raise ChangeControlError("AF-CHANGE-INPUT-NOT-FOUND", f"{field}: {result}")
    return result


def _duration(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 3)


def _recommendation(
    bundle: ChangeBundle,
    findings: tuple[object, ...],
    evidence: tuple[str, ...],
    verifier: str,
) -> Recommendation:
    finding_ids = tuple(str(getattr(item, "finding_id", "")) for item in findings)
    unresolved = tuple(
        str(getattr(item, "finding_id", ""))
        for item in findings
        if getattr(item, "status", None) is FindingStatus.UNRESOLVED
    )
    return Recommendation(
        recommendation="Review the governed change bundle and resolve every unresolved finding before merge.",
        facts=finding_ids,
        assumptions=("provider observations are read-only and may be stale",),
        alternatives=(
            "approve after independent verification",
            "hold the change and request remediation",
        ),
        risks=(
            "contract and implementation can diverge",
            "CI observations do not prove deployment safety",
        ),
        unresolved=unresolved,
        evidence_refs=evidence,
        verifier=verifier,
        confidence=0.8 if not unresolved else 0.6,
    )


def run_change_control(
    bundle: ChangeBundle,
    out_dir: Path,
    *,
    framework: str = "auto",
    phase: str = "verify",
) -> ChangeControlResult:
    """Run analyze -> next-step -> graph -> evidence -> brief deterministically."""
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    contract = _path(bundle.contract, "contract")
    project = _path(bundle.project, "project")
    baseline = Path(bundle.baseline) if bundle.baseline else None
    run_id = str(uuid5(NAMESPACE_URL, f"{bundle.repository}:{bundle.base_sha}:{bundle.head_sha}"))
    stages: list[ChangeStageMetric] = []
    unresolved: list[str] = list(bundle.limitations)
    adapter_errors: list[str] = []
    case_dir = root / "case"
    try:
        started = time.perf_counter()
        analysis = analyze_project(contract, project, baseline, case_dir, framework=framework)
        stages.append(
            ChangeStageMetric(stage="analyze", duration_ms=_duration(started), status="ok")
        )
    except (AnalysisError, OSError, ValueError) as exc:
        code = getattr(exc, "code", "AF-CHANGE-ANALYZE")
        detail = getattr(exc, "detail", str(exc))
        stages.append(
            ChangeStageMetric(stage="analyze", duration_ms=0, status="failed", error_code=code)
        )
        raise ChangeControlError(code, detail) from exc
    try:
        started = time.perf_counter()
        findings = load_findings(case_dir / "findings.json")
        route = next_step(findings, phase)
        write_json(root / "next-step.json", route)
        stages.append(
            ChangeStageMetric(stage="next_step", duration_ms=_duration(started), status="ok")
        )
    except (RoutingError, OSError) as exc:
        code = getattr(exc, "code", "AF-CHANGE-NEXT-STEP")
        stages.append(
            ChangeStageMetric(stage="next_step", duration_ms=0, status="failed", error_code=code)
        )
        raise ChangeControlError(code, str(exc)) from exc
    try:
        started = time.perf_counter()
        graph = build_graph(case_dir, root / "graph")
        write_json(root / "graph.json", graph)
        stages.append(ChangeStageMetric(stage="graph", duration_ms=_duration(started), status="ok"))
    except (OSError, ValueError) as exc:
        stages.append(
            ChangeStageMetric(
                stage="graph", duration_ms=0, status="failed", error_code="AF-CHANGE-GRAPH"
            )
        )
        raise ChangeControlError("AF-CHANGE-GRAPH", str(exc)) from exc
    try:
        started = time.perf_counter()
        receipt = emit_receipt(case_dir)
        receipt_path = root / "evidence" / "receipt.json"
        write_json(receipt_path, receipt)
        stages.append(
            ChangeStageMetric(stage="evidence", duration_ms=_duration(started), status="ok")
        )
    except (EvidenceError, OSError) as exc:
        code = getattr(exc, "code", "AF-CHANGE-EVIDENCE")
        stages.append(
            ChangeStageMetric(stage="evidence", duration_ms=0, status="failed", error_code=code)
        )
        raise ChangeControlError(code, str(exc)) from exc
    artifact_refs: tuple[str, ...] = (
        str(case_dir / "case.json"),
        str(root / "next-step.json"),
        str(root / "graph.json"),
        str(root / "graph" / "nodes.jsonl"),
        str(root / "graph" / "edges.jsonl"),
        str(receipt_path),
    )
    gaps = tuple(unresolved)
    if route.unmapped_count:
        gaps = (*gaps, f"{route.unmapped_count} finding(s) did not map to a catalog rule")
    recommendation = _recommendation(
        bundle,
        findings,
        artifact_refs,
        f"apiforge change-control verify --run-dir {root}",
    )
    evaluation = evaluate_recommendation(recommendation)
    if evaluation.status != "pass":
        gaps = (*gaps, "recommendation evaluation did not pass")
    try:
        started = time.perf_counter()
        brief = OutcomeBrief(
            status=BriefStatus.REVIEW if gaps or findings else BriefStatus.DECIDE,
            outcome="API/Git/CI change-control analysis completed",
            human_action="independently verify findings before approving the change",
            proof=artifact_refs,
            gaps=gaps,
            next="resolve findings, then rerun the governed verifier",
            subject=run_id,
        )
        brief_path = root / "brief.json"
        write_json(brief_path, brief)
        artifact_refs = (*artifact_refs, str(brief_path))
        stages.append(
            ChangeStageMetric(stage="brief", duration_ms=_duration(started), status="review")
        )
    except ValueError as exc:
        stages.append(
            ChangeStageMetric(
                stage="brief", duration_ms=0, status="failed", error_code="AF-CHANGE-BRIEF"
            )
        )
        raise ChangeControlError("AF-CHANGE-BRIEF", str(exc)) from exc
    raw_payload = {
        "run_id": run_id,
        "repository": bundle.repository,
        "base_sha": bundle.base_sha,
        "head_sha": bundle.head_sha,
        "origin": bundle.origin,
        "route": route.model_dump(mode="json"),
        "analysis": analysis.manifest.model_dump(mode="json"),
        "graph": graph.model_dump(mode="json"),
        "receipt": receipt.model_dump(mode="json"),
        "recommendation": recommendation.model_dump(mode="json"),
        "evaluation": evaluation.model_dump(mode="json"),
        "artifacts": artifact_refs,
    }
    payload = freeze_json(raw_payload)
    if not isinstance(payload, dict):
        raise ChangeControlError("AF-CHANGE-RESULT-SHAPE", "result payload must be an object")
    result = ChangeControlResult(
        state="supported",
        status="review" if gaps or findings else "ok",
        payload=payload,
        evidence=artifact_refs,
        gaps=gaps,
        limitations=bundle.limitations,
    )
    result_path = root / "result.json"
    write_json(result_path, result)
    metrics = ChangeRunMetrics(
        run_id=run_id,
        source=bundle.provider,
        repository=bundle.repository,
        base_sha=bundle.base_sha,
        head_sha=bundle.head_sha,
        status=result.status,
        unresolved=gaps,
        adapter_errors=tuple(adapter_errors),
        artifact_refs=(*artifact_refs, str(result_path)),
        stages=tuple(stages),
        details={"bundle_sha256": sha256_file(Path(bundle.contract)) if bundle.contract else ""},
    )
    write_change_metrics(root / "metrics.json", metrics)
    return result
