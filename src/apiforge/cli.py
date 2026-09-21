"""API Forge CLI: deterministic, offline API analysis."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import NoReturn

import typer

from apiforge import __version__
from apiforge.adapters.fastapi.extractor import extract_fastapi
from apiforge.api_ir.builder import build_api_model
from apiforge.application.analyze import AnalysisError, AnalysisResult, analyze_project
from apiforge.case.service import CaseIntegrityError, CaseStorageError
from apiforge.core.models import Finding, FindingStatus, Severity
from apiforge.openapi.diff import diff_contracts
from apiforge.openapi.loader import OpenApiLoadError, load_openapi
from apiforge.rules.judge import judge_api_model

_SEVERITY_RANK = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
    Severity.INFO: 4,
}

app = typer.Typer(
    help="Analyze API evolution deterministically and offline.",
    invoke_without_command=True,
)
model_app = typer.Typer(help="Build the canonical API-IR.")
diff_app = typer.Typer(help="Diff OpenAPI contracts.")
app.add_typer(model_app, name="model")
app.add_typer(diff_app, name="diff")

from apiforge.cli_governance import (
    evidence_app,
    policy_app,
    sandbox_app,
    sdd_app,
)

app.add_typer(policy_app, name="policy")
app.add_typer(sdd_app, name="sdd")
app.add_typer(sandbox_app, name="sandbox")
app.add_typer(evidence_app, name="evidence")


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the API Forge version and exit.",
        is_eager=True,
    ),
) -> None:
    """Analyze API evolution deterministically and offline."""
    if version:
        typer.echo(f"apiforge {__version__}")
        raise typer.Exit()


def _echo_json(value: object) -> None:
    if isinstance(value, list):
        value = [v.model_dump(mode="json") if hasattr(v, "model_dump") else v for v in value]
    elif hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    typer.echo(json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2))


def _fail(code: str, detail: str, exit_code: int = 2) -> NoReturn:
    typer.echo(f"{code}: {detail}", err=True)
    raise typer.Exit(code=exit_code)


def _run(fn: Callable[[], object]) -> object:
    """Map typed errors onto exit codes; let nothing else through."""
    try:
        return fn()
    except AnalysisError as exc:
        _fail(exc.code, exc.detail)
    except (OpenApiLoadError, CaseStorageError) as exc:
        _fail(exc.code, str(exc).split(": ", 1)[-1])
    except CaseIntegrityError as exc:
        _fail(exc.code, exc.path, exit_code=3)


def _confirmed_rank(findings: tuple[Finding, ...]) -> int | None:
    ranks = [_SEVERITY_RANK[f.severity] for f in findings if f.status == FindingStatus.CONFIRMED]
    return min(ranks) if ranks else None


@app.command()
def discover(
    project: Path = typer.Option(..., "--project", help="FastAPI project root."),
) -> None:
    """Statically inventory FastAPI routes without executing code."""

    def work() -> object:
        if not project.is_dir():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(project))
        inventory = extract_fastapi(project)
        return {
            "routes": [f.model_dump(mode="json") for f in inventory.facts],
            "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
            "input_hashes": dict(inventory.input_hashes),
        }

    _echo_json(_run(work))


@app.command()
def analyze(
    contract: Path = typer.Option(..., "--contract", help="OpenAPI 3.1 document."),
    project: Path = typer.Option(..., "--project", help="FastAPI project root."),
    baseline: Path | None = typer.Option(
        None, "--baseline", help="Baseline OpenAPI document to diff against."
    ),
    out_dir: Path = typer.Option(Path(".apiforge"), "--out-dir", help="Case output directory."),
    fail_on: Severity | None = typer.Option(
        None, "--fail-on", help="Exit 4 on confirmed findings at this severity or worse."
    ),
) -> None:
    """Run the full deterministic slice and persist a case."""

    def work() -> AnalysisResult:
        return analyze_project(contract, project, baseline, out_dir)

    result = _run(work)
    assert isinstance(result, AnalysisResult)
    _echo_json(
        {
            "case_id": result.manifest.case_id,
            "out_dir": str(out_dir),
            "artifacts": {k: v.path for k, v in result.manifest.artifacts.items()},
            "operations": len(result.model.operations),
            "findings": len(result.findings),
            "changes": len(result.changes),
            "diagnostics": len(result.diagnostics),
        }
    )
    if fail_on is not None:
        rank = _confirmed_rank(result.findings)
        if rank is not None and rank <= _SEVERITY_RANK[fail_on]:
            raise typer.Exit(code=4)


@app.command()
def judge(
    contract: Path = typer.Option(..., "--contract", help="OpenAPI 3.1 document."),
    project: Path = typer.Option(..., "--project", help="FastAPI project root."),
) -> None:
    """Judge contract/code divergence and print findings."""

    def work() -> object:
        if not contract.is_file():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(contract))
        if not project.is_dir():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(project))
        model = build_api_model(load_openapi(contract), extract_fastapi(project))
        return [f.model_dump(mode="json") for f in judge_api_model(model)]

    _echo_json(_run(work))


@model_app.command("build")
def model_build(
    contract: Path = typer.Option(..., "--contract", help="OpenAPI 3.1 document."),
    project: Path = typer.Option(..., "--project", help="FastAPI project root."),
) -> None:
    """Compose the API-IR and print it."""

    def work() -> object:
        if not contract.is_file():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(contract))
        if not project.is_dir():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(project))
        return build_api_model(load_openapi(contract), extract_fastapi(project))

    _echo_json(_run(work))


@diff_app.command("contract")
def diff_contract(
    baseline: Path = typer.Option(..., "--baseline", help="Baseline OpenAPI document."),
    candidate: Path = typer.Option(..., "--candidate", help="Candidate OpenAPI document."),
) -> None:
    """Classify bounded breaking changes between two contracts."""

    def work() -> object:
        for path in (baseline, candidate):
            if not path.is_file():
                raise AnalysisError("AF-INPUT-NOT-FOUND", str(path))
        return [
            c.model_dump(mode="json")
            for c in diff_contracts(load_openapi(baseline), load_openapi(candidate))
        ]

    _echo_json(_run(work))
