"""End-to-end analysis orchestration.

``analyze_project`` composes the five stages — load contract, extract code,
build API-IR, judge findings, optionally diff a baseline — and persists a
reproducible case. Construction is one-directional: a pre-persistence
``CasePayload`` feeds ``save_case`` and the returned manifest completes the
``AnalysisResult``.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict

from apiforge.adapters.fastapi.extractor import extract_fastapi
from apiforge.api_ir.builder import build_api_model
from apiforge.api_ir.models import ApiModel
from apiforge.case.models import CaseManifest, CasePayload
from apiforge.case.service import save_case
from apiforge.core.models import Diagnostic, Fact, Finding
from apiforge.openapi.diff import ContractChange, diff_contracts
from apiforge.openapi.loader import load_openapi
from apiforge.rules.judge import judge_api_model


class AnalysisError(ValueError):
    """An input or validation refusal; ``str()`` begins with the code."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


class AnalysisResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    manifest: CaseManifest
    model: ApiModel
    facts: tuple[Fact, ...]
    findings: tuple[Finding, ...]
    changes: tuple[ContractChange, ...]
    diagnostics: tuple[Diagnostic, ...]


def _require_file(path: Path, code: str = "AF-INPUT-NOT-FOUND") -> Path:
    if not path.is_file():
        raise AnalysisError(code, str(path))
    return path


def _require_dir(path: Path, code: str = "AF-INPUT-NOT-FOUND") -> Path:
    if not path.is_dir():
        raise AnalysisError(code, str(path))
    return path


def _contract_facts(model: ApiModel) -> tuple[Fact, ...]:
    """Synthesize contract.operation Facts so every evidence id resolves."""
    facts: list[Fact] = []
    for op in model.operations:
        for projection in op.contract_projections:
            operation_id = projection.detail.get("operation_id")
            facts.append(
                Fact(
                    fact_id=projection.fact_id,
                    kind="contract.operation",
                    source=projection.source,
                    measures={"method": op.method, "path": op.path},
                    attrs={"operation_id": operation_id} if operation_id else {},
                )
            )
    return tuple(facts)


def analyze_project(
    contract: Path,
    project: Path,
    baseline: Path | None,
    out_dir: Path,
) -> AnalysisResult:
    """Run the deterministic slice and persist a verified case."""
    contract_path = _require_file(Path(contract))
    project_path = _require_dir(Path(project))
    baseline_path = _require_file(Path(baseline)) if baseline else None

    document = load_openapi(contract_path)
    inventory = extract_fastapi(project_path)
    model = build_api_model(document, inventory)
    findings = judge_api_model(model)
    changes = diff_contracts(load_openapi(baseline_path), document) if baseline_path else ()

    payload = CasePayload(
        contract_path=str(contract),
        project_path=str(project),
        model=model,
        facts=(*inventory.facts, *_contract_facts(model)),
        findings=findings,
        changes=changes,
        diagnostics=model.diagnostics,
    )
    manifest = save_case(out_dir, payload)
    return AnalysisResult(
        manifest=manifest,
        model=model,
        facts=payload.facts,
        findings=findings,
        changes=changes,
        diagnostics=model.diagnostics,
    )
