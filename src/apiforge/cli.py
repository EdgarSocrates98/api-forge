"""API Forge CLI: deterministic, offline API analysis."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import NoReturn

import typer
from typer._click.globals import get_current_context

from apiforge import __version__
from apiforge.adapters.apigateway.extract import extract_apigateway
from apiforge.adapters.fastapi.extractor import extract_fastapi
from apiforge.api_ir.builder import build_api_model
from apiforge.application.analyze import AnalysisError, AnalysisResult, analyze_project
from apiforge.build.service import build_endpoint
from apiforge.case.service import CaseIntegrityError, CaseStorageError
from apiforge.collectors.apigateway import collect
from apiforge.collectors.manifest import CollectError, CollectManifest
from apiforge.core.detail import apply_detail_level
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
rules_app = typer.Typer(
    name="rules",
    help="Read the rule catalog — the knowledge base every finding cites.",
    no_args_is_help=True,
)
app.add_typer(rules_app)
build_app = typer.Typer(
    name="build",
    help="Generate code skeletons — evaluated in the sandbox, promoted via worktree only.",
    no_args_is_help=True,
)
app.add_typer(build_app)
collect_app = typer.Typer(
    name="collect",
    help="Collect AWS artifacts into offline dumps (the only family that touches AWS).",
    no_args_is_help=True,
)
app.add_typer(collect_app)
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
economy_app = typer.Typer(
    name="economy",
    help="Measured cost per call — bytes recorded, tokens unresolved without a transcript.",
    no_args_is_help=True,
)
app.add_typer(economy_app)
context_app = typer.Typer(
    name="context",
    help="Measured context accounting — the funnel, in bytes per stage.",
    no_args_is_help=True,
)
app.add_typer(context_app)


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


_DETAIL_HELP = "Payload level: summary|normal|full."


def _detail_option() -> object:
    return typer.Option("normal", "--detail-level", help=_DETAIL_HELP)


def _echo_json(value: object, detail_level: str = "normal") -> None:
    if isinstance(value, list):
        value = [v.model_dump(mode="json") if hasattr(v, "model_dump") else v for v in value]
    elif hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    value = apply_detail_level(value, detail_level)
    text = json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2)
    from apiforge.economy.ledger import record

    ctx = get_current_context(silent=True)
    record(
        Path.cwd(),
        verb=ctx.command_path if ctx is not None else "unknown",
        detail_level=detail_level,
        payload_bytes=len(text.encode("utf-8")),
    )
    typer.echo(text)


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
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
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

    _echo_json(_run(work), detail_level)


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
    framework: str = typer.Option(
        "auto", "--framework", help="fastapi|spring|go|auto (detected from files)."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Run the full deterministic slice and persist a case."""

    def work() -> AnalysisResult:
        return analyze_project(contract, project, baseline, out_dir, framework=framework)

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
        },
        detail_level,
    )
    if fail_on is not None:
        rank = _confirmed_rank(result.findings)
        if rank is not None and rank <= _SEVERITY_RANK[fail_on]:
            raise typer.Exit(code=4)


@app.command()
def judge(
    contract: Path = typer.Option(..., "--contract", help="OpenAPI 3.1 document."),
    project: Path = typer.Option(..., "--project", help="FastAPI project root."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Judge contract/code divergence and print findings."""

    def work() -> object:
        if not contract.is_file():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(contract))
        if not project.is_dir():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(project))
        model = build_api_model(load_openapi(contract), extract_fastapi(project))
        return [f.model_dump(mode="json") for f in judge_api_model(model)]

    _echo_json(_run(work), detail_level)


@model_app.command("build")
def model_build(
    contract: Path = typer.Option(..., "--contract", help="OpenAPI 3.1 document."),
    project: Path = typer.Option(..., "--project", help="FastAPI project root."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Compose the API-IR and print it."""

    def work() -> object:
        if not contract.is_file():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(contract))
        if not project.is_dir():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(project))
        return build_api_model(load_openapi(contract), extract_fastapi(project))

    _echo_json(_run(work), detail_level)


@app.command("next-step")
def next_step_cmd(
    findings: Path = typer.Option(
        ..., "--findings", help="findings.json produced by analyze or judge."
    ),
    phase: str = typer.Option(..., "--phase", help="Canonical SDD phase."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Recommend the specialist agent for the dominant finding area."""

    def work() -> object:
        from apiforge.application.next_step import RoutingError, next_step

        if not findings.is_file():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(findings))
        data = json.loads(findings.read_text(encoding="utf-8"))
        parsed = tuple(Finding.model_validate(f) for f in data)
        try:
            return next_step(parsed, phase)
        except RoutingError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_json(_run(work), detail_level)


@diff_app.command("contract")
def diff_contract(
    baseline: Path = typer.Option(..., "--baseline", help="Baseline OpenAPI document."),
    candidate: Path = typer.Option(..., "--candidate", help="Candidate OpenAPI document."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
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

    _echo_json(_run(work), detail_level)


@collect_app.command("api-gateway")
def collect_api_gateway(
    api_id: str = typer.Option(..., "--api-id", help="REST API id."),
    out_dir: Path = typer.Option(..., "--out", help="Dump directory to write."),
    now: str | None = typer.Option(
        None, "--now", help="Explicit ISO8601 collection timestamp (the only clock)."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Fetch one REST API's configuration into an offline dump."""

    def work() -> CollectManifest:
        try:
            return collect(api_id, out_dir, now=now)
        except CollectError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    manifest = _run(work)
    assert isinstance(manifest, CollectManifest)
    _echo_json(
        {
            "artifacts": manifest.artifacts,
            "collected_at": manifest.collected_at,
            "source": manifest.source,
            "tool_version": manifest.tool_version,
        },
        detail_level,
    )


@collect_app.command("lambda")
def collect_lambda(
    function_name: str = typer.Option(..., "--function-name", help="Lambda function name."),
    out_dir: Path = typer.Option(..., "--out", help="Dump directory to write."),
    now: str | None = typer.Option(
        None, "--now", help="Explicit ISO8601 collection timestamp (the only clock)."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Fetch one Lambda function's configuration into an offline dump."""

    def work() -> CollectManifest:
        from apiforge.collectors.lambda_ import collect

        try:
            return collect(function_name, out_dir, now=now)
        except CollectError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    manifest = _run(work)
    assert isinstance(manifest, CollectManifest)
    _echo_json(
        {
            "artifacts": manifest.artifacts,
            "collected_at": manifest.collected_at,
            "source": manifest.source,
            "tool_version": manifest.tool_version,
        },
        detail_level,
    )


@model_app.command("lambda")
def inventory_lambda(
    path: Path = typer.Option(..., "--path", help="Dump directory from collect lambda."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Read a Lambda dump into facts — offline, no credentials."""

    def work() -> dict[str, object]:
        from apiforge.adapters.lambda_.extract import extract_lambda

        if not path.is_dir():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(path))
        inventory = extract_lambda(path)
        return {
            "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
            "facts": [f.model_dump(mode="json") for f in inventory.facts],
            "framework": inventory.framework,
            "input_hashes": dict(inventory.input_hashes),
        }

    _echo_json(_run(work), detail_level)


@model_app.command("terraform")
def inventory_terraform(
    path: Path = typer.Option(..., "--path", help="Directory of *.tf files."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Extract API Gateway + Lambda resources from HCL — offline, no terraform."""

    def work() -> dict[str, object]:
        from apiforge.adapters.terraform.extract import extract_terraform

        if not path.is_dir():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(path))
        inventory = extract_terraform(path)
        return {
            "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
            "facts": [f.model_dump(mode="json") for f in inventory.facts],
            "framework": inventory.framework,
            "input_hashes": dict(inventory.input_hashes),
        }

    _echo_json(_run(work), detail_level)


@model_app.command("sam")
def inventory_sam(
    path: Path = typer.Option(..., "--path", help="SAM template.yaml."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Extract AWS::Serverless::* resources — intrinsics become named diagnostics."""

    def work() -> dict[str, object]:
        from apiforge.adapters.sam.extract import extract_sam

        if not path.is_file():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(path))
        inventory = extract_sam(path)
        return {
            "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
            "facts": [f.model_dump(mode="json") for f in inventory.facts],
            "framework": inventory.framework,
            "input_hashes": dict(inventory.input_hashes),
        }

    _echo_json(_run(work), detail_level)


_REPORT_READERS: tuple[tuple[str, str, str], ...] = (
    ("pact", "apiforge.adapters.testreports.extract_pact", "Pact contract JSON file."),
    (
        "schemathesis",
        "apiforge.adapters.testreports.extract_schemathesis",
        "Schemathesis JSON report.",
    ),
    ("k6", "apiforge.adapters.testreports.extract_k6", "k6 --summary-export JSON."),
    ("coverage", "apiforge.adapters.testreports.extract_coverage", "coverage.py JSON report."),
    ("zap", "apiforge.adapters.secreports.extract_zap", "OWASP ZAP JSON report."),
    ("semgrep", "apiforge.adapters.secreports.extract_semgrep", "Semgrep --json output."),
    ("trivy", "apiforge.adapters.secreports.extract_trivy", "trivy --format json output."),
    ("gitleaks", "apiforge.adapters.secreports.extract_gitleaks", "gitleaks report JSON."),
)


def _register_report(name: str, import_path: str, help_text: str) -> None:
    """One `model <name>` command per report reader — identical payload shape."""

    def cmd(
        path: Path = typer.Option(..., "--path", help=help_text),
        detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
    ) -> None:
        def work() -> dict[str, object]:
            import importlib

            if not path.is_file():
                raise AnalysisError("AF-INPUT-NOT-FOUND", str(path))
            module, func = import_path.rsplit(".", 1)
            extract = getattr(importlib.import_module(module), func)
            inventory = extract(path)
            return {
                "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
                "facts": [f.model_dump(mode="json") for f in inventory.facts],
                "framework": inventory.framework,
                "input_hashes": dict(inventory.input_hashes),
            }

        _echo_json(_run(work), detail_level)

    model_app.command(name)(cmd)


for _name, _import, _help in _REPORT_READERS:
    _register_report(_name, _import, _help)


@model_app.command("api-gateway")
def inventory_api_gateway(
    path: Path = typer.Option(..., "--path", help="Dump directory from collect api-gateway."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Read an API Gateway dump into facts — offline, no credentials."""

    def work() -> dict[str, object]:
        if not path.is_dir():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(path))
        inventory = extract_apigateway(path)
        return {
            "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
            "facts": [f.model_dump(mode="json") for f in inventory.facts],
            "framework": inventory.framework,
            "input_hashes": dict(inventory.input_hashes),
        }

    _echo_json(_run(work), detail_level)


@build_app.command("endpoint")
def build_endpoint_cmd(
    contract: Path = typer.Option(..., "--contract", help="OpenAPI 3.1 document."),
    operation_id: str = typer.Option(..., "--operation-id", help="operationId to build."),
    project: Path = typer.Option(..., "--project", help="Java project root."),
    write_diff: Path | None = typer.Option(
        None, "--write-diff", help="Also write the emitted unified diff to a file."
    ),
    into_worktree: str | None = typer.Option(
        None, "--into-worktree", help="Promote generated files into this git worktree."
    ),
    approve: bool = typer.Option(
        False, "--approve", help="Record approval evidence for the sensitive-class gate."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Synthesize a Spring endpoint skeleton; main tree is never touched."""

    def work() -> dict[str, object]:
        if not project.is_dir():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(project))
        return build_endpoint(
            contract, project, operation_id, promote=into_worktree, approve=approve
        )

    report = _run(work)
    assert isinstance(report, dict)
    if write_diff is not None:
        from apiforge.build.diff import sources_to_diff
        from apiforge.build.java import operation_to_sources
        from apiforge.openapi.loader import load_openapi

        sources = operation_to_sources(load_openapi(contract), operation_id)
        write_diff.write_text(sources_to_diff(sources), encoding="utf-8")
    _echo_json(report, detail_level)
    promo = report.get("promotion")
    if report.get("refused") or (isinstance(promo, dict) and promo.get("refused")):
        raise typer.Exit(4)


@rules_app.command("list")
def rules_list(
    area: str | None = typer.Option(None, "--area", help="Filter by catalog area."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """List rule ids, titles and severities by area."""

    def work() -> dict[str, object]:
        from apiforge.rules.catalog import load_catalog

        catalog = load_catalog()
        by_area: dict[str, list[dict[str, str]]] = {}
        for rule_id, meta in sorted(catalog.items()):
            if area is not None and meta.area.upper() != area.upper():
                continue
            by_area.setdefault(meta.area, []).append(
                {"id": rule_id, "severity": meta.severity.value, "title": meta.title}
            )
        return {"areas": by_area, "count": sum(len(v) for v in by_area.values())}

    _echo_json(_run(work), detail_level)


@economy_app.command("report")
def economy_report(
    root: Path | None = typer.Option(
        None, "--root", help="Directory whose .apiforge/economy.jsonl to aggregate."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Aggregate recorded call sizes; detail_level_effect shows what summary saves."""

    def work() -> dict[str, object]:
        from apiforge.economy.ledger import report

        return report(root if root is not None else Path.cwd())

    _echo_json(_run(work), detail_level)


@context_app.command("funnel")
def context_funnel(
    case_dir: Path = typer.Option(
        ..., "--case", help="Persisted case directory (api-ir/facts/findings)."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Measure what each case stage keeps — bytes, never claims."""

    def work() -> dict[str, object]:
        from apiforge.application.funnel import measure_funnel

        return measure_funnel(case_dir)

    _echo_json(_run(work), detail_level)


@app.command("playbook")
def playbook_cmd(
    coordinator: str = typer.Argument(..., help="Coordinator profile name."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Render the declared executor decomposition for a coordinator.

    The floor on every platform — works without dispatch.
    """

    def work() -> dict[str, object]:
        from apiforge.rules.catalog import load_playbooks

        playbooks = load_playbooks()
        steps = playbooks.get(coordinator)
        if steps is None:
            raise AnalysisError(
                "AF-PLAYBOOK-NOT-FOUND",
                f"no playbook for {coordinator!r}; known: {sorted(playbooks)}",
            )
        return {
            "coordinator": coordinator,
            "steps": [dict(s, order=i) for i, s in enumerate(steps, 1)],
        }

    _echo_json(_run(work), detail_level)


@rules_app.command("lookup")
def rules_lookup(
    rule_id: str = typer.Argument(..., help="Rule id, e.g. AF-SEC-001."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Print one rule's full guidance."""

    def work() -> dict[str, object]:
        from apiforge.rules.catalog import load_catalog

        meta = load_catalog().get(rule_id.upper())
        if meta is None:
            raise AnalysisError("AF-RULE-NOT-FOUND", f"no rule {rule_id!r} in the catalog")
        return meta.model_dump(mode="json") | {"id": rule_id.upper()}

    _echo_json(_run(work), detail_level)
