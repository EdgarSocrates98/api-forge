"""API Forge CLI: deterministic, offline API analysis."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Literal, NoReturn, cast

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
from apiforge.contract_intel import (
    ContractProtocol,
    analyze_contract,
    build_twin_plan,
    simulate_twin,
)
from apiforge.contracts.base import ContractError
from apiforge.contracts.stubs import PerformanceRun
from apiforge.core.detail import apply_detail_level
from apiforge.core.models import Fact, Finding, FindingStatus, Severity
from apiforge.debate.service import DebateError
from apiforge.dispatch.runner import DispatchError
from apiforge.openapi.diff import diff_contracts
from apiforge.openapi.loader import OpenApiLoadError, load_openapi
from apiforge.rules.fact_judge import judge_facts
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
    autonomy_app as _governance_autonomy,
)
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
agentops_app = typer.Typer(
    name="agentops",
    help="Host-neutral Caveman/RTK protocols, workflows and adapters.",
    no_args_is_help=True,
)
app.add_typer(agentops_app)
evals_app = typer.Typer(
    name="evals",
    help="Declarative local eval matrix, goldens and holdout metadata.",
    no_args_is_help=True,
)
app.add_typer(evals_app)
contract_intel_app = typer.Typer(
    name="contract-intel",
    help="Unify contract impact analysis and build an offline API Digital Twin.",
    no_args_is_help=True,
)
app.add_typer(contract_intel_app)
report_app = typer.Typer(
    name="report",
    help="Release evidence bundle — sign binds hashes; verify names what diverged.",
    no_args_is_help=True,
)
app.add_typer(report_app)
plan_app = typer.Typer(
    name="plan",
    help="Planning verbs — compose over facts other verbs already extracted.",
    no_args_is_help=True,
)
app.add_typer(plan_app)
debate_app = typer.Typer(
    name="debate",
    help="Record specialist disagreement — positions cite fact_ids, a referee closes.",
    no_args_is_help=True,
)
app.add_typer(debate_app)
dispatch_app = typer.Typer(
    name="dispatch",
    help="Run deterministic playbook steps; pending steps name their missing inputs.",
    no_args_is_help=True,
)
app.add_typer(dispatch_app)
perf_app = typer.Typer(
    name="perf",
    help="Compose over measured runs — compare, never interpolate.",
    no_args_is_help=True,
)
app.add_typer(perf_app)
agents_app = typer.Typer(
    name="agents",
    help="Publish coordinator profiles to host-native mirrors.",
    no_args_is_help=True,
)
app.add_typer(agents_app)
run_app = typer.Typer(
    name="run",
    help="Execute allowlisted scanner binaries, then read their reports.",
    no_args_is_help=True,
)
app.add_typer(run_app)
autonomy_app = _governance_autonomy
app.add_typer(autonomy_app, name="autonomy")
contract_app = typer.Typer(
    name="contract",
    help="List and inspect the canonical versioned contracts.",
    no_args_is_help=True,
)
app.add_typer(contract_app)
task_app = typer.Typer(
    name="task",
    help="Sealed, budgeted units of agentic work (TaskSpec).",
    no_args_is_help=True,
)
app.add_typer(task_app)
runtime_app = typer.Typer(
    name="runtime",
    help="Bounded agentic execution over sealed TaskSpecs; local and CI safe.",
    no_args_is_help=True,
)
app.add_typer(runtime_app)
brief_app = typer.Typer(
    name="brief",
    help="Outcome Briefs — DONE is refused while mandatory gaps exist.",
    no_args_is_help=True,
)
app.add_typer(brief_app)
graph_app = typer.Typer(
    name="graph",
    help="Native provenance graph — canonical JSONL store, closed-vocabulary queries.",
    no_args_is_help=True,
)
app.add_typer(graph_app)
index_app = typer.Typer(
    name="index",
    help="TokenSave: content-hash cache + local indexes over extractor output.",
    no_args_is_help=True,
)
app.add_typer(index_app)
knowledge_app = typer.Typer(
    name="knowledge",
    help="Domain packs — source authority, runtime matrices, declared evals.",
    no_args_is_help=True,
)
app.add_typer(knowledge_app)
observability_app = typer.Typer(
    name="observability",
    help="Offline-first OTel, Datadog and Dynatrace control plane.",
    no_args_is_help=True,
)
app.add_typer(observability_app)
grpc_app = typer.Typer(
    name="grpc",
    help="Offline-first gRPC contract control plane.",
    no_args_is_help=True,
)
app.add_typer(grpc_app)
migration_app = typer.Typer(
    name="migration",
    help="Offline-first runtime migration analysis and verification.",
    no_args_is_help=True,
)
app.add_typer(migration_app)


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
    # JSON must remain printable on Windows hosts whose stdout is cp1252;
    # Unicode content stays lossless through JSON escapes.
    text = json.dumps(value, sort_keys=True, ensure_ascii=True, indent=2)
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


def _load_facts(path: Path) -> list[Fact]:
    """Read a facts payload ({"facts": [...]} or a bare list) from disk."""
    if not path.is_file():
        raise AnalysisError("AF-INPUT-NOT-FOUND", str(path))
    doc = json.loads(path.read_text(encoding="utf-8"))
    payload = doc.get("facts", doc) if isinstance(doc, dict) else doc
    if not isinstance(payload, list):
        raise AnalysisError("AF-JUDGE-FACTS-INVALID", f"{path}: not a fact list")
    return [Fact.model_validate(f) for f in payload]


def _run(fn: Callable[[], object]) -> object:
    """Map typed errors onto exit codes; let nothing else through."""
    try:
        return fn()
    except AnalysisError as exc:
        _fail(exc.code, exc.detail)
    except DebateError as exc:
        _fail(exc.code, str(exc).split(": ", 1)[-1])
    except DispatchError as exc:
        _fail(exc.code, str(exc).split(": ", 1)[-1])
    except (OpenApiLoadError, CaseStorageError) as exc:
        _fail(exc.code, str(exc).split(": ", 1)[-1])
    except CaseIntegrityError as exc:
        _fail(exc.code, exc.path, exit_code=3)


def _confirmed_rank(findings: tuple[Finding, ...]) -> int | None:
    ranks = [_SEVERITY_RANK[f.severity] for f in findings if f.status == FindingStatus.CONFIRMED]
    return min(ranks) if ranks else None


@observability_app.command("ingest")
def observability_ingest(
    source: Path = typer.Option(..., "--source", help="OTel-compatible JSON fixture."),
    service: str | None = typer.Option(None, "--service"),
    slo: Path | None = typer.Option(None, "--slo", help="SLO JSON definition."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Normalize a fixture and compute signals without external access."""
    from apiforge.observability.supervisor import run_fixture

    def work() -> dict[str, object]:
        if not source.is_file():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(source))
        definition = json.loads(slo.read_text(encoding="utf-8")) if slo else None
        return run_fixture(Path.cwd(), source, service=service, slo=definition)

    _echo_json(_run(work), detail_level)


@observability_app.command("capabilities")
def observability_capabilities(
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Show provider capabilities without credentials."""
    from apiforge.observability.registry import capabilities

    _echo_json(capabilities(), detail_level)


@observability_app.command("instrument")
def observability_instrument(
    language: str = typer.Option(..., "--language"),
    framework: str | None = typer.Option(None, "--framework"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Recommend OTel instrumentation for Java, Go or Python."""
    from apiforge.observability.instrumentation import recommend

    _echo_json(recommend(language, framework), detail_level)


@observability_app.command("health")
def observability_health(
    source: Path = typer.Option(..., "--source", help="OTel-compatible JSON fixture."),
    service: str = typer.Option(..., "--service"),
    slo: Path | None = typer.Option(None, "--slo", help="SLO JSON definition."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Correlate telemetry and SLO evidence into an incident-ready health view."""
    from apiforge.contracts.observability import SLODefinition, SLOResult
    from apiforge.observability.adapters.otel_json import read
    from apiforge.observability.health import assess_health
    from apiforge.observability.normalize import normalize_records
    from apiforge.observability.slo import evaluate_slo

    try:
        if not source.is_file():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(source))
        records = tuple(record for record in normalize_records(read(source), source=source.name) if record.service == service)
        slo_results: tuple[SLOResult, ...] = ()
        if slo:
            definitions = json.loads(slo.read_text(encoding="utf-8"))
            raw_definitions = definitions if isinstance(definitions, list) else [definitions]
            slo_results = tuple(evaluate_slo(SLODefinition.model_validate(item), records) for item in raw_definitions)
        result = assess_health(service, records, slo_results)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise AnalysisError("AF-OBSERVABILITY-HEALTH-INVALID", str(exc)) from exc
    _echo_json(result.model_dump(mode="json"), detail_level)


@observability_app.command("read-plan")
def observability_read_plan(
    provider: str = typer.Option(..., "--provider", help="otel, datadog, dynatrace or cloudwatch."),
    service: str = typer.Option(..., "--service"),
    start: str = typer.Option(..., "--start", help="ISO-8601 start."),
    end: str = typer.Option(..., "--end", help="ISO-8601 end."),
    environment: str = typer.Option("unknown", "--environment"),
    signal: list[str] = typer.Option([], "--signal", help="traces, metrics, logs or events."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Create a vendor read plan without credentials or network access."""
    from apiforge.observability.read import build_read_plan

    try:
        signals = cast(
            tuple[Literal["traces", "metrics", "logs", "events"], ...],
            tuple(signal) if signal else ("traces", "metrics"),
        )
        result = build_read_plan(provider, service, start, end, environment=environment, signals=signals)
    except (TypeError, ValueError) as exc:
        raise AnalysisError("AF-OBS-READ-PLAN-INVALID", str(exc)) from exc
    _echo_json(result.model_dump(mode="json"), detail_level)


@observability_app.command("credential-check")
def observability_credential_check(
    provider: str = typer.Option(..., "--provider"),
    reference: str = typer.Option(..., "--reference", help="Secret reference name; never a secret value."),
    source: str = typer.Option("external_broker", "--source"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Validate credential metadata without reading environment or secret stores."""
    from apiforge.observability.credentials import check_reference

    try:
        result = check_reference(provider, reference, source)
    except ValueError as exc:
        raise AnalysisError("AF-OBS-CREDENTIAL-INVALID", str(exc)) from exc
    _echo_json(result.model_dump(mode="json"), detail_level)


@app.command()
def discover(
    project: Path = typer.Option(..., "--project", help="FastAPI project root."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Statically inventory FastAPI routes without executing code."""

    def work() -> object:
        if not project.is_dir():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(project))
        from apiforge.index.cache import extract_cached

        inventory, cache_meta = extract_cached(
            project,
            "fastapi",
            extract_fastapi,
            Path.cwd() / ".apiforge" / "cache",
            ledger_root=Path.cwd(),
        )
        return {
            "cache": cache_meta,
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
        return analyze_project(
            contract,
            project,
            baseline,
            out_dir,
            framework=framework,
            cache_dir=Path.cwd() / ".apiforge" / "cache",
            ledger_root=Path.cwd(),
        )

    result = _run(work)
    assert isinstance(result, AnalysisResult)
    _echo_json(
        {
            "cache": dict(result.cache),
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
    contract: Path | None = typer.Option(None, "--contract", help="OpenAPI 3.1 document."),
    project: Path | None = typer.Option(None, "--project", help="FastAPI project root."),
    facts: Path | None = typer.Option(
        None, "--facts", help="facts.json emitted by a `model *` verb."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Judge contract/code divergence, or catalog checks over report facts."""

    def work() -> object:
        if facts is not None:
            if contract is not None or project is not None:
                raise AnalysisError(
                    "AF-JUDGE-INPUT-AMBIGUOUS",
                    "--facts is exclusive with --contract/--project",
                )
            return [f.model_dump(mode="json") for f in judge_facts(_load_facts(facts))]
        if contract is None or project is None:
            raise AnalysisError(
                "AF-JUDGE-INPUT-MISSING",
                "judge needs --contract/--project or --facts",
            )
        if not contract.is_file() or not project.is_dir():
            raise AnalysisError("AF-INPUT-NOT-FOUND", f"{contract} or {project}")
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


_AWS_DUMP_READERS = {
    "sqs": "apiforge.adapters.awsdumps.extract_sqs",
    "sns": "apiforge.adapters.awsdumps.extract_sns",
    "eventbridge": "apiforge.adapters.awsdumps.extract_eventbridge",
    "iam-role": "apiforge.adapters.awsdumps.extract_iam_role",
    "cognito": "apiforge.adapters.awsdumps.extract_cognito",
    "waf": "apiforge.adapters.awsdumps.extract_waf",
    "dynamodb": "apiforge.adapters.awsdumps.extract_dynamodb",
    "docdb": "apiforge.adapters.awsdumps.extract_docdb",
    "neptune": "apiforge.adapters.awsdumps.extract_neptune",
    "stepfunctions": "apiforge.adapters.awsdumps.extract_stepfunctions",
    "cloudwatch": "apiforge.adapters.awsdumps.extract_cloudwatch",
    "xray": "apiforge.adapters.awsdumps.extract_xray",
    "kms": "apiforge.adapters.awsdumps.extract_kms",
    "secrets": "apiforge.adapters.awsdumps.extract_secrets",
    "vpc-endpoints": "apiforge.adapters.awsdumps.extract_vpc_endpoints",
    "s3": "apiforge.adapters.awsdumps.extract_s3",
    "alb": "apiforge.adapters.awsdumps.extract_alb",
    "ecs": "apiforge.adapters.awsdumps.extract_ecs",
    "eks": "apiforge.adapters.awsdumps.extract_eks",
    "ec2": "apiforge.adapters.awsdumps.extract_ec2",
    "msk": "apiforge.adapters.awsdumps.extract_msk",
    "elasticache": "apiforge.adapters.awsdumps.extract_elasticache",
}


def _register_dump_models() -> None:
    """One `model <svc>` command per collector dump — same closed shape."""

    def make(dotted: str) -> Callable[[Path, str], None]:
        def cmd(
            path: Path = typer.Option(..., "--path", help="Dump directory from `collect`."),
            detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
        ) -> None:
            def work() -> dict[str, object]:
                import importlib

                if not path.is_dir():
                    raise AnalysisError("AF-INPUT-NOT-FOUND", str(path))
                module, _, func = dotted.rpartition(".")
                inventory = getattr(importlib.import_module(module), func)(path)
                return {
                    "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
                    "facts": [f.model_dump(mode="json") for f in inventory.facts],
                    "framework": inventory.framework,
                    "input_hashes": dict(inventory.input_hashes),
                }

            _echo_json(_run(work), detail_level)

        return cmd

    for svc, dotted in _AWS_DUMP_READERS.items():
        model_app.command(svc)(make(dotted))


_register_dump_models()


@collect_app.command("sqs")
def collect_sqs(
    queue_url: str = typer.Option(..., "--queue-url", help="SQS queue URL."),
    out_dir: Path = typer.Option(..., "--out", help="Dump directory to write."),
    now: str | None = typer.Option(
        None, "--now", help="Explicit ISO8601 collection timestamp (the only clock)."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Fetch one queue's attribute set into an offline dump."""

    def work() -> CollectManifest:
        from apiforge.collectors.messaging import collect_sqs

        try:
            return collect_sqs(queue_url, out_dir, now=now)
        except CollectError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_manifest(_run(work), detail_level)


@collect_app.command("sns")
def collect_sns(
    topic_arn: str = typer.Option(..., "--topic-arn", help="SNS topic ARN."),
    out_dir: Path = typer.Option(..., "--out", help="Dump directory to write."),
    now: str | None = typer.Option(
        None, "--now", help="Explicit ISO8601 collection timestamp (the only clock)."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Fetch one topic's attributes and subscriptions into an offline dump."""

    def work() -> CollectManifest:
        from apiforge.collectors.messaging import collect_sns

        try:
            return collect_sns(topic_arn, out_dir, now=now)
        except CollectError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_manifest(_run(work), detail_level)


@collect_app.command("eventbridge")
def collect_eventbridge(
    bus_name: str = typer.Option(..., "--event-bus", help="Event bus name."),
    out_dir: Path = typer.Option(..., "--out", help="Dump directory to write."),
    now: str | None = typer.Option(
        None, "--now", help="Explicit ISO8601 collection timestamp (the only clock)."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Fetch the bus, its rules and their targets into an offline dump."""

    def work() -> CollectManifest:
        from apiforge.collectors.messaging import collect_eventbridge

        try:
            return collect_eventbridge(bus_name, out_dir, now=now)
        except CollectError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_manifest(_run(work), detail_level)


@collect_app.command("iam-role")
def collect_iam_role(
    role_name: str = typer.Option(..., "--role-name", help="IAM role name."),
    out_dir: Path = typer.Option(..., "--out", help="Dump directory to write."),
    now: str | None = typer.Option(
        None, "--now", help="Explicit ISO8601 collection timestamp (the only clock)."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Fetch one role, its attached policies and inline policy documents."""

    def work() -> CollectManifest:
        from apiforge.collectors.identity import collect_iam_role

        try:
            return collect_iam_role(role_name, out_dir, now=now)
        except CollectError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_manifest(_run(work), detail_level)


@collect_app.command("cognito")
def collect_cognito(
    user_pool_id: str = typer.Option(..., "--user-pool-id", help="User pool id."),
    out_dir: Path = typer.Option(..., "--out", help="Dump directory to write."),
    now: str | None = typer.Option(
        None, "--now", help="Explicit ISO8601 collection timestamp (the only clock)."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Fetch the user pool and its app clients into an offline dump."""

    def work() -> CollectManifest:
        from apiforge.collectors.identity import collect_cognito

        try:
            return collect_cognito(user_pool_id, out_dir, now=now)
        except CollectError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_manifest(_run(work), detail_level)


@collect_app.command("waf")
def collect_waf(
    web_acl_id: str = typer.Option(..., "--web-acl-id", help="WebACL id."),
    web_acl_name: str = typer.Option(..., "--web-acl-name", help="WebACL name."),
    scope: str = typer.Option("REGIONAL", "--scope", help="REGIONAL or CLOUDFRONT."),
    out_dir: Path = typer.Option(..., "--out", help="Dump directory to write."),
    now: str | None = typer.Option(
        None, "--now", help="Explicit ISO8601 collection timestamp (the only clock)."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Fetch one WebACL's configuration into an offline dump."""

    def work() -> CollectManifest:
        from apiforge.collectors.identity import collect_waf

        try:
            return collect_waf(web_acl_id, web_acl_name, scope, out_dir, now=now)
        except CollectError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_manifest(_run(work), detail_level)


_COLLECT_SIMPLE = {
    "rds": (
        "apiforge.collectors.datastores.collect_rds",
        "--resource-id",
        "RDS instance or Aurora cluster identifier.",
    ),
    "dynamodb": (
        "apiforge.collectors.datastores.collect_dynamodb",
        "--table-name",
        "DynamoDB table name.",
    ),
    "docdb": (
        "apiforge.collectors.datastores.collect_docdb",
        "--cluster-id",
        "DocDB cluster identifier.",
    ),
    "neptune": (
        "apiforge.collectors.datastores.collect_neptune",
        "--cluster-id",
        "Neptune cluster identifier.",
    ),
    "stepfunctions": (
        "apiforge.collectors.ops.collect_stepfunctions",
        "--state-machine-arn",
        "State machine ARN.",
    ),
    "cloudwatch": (
        "apiforge.collectors.ops.collect_cloudwatch",
        "--alarm-prefix",
        "Alarm name prefix.",
    ),
    "kms": (
        "apiforge.collectors.ops.collect_kms",
        "--key-id",
        "KMS key id or ARN.",
    ),
    "secrets": (
        "apiforge.collectors.ops.collect_secrets",
        "--secret-id",
        "Secret name or ARN — metadata only, value never read.",
    ),
    "vpc-endpoints": (
        "apiforge.collectors.ops.collect_vpc_endpoints",
        "--vpc-id",
        "VPC id.",
    ),
    "s3": (
        "apiforge.collectors.ops.collect_s3",
        "--bucket",
        "S3 bucket name — posture only, never objects.",
    ),
    "alb": (
        "apiforge.collectors.compute.collect_alb",
        "--lb-arn",
        "Load balancer ARN.",
    ),
    "ecs": (
        "apiforge.collectors.compute.collect_ecs",
        "--cluster",
        "ECS cluster name — collects every service in it.",
    ),
    "eks": (
        "apiforge.collectors.compute.collect_eks",
        "--cluster-name",
        "EKS cluster name.",
    ),
    "ec2": (
        "apiforge.collectors.compute.collect_ec2",
        "--instance-id",
        "EC2 instance id — posture only, never user-data.",
    ),
    "msk": (
        "apiforge.collectors.compute.collect_msk",
        "--cluster-arn",
        "MSK cluster ARN.",
    ),
    "elasticache": (
        "apiforge.collectors.compute.collect_elasticache",
        "--replication-group-id",
        "ElastiCache replication group id.",
    ),
}


def _register_collect_simple() -> None:
    """One `collect <svc>` per single-identifier collector — closed shape."""

    def make(dotted: str, flag: str, help_text: str) -> Callable[..., None]:
        def cmd(
            identifier: str = typer.Option(..., flag, help=help_text),
            out_dir: Path = typer.Option(..., "--out", help="Dump directory to write."),
            now: str | None = typer.Option(
                None,
                "--now",
                help="Explicit ISO8601 collection timestamp (the only clock).",
            ),
            detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
        ) -> None:
            def work() -> CollectManifest:
                import importlib

                module, _, func = dotted.rpartition(".")
                collect_fn = getattr(importlib.import_module(module), func)
                try:
                    manifest = collect_fn(identifier, out_dir, now=now)
                    assert isinstance(manifest, CollectManifest)
                    return manifest
                except CollectError as exc:
                    raise AnalysisError(exc.code, exc.detail) from exc

            _echo_manifest(_run(work), detail_level)

        return cmd

    for svc, (dotted, flag, help_text) in _COLLECT_SIMPLE.items():
        collect_app.command(svc)(make(dotted, flag, help_text))

    @collect_app.command("xray")
    def collect_xray_cmd(
        out_dir: Path = typer.Option(..., "--out", help="Dump directory to write."),
        now: str | None = typer.Option(
            None,
            "--now",
            help="Explicit ISO8601 collection timestamp (the only clock).",
        ),
        detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
    ) -> None:
        """Fetch X-Ray sampling rules and encryption config."""

        def work() -> CollectManifest:
            from apiforge.collectors.ops import collect_xray

            try:
                return collect_xray(out_dir, now=now)
            except CollectError as exc:
                raise AnalysisError(exc.code, exc.detail) from exc

        _echo_manifest(_run(work), detail_level)


_register_collect_simple()


def _echo_manifest(manifest: object, detail_level: str) -> None:
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
    ("locust", "apiforge.adapters.testreports.extract_locust", "Locust --csv stats export."),
    ("jmeter", "apiforge.adapters.testreports.extract_jmeter", "JMeter JTL CSV."),
    (
        "gatling",
        "apiforge.adapters.testreports.extract_gatling",
        "Gatling global_stats.json or report dir.",
    ),
    ("vegeta", "apiforge.adapters.testreports.extract_vegeta", "vegeta report -type=json."),
    ("wrk", "apiforge.adapters.testreports.extract_wrk", "wrk stdout summary text."),
    ("hey", "apiforge.adapters.testreports.extract_hey", "hey -o csv export."),
    (
        "pytest-benchmark",
        "apiforge.adapters.testreports.extract_pytest_benchmark",
        "pytest-benchmark --benchmark-json.",
    ),
    ("coverage", "apiforge.adapters.testreports.extract_coverage", "coverage.py JSON report."),
    ("zap", "apiforge.adapters.secreports.extract_zap", "OWASP ZAP JSON report."),
    ("semgrep", "apiforge.adapters.secreports.extract_semgrep", "Semgrep --json output."),
    ("trivy", "apiforge.adapters.secreports.extract_trivy", "trivy --format json output."),
    ("gitleaks", "apiforge.adapters.secreports.extract_gitleaks", "gitleaks report JSON."),
    (
        "asyncapi",
        "apiforge.adapters.asyncapi.extract.extract_asyncapi",
        "AsyncAPI 2.x/3.x document.",
    ),
    (
        "graphql",
        "apiforge.adapters.graphql_.extract.extract_graphql",
        "GraphQL SDL schema file.",
    ),
    ("jfr", "apiforge.adapters.perfprofiles.extract_jfr", "jfr print --json output."),
    ("pprof", "apiforge.adapters.perfprofiles.extract_pprof", "go tool pprof -top text."),
    (
        "pyroscope",
        "apiforge.adapters.perfprofiles.extract_pyroscope",
        "Pyroscope flamebearer JSON.",
    ),
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


@model_app.command("proto")
def inventory_proto(
    path: Path = typer.Option(..., "--path", help="Directory of *.proto files."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Extract gRPC services/messages from .proto — no protoc, offline."""

    def work() -> dict[str, object]:
        from apiforge.adapters.protobuf.extract import extract_protobuf

        if not path.is_dir():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(path))
        inventory = extract_protobuf(path)
        return {
            "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
            "facts": [f.model_dump(mode="json") for f in inventory.facts],
            "framework": inventory.framework,
            "input_hashes": dict(inventory.input_hashes),
        }

    _echo_json(_run(work), detail_level)


@model_app.command("resilience")
def inventory_resilience(
    path: Path = typer.Option(
        ..., "--path", help="Project directory to scan for resilience signals."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Static resilience scan (timeouts, retries, pools, breaker/shutdown/
    idempotency declarations) — heuristic, blind spots named."""

    def work() -> dict[str, object]:
        from apiforge.adapters.resilience import extract_resilience

        if not path.is_dir():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(path))
        inventory = extract_resilience(path)
        return {
            "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
            "facts": [f.model_dump(mode="json") for f in inventory.facts],
            "framework": inventory.framework,
            "input_hashes": dict(inventory.input_hashes),
        }

    _echo_json(_run(work), detail_level)


@model_app.command("redis")
def inventory_redis(
    path: Path = typer.Option(
        ..., "--path", help="Project directory to scan for Redis/Valkey calls."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Static extraction of Redis/Valkey call sites + DataAccessIR — offline."""

    def work() -> dict[str, object]:
        from apiforge.adapters.redis_.extract import extract_redis
        from apiforge.adapters.redis_.ir import build_data_access_ir

        if not path.is_dir():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(path))
        inventory = extract_redis(path)
        return {
            "data_access_ir": build_data_access_ir(inventory).model_dump(mode="json"),
            "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
            "facts": [f.model_dump(mode="json") for f in inventory.facts],
            "framework": inventory.framework,
            "input_hashes": dict(inventory.input_hashes),
        }

    _echo_json(_run(work), detail_level)


_DATA_ACCESS_READERS = {
    "rds-access": (
        "apiforge.adapters.relational.extract_rds_access",
        "rds",
        "rds",
        "Project directory to scan for PostgreSQL/MySQL/Aurora relational access.",
    ),
    "postgres-access": (
        "apiforge.adapters.relational.extract_postgres",
        "postgres",
        "postgres",
        "Project directory to scan for PostgreSQL access.",
    ),
    "mysql-access": (
        "apiforge.adapters.relational.extract_mysql",
        "mysql",
        "mysql",
        "Project directory to scan for MySQL/MariaDB access.",
    ),
    "elasticache-access": (
        "apiforge.adapters.redis_.extract.extract_elasticache",
        "elasticache",
        "elasticache",
        "Project directory to scan for Redis-protocol calls on ElastiCache.",
    ),
    "mongo": (
        "apiforge.adapters.dbaccess.extract_mongo",
        "mongodb|documentdb",
        "mongodb",
        "Project directory to scan for MongoDB/DocumentDB calls.",
    ),
    "dynamodb-access": (
        "apiforge.adapters.dbaccess.extract_dynamo_access",
        "dynamodb",
        "dynamodb",
        "Project directory to scan for DynamoDB data-plane calls.",
    ),
    "neptune-access": (
        "apiforge.adapters.dbaccess.extract_neptune_access",
        "neptune",
        "neptune",
        "Project directory to scan for Neptune gremlin/cypher/SPARQL calls.",
    ),
}


def _register_data_access_models() -> None:
    """`model <db>-access` — source-tree scan + DataAccessIR, offline."""

    def make(dotted: str, provider: str, database: str) -> Callable[..., None]:
        def cmd(
            path: Path = typer.Option(..., "--path", help="Project directory."),
            detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
        ) -> None:
            def work() -> dict[str, object]:
                import importlib

                from apiforge.adapters.redis_.ir import build_data_access_ir

                if not path.is_dir():
                    raise AnalysisError("AF-INPUT-NOT-FOUND", str(path))
                module, _, func = dotted.rpartition(".")
                inventory = getattr(importlib.import_module(module), func)(path)
                return {
                    "data_access_ir": build_data_access_ir(
                        inventory, database=database, provider=provider
                    ).model_dump(mode="json"),
                    "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
                    "facts": [f.model_dump(mode="json") for f in inventory.facts],
                    "framework": inventory.framework,
                    "input_hashes": dict(inventory.input_hashes),
                }

            _echo_json(_run(work), detail_level)

        return cmd

    for name, (dotted, provider, database, _help) in _DATA_ACCESS_READERS.items():
        model_app.command(name)(make(dotted, provider, database))


_register_data_access_models()


_STREAMING_READERS = {
    "kafka-access": (
        "apiforge.adapters.streaming.extract_kafka",
        "kafka",
        "kafka|msk",
        "Project directory to scan for Kafka producer/consumer access.",
    ),
    "msk-access": (
        "apiforge.adapters.streaming.extract_msk_access",
        "msk",
        "aws-msk",
        "Project directory to scan for Kafka access declared for Amazon MSK.",
    ),
}


def _register_streaming_models() -> None:
    def make(dotted: str, broker: str, provider: str, help_text: str) -> Callable[..., None]:
        def cmd(
            path: Path = typer.Option(..., "--path", help=help_text),
            detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
        ) -> None:
            def work() -> dict[str, object]:
                import importlib

                from apiforge.adapters.streaming import build_streaming_ir

                if not path.is_dir():
                    raise AnalysisError("AF-INPUT-NOT-FOUND", str(path))
                module, _, func = dotted.rpartition(".")
                inventory = getattr(importlib.import_module(module), func)(path)
                return {
                    "streaming_access_ir": build_streaming_ir(
                        inventory, broker=broker, provider=provider
                    ).model_dump(mode="json"),
                    "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
                    "facts": [f.model_dump(mode="json") for f in inventory.facts],
                    "framework": inventory.framework,
                    "input_hashes": dict(inventory.input_hashes),
                }

            _echo_json(_run(work), detail_level)

        return cmd

    for name, (dotted, broker, provider, help_text) in _STREAMING_READERS.items():
        model_app.command(name)(make(dotted, broker, provider, help_text))


_register_streaming_models()


_MESSAGING_READERS = {
    "sqs-access": ("apiforge.adapters.messaging.extract_sqs", "sqs", "AWS SQS"),
    "sns-access": ("apiforge.adapters.messaging.extract_sns", "sns", "AWS SNS"),
    "eventbridge-access": ("apiforge.adapters.messaging.extract_eventbridge", "eventbridge", "AWS EventBridge"),
    "kinesis-access": ("apiforge.adapters.messaging.extract_kinesis", "kinesis", "AWS Kinesis"),
}


def _register_messaging_models() -> None:
    def make(dotted: str, service: str, help_text: str) -> Callable[..., None]:
        def cmd(
            path: Path = typer.Option(..., "--path", help=help_text),
            detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
        ) -> None:
            def work() -> dict[str, object]:
                import importlib

                from apiforge.adapters.messaging import build_messaging_ir

                if not path.is_dir():
                    raise AnalysisError("AF-INPUT-NOT-FOUND", str(path))
                module, _, func = dotted.rpartition(".")
                inventory = getattr(importlib.import_module(module), func)(path)
                return {
                    "messaging_access_ir": build_messaging_ir(
                        inventory, service=service
                    ).model_dump(mode="json"),
                    "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
                    "facts": [f.model_dump(mode="json") for f in inventory.facts],
                    "framework": inventory.framework,
                    "input_hashes": dict(inventory.input_hashes),
                }

            _echo_json(_run(work), detail_level)

        return cmd

    for name, (dotted, service, help_text) in _MESSAGING_READERS.items():
        model_app.command(name)(make(dotted, service, help_text))


_register_messaging_models()


_ANALYTICAL_READERS = {
    "opensearch-access": ("apiforge.adapters.analytical.extract_opensearch", "opensearch", "OpenSearch/Elasticsearch"),
    "redshift-access": ("apiforge.adapters.analytical.extract_redshift", "redshift", "Amazon Redshift"),
}


def _register_analytical_models() -> None:
    def make(dotted: str, engine: str, help_text: str) -> Callable[..., None]:
        def cmd(
            path: Path = typer.Option(..., "--path", help=help_text),
            detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
        ) -> None:
            def work() -> dict[str, object]:
                import importlib

                from apiforge.adapters.analytical import build_analytical_ir

                if not path.is_dir():
                    raise AnalysisError("AF-INPUT-NOT-FOUND", str(path))
                module, _, func = dotted.rpartition(".")
                inventory = getattr(importlib.import_module(module), func)(path)
                return {
                    "analytical_access_ir": build_analytical_ir(
                        inventory, engine=engine
                    ).model_dump(mode="json"),
                    "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
                    "facts": [f.model_dump(mode="json") for f in inventory.facts],
                    "framework": inventory.framework,
                    "input_hashes": dict(inventory.input_hashes),
                }

            _echo_json(_run(work), detail_level)

        return cmd

    for name, (dotted, engine, help_text) in _ANALYTICAL_READERS.items():
        model_app.command(name)(make(dotted, engine, help_text))


_register_analytical_models()


@model_app.command("otel")
def inventory_otel(
    path: Path = typer.Option(..., "--path", help="OTLP/JSON trace export from an OTel collector."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """OTel export -> perf.otel.* facts + a PerformanceRun — offline."""

    def work() -> dict[str, object]:
        from apiforge.adapters.otel.extract import extract_otel
        from apiforge.adapters.otel.run import build_performance_run

        if not path.is_file():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(path))
        inventory = extract_otel(path)
        return {
            "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
            "facts": [f.model_dump(mode="json") for f in inventory.facts],
            "framework": inventory.framework,
            "input_hashes": dict(inventory.input_hashes),
            "performance_run": build_performance_run(inventory, path.name).model_dump(mode="json"),
        }

    _echo_json(_run(work), detail_level)


def _load_repeat_baselines(directory: Path | None) -> tuple[PerformanceRun, ...]:
    """Every ``*.json`` in the dir is a repeated baseline run — or named."""
    if directory is None:
        return ()
    if not directory.is_dir():
        raise AnalysisError("AF-PERF-RUN-INVALID", f"{directory}: not a directory")
    runs = tuple(_load_performance_run(p) for p in sorted(directory.glob("*.json")))
    return runs


@perf_app.command("compare")
def perf_compare(
    baseline: Path = typer.Option(
        ..., "--baseline", help="PerformanceRun JSON (or `model otel` payload)."
    ),
    candidate: Path = typer.Option(
        ..., "--candidate", help="PerformanceRun JSON (or `model otel` payload)."
    ),
    threshold_pct: float = typer.Option(
        10.0, "--threshold-pct", help="Regression threshold — declared, never assumed."
    ),
    min_samples: int = typer.Option(
        3, "--min-samples", help="Minimum span count per operation to be judged."
    ),
    repeat_baseline: Path | None = typer.Option(
        None,
        "--repeat-baseline",
        help="Dir of repeated baseline runs — measures the noise floor.",
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """compare_runs / detect_regression over two PerformanceRun payloads."""

    def work() -> object:
        from apiforge.perf.compare import compare_runs

        base = _load_performance_run(baseline)
        cand = _load_performance_run(candidate)
        return compare_runs(
            base,
            cand,
            threshold_pct=threshold_pct,
            min_samples=min_samples,
            repeat_baselines=_load_repeat_baselines(repeat_baseline),
        ).model_dump(mode="json")

    _echo_json(_run(work), detail_level)


@perf_app.command("verdict")
def perf_verdict(
    run: Path = typer.Option(..., "--run", help="PerformanceRun JSON (or `model otel` payload)."),
    repeat_baseline: Path | None = typer.Option(
        None,
        "--repeat-baseline",
        help="Dir of repeated baseline runs — deltas inside the measured "
        "noise floor make the verdict inconclusive.",
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """passed / failed / inconclusive over a run — conditions named, never guessed."""

    def work() -> object:
        from apiforge.perf.verdict import verdict

        return verdict(
            _load_performance_run(run),
            repeat_baselines=_load_repeat_baselines(repeat_baseline),
        ).model_dump(mode="json")

    _echo_json(_run(work), detail_level)


memory_app = typer.Typer(help="Append-only PerformanceRun memory — local store.")
perf_app.add_typer(memory_app, name="memory")


@memory_app.command("add")
def perf_memory_add(
    run: Path = typer.Option(..., "--run", help="PerformanceRun JSON to persist."),
    root: Path = typer.Option(Path("."), "--root", help="Workspace root."),
    recorded_at: str | None = typer.Option(
        None, "--recorded-at", help="Explicit timestamp; the only clock source."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Append a run to .apiforge/perf/runs.jsonl — payload hash recorded."""

    def work() -> object:
        from apiforge.perf.run_store import add_run

        return add_run(root, _load_performance_run(run), recorded_at=recorded_at)

    _echo_json(_run(work), detail_level)


@memory_app.command("search")
def perf_memory_search(
    subject: str | None = typer.Option(None, "--subject"),
    tool: str | None = typer.Option(None, "--tool"),
    since: str | None = typer.Option(None, "--since", help="ISO-8601 lower bound on recorded_at."),
    root: Path = typer.Option(Path("."), "--root", help="Workspace root."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """search_performance_memory — filters declared fields, never infers."""

    def work() -> object:
        from apiforge.perf.run_store import search_runs

        return {
            "count": len(search_runs(root, subject=subject, tool=tool, since=since)),
            "runs": search_runs(root, subject=subject, tool=tool, since=since),
        }

    _echo_json(_run(work), detail_level)


@perf_app.command("suggest")
def perf_suggest(
    case: Path | None = typer.Option(
        None, "--case", help="Case dir — reads findings.json inside it."
    ),
    findings: Path | None = typer.Option(
        None, "--findings", help="Findings JSON (list or {findings: []})."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """suggest_fix — emits an ActionPlan; never applies it."""

    def work() -> object:
        from apiforge.core.models import Finding
        from apiforge.perf.suggest import suggest_fix

        source = findings or (case / "findings.json" if case else None)
        if source is None or not Path(source).is_file():
            raise AnalysisError(
                "AF-PERF-SUGGEST-INPUT",
                "pass --case <dir> (reads findings.json) or --findings <file>",
            )
        try:
            doc = json.loads(Path(source).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AnalysisError("AF-PERF-SUGGEST-INPUT", f"{source}: {exc}") from exc
        payload = doc if isinstance(doc, list) else doc.get("findings", [])
        try:
            parsed = [Finding.model_validate(f) for f in payload]
        except Exception as exc:
            raise AnalysisError("AF-PERF-SUGGEST-INPUT", f"{source}: {exc}") from exc
        return suggest_fix(parsed).model_dump(mode="json")

    _echo_json(_run(work), detail_level)


@perf_app.command("scenario")
def perf_scenario(
    tool: str = typer.Option(..., "--tool", help="k6 | jmeter | locust."),
    scenario: Path = typer.Option(
        ..., "--scenario", help="Declared scenario JSON (endpoints, rps, duration)."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Generate the tool's script for a declared scenario — never executes it."""

    def work() -> object:
        from apiforge.perf.scenario import generate_scenario
        from apiforge.run_tools import RunError

        try:
            spec = json.loads(scenario.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AnalysisError("AF-SCENARIO-SCHEMA", f"{scenario}: {exc}") from exc
        try:
            return generate_scenario(tool, spec)
        except RunError as exc:
            raise AnalysisError(exc.code, str(exc).split(": ", 1)[-1]) from exc

    _echo_json(_run(work), detail_level)


@perf_app.command("plan")
def perf_plan(
    subject: str = typer.Option(..., "--subject"),
    endpoint: list[str] = typer.Option(..., "--endpoint"),
    target_tps: float = typer.Option(..., "--target-tps", min=0.0001),
    test_kind: str = typer.Option("load", "--test-kind"),
    duration_s: int = typer.Option(60, "--duration-s", min=1),
    max_p99_ms: float = typer.Option(500, "--max-p99-ms", min=0.001),
    max_error_rate: float = typer.Option(0.01, "--max-error-rate", min=0, max=1),
    generator: str = typer.Option("k6", "--generator"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Create a declarative load plan; generation never executes a tool."""
    from apiforge.perf_control import build_plan

    try:
        result = build_plan(
            subject,
            tuple(endpoint),
            target_tps=target_tps,
            test_kind=test_kind,
            duration_s=duration_s,
            max_p99_ms=max_p99_ms,
            max_error_rate=max_error_rate,
            generator=generator,
        )
    except (TypeError, ValueError) as exc:
        raise AnalysisError("AF-PERF-PLAN-INVALID", str(exc)) from exc
    _echo_json(result.model_dump(mode="json"), detail_level)


@perf_app.command("chaos")
def perf_chaos(
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """List the declared controlled failure-injection scenarios (CHAOS-001..013).

    Each scenario names the fault, the expected signal, the blast-radius
    guard and the evidence a run must produce — injection itself is never
    executed by API Forge."""

    def work() -> object:
        from apiforge.perf.chaos import list_scenarios

        return {"scenarios": list_scenarios()}

    _echo_json(_run(work), detail_level)


def _load_performance_run(path: Path) -> PerformanceRun:
    """Accept a bare PerformanceRun or the `model otel` payload wrapping one."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise AnalysisError("AF-PERF-RUN-INVALID", f"{path}: {exc}") from exc
    if isinstance(payload, dict) and isinstance(payload.get("performance_run"), dict):
        payload = payload["performance_run"]
    try:
        return PerformanceRun.model_validate(payload)
    except Exception as exc:
        raise AnalysisError("AF-PERF-RUN-INVALID", f"{path}: {exc}") from exc


@plan_app.command("strangler")
def plan_strangler(
    baseline: Path = typer.Option(..., "--baseline", help="facts.json from the legacy surface."),
    candidate: Path = typer.Option(
        ..., "--candidate", help="facts.json from the new implementation."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Per-route strangler cut plan over two code inventories."""

    def work() -> object:
        from apiforge.plan.strangler import strangler_plan

        base = _load_facts(baseline)
        cand = _load_facts(candidate)
        if not any(f.kind == "code.route" for f in (*base, *cand)):
            raise AnalysisError("AF-PLAN-NO-ROUTES", "neither payload carries code.route facts")
        return strangler_plan(base, cand)

    _echo_json(_run(work), detail_level)


@plan_app.command("architecture")
def plan_architecture(
    profile: Path = typer.Option(
        ..., "--profile", help="WorkloadProfile JSON — every field declared."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Architecture Decision Engine — rank AWS primitives per role.

    Eliminates on declared hard constraints, scores survivors on the
    profile, and emits chosen + rejected-with-reason + change conditions.
    """

    def work() -> object:
        from apiforge.contracts.stubs import WorkloadProfile
        from apiforge.plan.architecture import recommend

        try:
            payload = json.loads(profile.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AnalysisError("AF-PLAN-PROFILE-INVALID", f"{profile}: {exc}") from exc
        if isinstance(payload, dict) and isinstance(payload.get("workload_profile"), dict):
            payload = payload["workload_profile"]
        try:
            wp = WorkloadProfile.model_validate(payload)
        except Exception as exc:
            raise AnalysisError("AF-PLAN-PROFILE-INVALID", f"{profile}: {exc}") from exc
        return recommend(wp)

    _echo_json(_run(work), detail_level)


@debate_app.command("open")
def debate_open(
    case: Path = typer.Option(..., "--case", help="Case directory."),
    question: str = typer.Option(..., "--question", help="What is disputed."),
    sides: str = typer.Option(..., "--sides", help="Comma-separated side names."),
    now: str = typer.Option(..., "--now", help="ISO8601 timestamp — the only clock."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Open a debate over a question with named sides."""

    def work() -> object:
        from apiforge.debate.service import open_debate

        parts = tuple(s.strip() for s in sides.split(",") if s.strip())
        d = open_debate(case, question, parts, now)
        return {"debate_id": d.debate_id, "status": d.status, "sides": list(d.sides)}

    _echo_json(_run(work), detail_level)


@debate_app.command("submit")
def debate_submit(
    case: Path = typer.Option(..., "--case", help="Case directory."),
    debate: str = typer.Option(..., "--debate", help="Debate id."),
    side: str = typer.Option(..., "--side", help="Which side this position serves."),
    position: str = typer.Option(..., "--position", help="The position text."),
    evidence: str = typer.Option(..., "--evidence", help="Comma-separated fact_id citations."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Append a position — every position must cite fact_id evidence."""

    def work() -> object:
        from apiforge.debate.service import submit

        ev = tuple(e.strip() for e in evidence.split(",") if e.strip())
        d = submit(case, debate, side, position, ev)
        return {"debate_id": d.debate_id, "submissions": len(d.submissions)}

    _echo_json(_run(work), detail_level)


@debate_app.command("close")
def debate_close(
    case: Path = typer.Option(..., "--case", help="Case directory."),
    debate: str = typer.Option(..., "--debate", help="Debate id."),
    referee: str = typer.Option(..., "--referee", help="Who closes the debate."),
    decision: str | None = typer.Option(
        None, "--decision", help="The decision; omit to record unresolved."
    ),
    now: str = typer.Option(..., "--now", help="ISO8601 timestamp."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Close as resolved (--decision) or unresolved (no --decision)."""

    def work() -> object:
        from apiforge.debate.service import close

        d = close(case, debate, referee, decision, now)
        return {
            "debate_id": d.debate_id,
            "status": d.status,
            "decision": d.decision,
            "referee": d.referee,
        }

    _echo_json(_run(work), detail_level)


@dispatch_app.command("run")
def dispatch_run(
    coordinator: str = typer.Option(..., "--coordinator", help="Coordinator name."),
    case: Path = typer.Option(..., "--case", help="Case directory."),
    project: Path | None = typer.Option(None, "--project"),
    contract: Path | None = typer.Option(None, "--contract"),
    baseline: Path | None = typer.Option(None, "--baseline"),
    candidate: Path | None = typer.Option(None, "--candidate"),
    input_path: Path | None = typer.Option(
        None, "--input-path", help="Dump/report/template path for model verbs."
    ),
    findings: Path | None = typer.Option(None, "--findings"),
    rule_id: str | None = typer.Option(None, "--rule-id"),
    tool: str | None = typer.Option(
        None, "--tool", help="Tool selection for verbs that need one (perf scenario)."
    ),
    now: str | None = typer.Option(None, "--now", help="ISO8601 — the only clock."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Run a coordinator's playbook; pending steps name their missing inputs."""

    def work() -> object:
        from apiforge.dispatch.runner import DispatchContext, run_playbook

        ctx = DispatchContext(
            case=case,
            project=project,
            contract=contract,
            baseline=baseline,
            candidate=candidate,
            input_path=input_path,
            findings=findings,
            rule_id=rule_id,
            tool=tool,
            now=now,
        )
        return run_playbook(coordinator, ctx)

    _echo_json(_run(work), detail_level)


@agents_app.command("sync")
def agents_sync(
    root: Path = typer.Option(Path("."), "--root", help="Repository root."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Regenerate `.agents/agents/` + `.claude/agents/` from `agents/*.md`."""

    def work() -> object:
        from apiforge.dispatch.mirrors import sync_mirrors

        return sync_mirrors(Path(root).resolve())

    _echo_json(_run(work), detail_level)


@agents_app.command("check")
def agents_check(
    root: Path = typer.Option(Path("."), "--root", help="Repository root."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Report mirror drift — the release gate fails on the same check."""

    def work() -> object:
        from apiforge.dispatch.mirrors import mirror_drift

        drift = mirror_drift(Path(root).resolve())
        return {"drift": drift, "ok": not drift}

    _echo_json(_run(work), detail_level)


@run_app.command("tool")
def run_tool_cmd(
    tool: str = typer.Argument(..., help="Allowlisted tool: semgrep|trivy|gitleaks|k6."),
    target: Path = typer.Option(..., "--target", help="Path the tool scans."),
    out: Path = typer.Option(..., "--out", help="Report file the tool writes."),
    config: str | None = typer.Option(
        None, "--config", help="Tool config (semgrep requires a local rules path)."
    ),
    timeout: int = typer.Option(300, "--timeout", help="Seconds before the run is refused."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print argv; execute nothing."),
    approve: str | None = typer.Option(
        None,
        "--approve",
        help="Approval reference required when a load script targets a remote or "
        "unresolvable URL (policy gate `sensitive`).",
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Execute a scanner binary (fixed argv, no shell) and read its report."""

    def work() -> dict[str, object]:
        from apiforge.run_tools import RunError, run_tool

        try:
            extra = {"config": config} if config else {}
            return run_tool(tool, target, out, extra, timeout, dry_run=dry_run, approval=approve)
        except RunError as exc:
            raise AnalysisError(exc.code, str(exc).split(": ", 1)[-1]) from exc

    _echo_json(_run(work), detail_level)


@run_app.command("list")
def run_list(
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """The tool registry — declared metadata plus *measured* install status."""

    def work() -> dict[str, object]:
        from apiforge.run_tools import list_tools

        return {"tools": list_tools()}

    _echo_json(_run(work), detail_level)


@contract_app.command("list")
def contract_list(
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """List the registered canonical contracts."""

    def work() -> dict[str, object]:
        from apiforge.contracts.registry import contract_names

        return {"contracts": contract_names()}

    _echo_json(_run(work), detail_level)


@contract_app.command("show")
def contract_show(
    name: str = typer.Argument(..., help="Contract name, e.g. TaskSpec/v1."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Emit the JSON schema of a canonical contract."""

    def work() -> dict[str, object]:
        from apiforge.contracts.base import ContractError
        from apiforge.contracts.registry import contract_schema

        try:
            return contract_schema(name)
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_json(_run(work), detail_level)


def _task_root(root: Path | None) -> Path:
    return root if root is not None else Path.cwd()


@task_app.command("create")
def task_create(
    task_id: str = typer.Argument(..., help="Task id (lowercase, digits, hyphens)."),
    outcome: str = typer.Option(..., "--outcome", help="The single outcome."),
    spec_file: Path | None = typer.Option(
        None, "--spec", help="YAML/JSON TaskSpec to load instead of flags."
    ),
    input_: list[str] = typer.Option(
        [], "--input", help="field=path-or-value (project, contract, findings…)"
    ),
    writable: list[str] = typer.Option([], "--writable", help="Writable path glob."),
    strategy: str = typer.Option("direct", "--strategy", help="Recipe name."),
    risk: str = typer.Option("read_only", "--risk", help="Action class."),
    root: Path | None = typer.Option(None, "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Create a task in draft; sealed only after review."""

    def work() -> dict[str, object]:
        from apiforge.contracts.base import ContractError
        from apiforge.contracts.task import TaskSpec
        from apiforge.taskspec.service import create_task

        try:
            if spec_file is not None:
                import yaml

                data = yaml.safe_load(spec_file.read_text(encoding="utf-8"))
                data["id"] = task_id
                spec = TaskSpec.model_validate(data)
            else:
                spec = TaskSpec.model_validate(
                    {
                        "id": task_id,
                        "outcome": outcome,
                        "inputs": tuple(input_),
                        "writable_paths": tuple(writable),
                        "strategy": strategy,
                        "risk": risk,
                    }
                )
            created = create_task(_task_root(root), spec)
            return created.model_dump(mode="json")
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_json(_run(work), detail_level)


@task_app.command("review")
def task_review(
    task_id: str = typer.Argument(...),
    by: str = typer.Option(..., "--by", help="Reviewer identity."),
    set_: list[str] = typer.Option([], "--set", help="scalar field=value changes"),
    root: Path | None = typer.Option(None, "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Mark reviewed — any --set change bumps the revision, voiding seals."""

    def work() -> dict[str, object]:
        from apiforge.contracts.base import ContractError
        from apiforge.taskspec.service import review_task

        sets = dict(item.split("=", 1) for item in set_ if "=" in item)
        try:
            spec = review_task(_task_root(root), task_id, by, sets)
            return spec.model_dump(mode="json")
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_json(_run(work), detail_level)


@task_app.command("seal")
def task_seal(
    task_id: str = typer.Argument(...),
    key: Path = typer.Option(..., "--key", help="Ed25519 private PEM."),
    by: str = typer.Option(..., "--by"),
    root: Path | None = typer.Option(None, "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Seal the current revision — key possession, never identity."""

    def work() -> dict[str, object]:
        from apiforge.contracts.base import ContractError
        from apiforge.taskspec.service import seal_task

        try:
            spec = seal_task(_task_root(root), task_id, key, by)
            return spec.model_dump(mode="json")
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_json(_run(work), detail_level)


@task_app.command("run")
def task_run(
    task_id: str = typer.Argument(...),
    by: str = typer.Option(..., "--by", help="Executor identity."),
    now: str | None = typer.Option(None, "--now", help="ISO8601 (only clock)."),
    root: Path | None = typer.Option(None, "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Run the recipe within budgets; ends awaiting supervision or named stop."""

    def work() -> dict[str, object]:
        from apiforge.contracts.base import ContractError
        from apiforge.taskspec.runner import run_task

        try:
            return run_task(_task_root(root), task_id, by, now=now)
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_json(_run(work), detail_level)


@task_app.command("accept")
def task_accept(
    task_id: str = typer.Argument(...),
    by: str = typer.Option(..., "--by", help="Acceptor — never the executor."),
    evidence: list[str] = typer.Option([], "--evidence"),
    notes: str = typer.Option("", "--notes"),
    root: Path | None = typer.Option(None, "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Accept a supervised run; the acceptor must differ from the executor."""

    def work() -> dict[str, object]:
        from apiforge.contracts.base import ContractError
        from apiforge.taskspec.runner import accept_task

        try:
            return accept_task(_task_root(root), task_id, by, tuple(evidence), notes)
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_json(_run(work), detail_level)


@task_app.command("reject")
def task_reject(
    task_id: str = typer.Argument(...),
    by: str = typer.Option(..., "--by"),
    reason: str = typer.Option(..., "--reason"),
    root: Path | None = typer.Option(None, "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Reject a supervised run back to reviewable state."""

    def work() -> dict[str, object]:
        from apiforge.contracts.base import ContractError
        from apiforge.taskspec.runner import reject_task

        try:
            spec = reject_task(_task_root(root), task_id, by, reason)
            return spec.model_dump(mode="json")
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_json(_run(work), detail_level)


@task_app.command("status")
def task_status_cmd(
    task_id: str = typer.Argument(...),
    root: Path | None = typer.Option(None, "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Task spec plus its append-only history."""

    def work() -> dict[str, object]:
        from apiforge.contracts.base import ContractError
        from apiforge.taskspec.runner import task_status

        try:
            return task_status(_task_root(root), task_id)
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_json(_run(work), detail_level)


@task_app.command("compile")
def task_compile(
    task_id: str = typer.Argument(...),
    outcome: str = typer.Option(..., "--outcome"),
    contract: Path = typer.Option(..., "--contract"),
    project: Path = typer.Option(..., "--project"),
    case: Path = typer.Option(..., "--case"),
    root: Path | None = typer.Option(None, "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Compile a local API intention into a verified TaskSpec draft."""

    def work() -> dict[str, object]:
        from apiforge.contracts.base import ContractError
        from apiforge.taskspec.compiler import compile_intent
        from apiforge.taskspec.service import create_task

        try:
            spec = compile_intent(
                task_id,
                outcome,
                contract=contract,
                project=project,
                case=case,
            )
            return create_task(_task_root(root), spec).model_dump(mode="json")
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_json(_run(work), detail_level)


@task_app.command("plan")
def task_plan_cmd(
    task_id: str = typer.Argument(...),
    root: Path | None = typer.Option(None, "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Bind a sealed TaskSpec to a closed persisted TaskPlan."""

    def work() -> dict[str, object]:
        from apiforge.contracts.base import ContractError
        from apiforge.taskspec.planner import plan_task

        try:
            return plan_task(_task_root(root), task_id).model_dump(mode="json")
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_json(_run(work), detail_level)


@task_app.command("holdout")
def task_holdout_cmd(
    project: Path = typer.Option(..., "--project"),
    contract: Path = typer.Option(..., "--contract"),
    manifest: Path = typer.Option(..., "--manifest"),
    root: Path | None = typer.Option(None, "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Run deterministic local mutations and report whether proofs detect them."""

    def work() -> dict[str, object]:
        from apiforge.contracts.base import ContractError
        from apiforge.verification.holdout import run_holdouts

        try:
            records = run_holdouts(_task_root(root), project, contract, manifest)
            return {"holdouts": [record.model_dump(mode="json") for record in records]}
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_json(_run(work), detail_level)


@task_app.command("verify")
def task_verify_cmd(
    task_id: str = typer.Argument(...),
    project: Path = typer.Option(..., "--project"),
    contract: Path = typer.Option(..., "--contract"),
    manifest: Path | None = typer.Option(None, "--manifest"),
    run_id: str = typer.Option("manual", "--run-id"),
    by: str = typer.Option("af-verifier", "--by"),
    root: Path | None = typer.Option(None, "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Run independent proof checks and persist a VerificationRecord."""

    def work() -> dict[str, object]:
        from apiforge.contracts.base import ContractError
        from apiforge.taskspec.planner import plan_task
        from apiforge.verification.holdout import run_holdouts
        from apiforge.verification.service import verify_task

        task_root = _task_root(root)
        try:
            plan_path = task_root / ".apiforge" / "tasks" / task_id / "plan.json"
            if not plan_path.is_file():
                plan_task(task_root, task_id)
            holdout = (
                run_holdouts(task_root, project, contract, manifest) if manifest is not None else ()
            )
            return verify_task(
                task_root,
                task_id,
                project=project,
                contract=contract,
                run_id=run_id,
                holdout=holdout,
                verified_by=by,
            ).model_dump(mode="json")
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_json(_run(work), detail_level)


@brief_app.command("show")
def brief_show(
    task_id: str = typer.Option(..., "--task", help="Task id to brief."),
    root: Path | None = typer.Option(None, "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Render the Outcome Brief for a task — DONE is refused, not advised."""

    def work() -> dict[str, object]:
        from apiforge.brief.render import brief_payload
        from apiforge.contracts.base import ContractError

        try:
            return brief_payload(_task_root(root), task_id)
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_json(_run(work), detail_level)


def _graph_work(fn: Callable[[], object]) -> object:
    from apiforge.contracts.base import ContractError

    try:
        return fn()
    except ContractError as exc:
        raise AnalysisError(exc.code, exc.detail) from exc


@graph_app.command("build")
def graph_build(
    case: Path = typer.Option(..., "--case", help="Case directory with case.json."),
    out: Path = typer.Option(..., "--out", help="Graph output directory."),
    tasks_root: Path | None = typer.Option(
        None, "--tasks-root", help="Root holding .apiforge/tasks for task nodes."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Populate nodes.jsonl/edges.jsonl from case artifacts — deterministic bytes."""

    def work() -> object:
        from apiforge.graph.build import build_graph

        return _graph_work(lambda: build_graph(case, out, tasks_root))

    _echo_json(_run(work), detail_level)


@graph_app.command("query")
def graph_query(
    graph: Path = typer.Option(..., "--graph", help="Graph directory (nodes.jsonl)."),
    kind: str | None = typer.Option(None, "--kind", help="Filter nodes by kind."),
    edge_kind: str | None = typer.Option(None, "--edge", help="Filter edges by kind."),
    prop: list[str] = typer.Option([], "--prop", help="Node prop filter `k=v` (repeatable)."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Filter nodes/edges by closed vocabulary — no free text."""

    def work() -> object:
        from apiforge.graph.query import query_graph

        return _graph_work(
            lambda: query_graph(graph, kind=kind, edge_kind=edge_kind, prop=tuple(prop))
        )

    _echo_json(_run(work), detail_level)


@graph_app.command("impact")
def graph_impact(
    graph: Path = typer.Option(..., "--graph", help="Graph directory."),
    node: str = typer.Option(..., "--node", help="Node id whose dependents to list."),
    max_depth: int = typer.Option(4, "--max-depth"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Reverse traversal: everything that transitively depends on the node."""

    def work() -> object:
        from apiforge.graph.query import impact

        return _graph_work(lambda: impact(graph, node, max_depth=max_depth))

    _echo_json(_run(work), detail_level)


@graph_app.command("trace")
def graph_trace(
    graph: Path = typer.Option(..., "--graph", help="Graph directory."),
    from_id: str = typer.Option(..., "--from", help="Source node id."),
    to_id: str = typer.Option(..., "--to", help="Target node id."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Shortest directed path between two nodes; absent path is named."""

    def work() -> object:
        from apiforge.graph.query import trace

        return _graph_work(lambda: trace(graph, from_id, to_id))

    _echo_json(_run(work), detail_level)


@graph_app.command("coverage")
def graph_coverage(
    graph: Path = typer.Option(..., "--graph", help="Graph directory."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Structural gaps: unverified findings, unimplemented ops, unreferenced facts."""

    def work() -> object:
        from apiforge.graph.query import coverage

        return _graph_work(lambda: coverage(graph))

    _echo_json(_run(work), detail_level)


@graph_app.command("export")
def graph_export(
    graph: Path = typer.Option(..., "--graph", help="Graph directory."),
    out: Path = typer.Option(..., "--out", help="Export directory."),
    fmt: str = typer.Option("jsonl", "--format", help="jsonl (neptune is a named stub)."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Canonical copy plus export.json digests; `neptune` refuses as a named stub."""

    def work() -> object:
        from apiforge.graph.export import export_graph, export_summary

        return _graph_work(lambda: export_summary(export_graph(graph, out, fmt)))

    _echo_json(_run(work), detail_level)


@index_app.command("build")
def index_build(
    project: Path = typer.Option(..., "--project", help="Project root to index."),
    root: Path = typer.Option(Path("."), "--root", help="Root holding .apiforge/."),
    framework: str = typer.Option("auto", "--framework", help="fastapi|spring|go|auto."),
    findings: Path | None = typer.Option(
        None,
        "--findings",
        help="Case findings.json feeding the derived findings index.",
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Write the 12 index kinds under .apiforge/index/ (manifest lists all)."""

    def work() -> object:
        from apiforge.contracts.base import ContractError
        from apiforge.index.build import build_index

        try:
            return build_index(project, root, framework=framework, findings_path=findings)
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_json(_run(work), detail_level)


@index_app.command("status")
def index_status(
    project: Path = typer.Option(..., "--project", help="Project root to compare."),
    root: Path = typer.Option(Path("."), "--root", help="Root holding .apiforge/."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Name added/changed/removed source files against the built index."""

    def work() -> object:
        from apiforge.contracts.base import ContractError
        from apiforge.index.build import index_status as status

        try:
            return status(project, root)
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_json(_run(work), detail_level)


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
    transcript: Path | None = typer.Option(
        None, "--transcript", help="Host transcript JSONL; unlocks counted tokens."
    ),
    estimate: bool = typer.Option(
        False, "--estimate", help="Add a labeled chars/4 estimate (never counted)."
    ),
    cost_basis: Path | None = typer.Option(
        None, "--cost-basis", help="YAML model→rates; unlocks dollar cost."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Aggregate recorded call sizes; detail_level_effect shows what summary saves."""

    def work() -> dict[str, object]:
        from apiforge.economy.ledger import report
        from apiforge.economy.tokens import (
            TokenError,
            cost,
            estimate_tokens,
            read_transcript,
        )

        try:
            payload = report(root if root is not None else Path.cwd())
            if transcript is not None:
                counted = read_transcript(transcript)
                payload["tokens"] = counted
                payload["tokens_unresolved"] = False
                if cost_basis is not None:
                    payload["cost"] = cost(counted, cost_basis)
            elif cost_basis is not None:
                raise TokenError(
                    "AF-ECONOMY-TRANSCRIPT-MISSING",
                    "--cost-basis needs --transcript — no tokens to price",
                )
            if estimate:
                payload["token_estimate"] = estimate_tokens(int(payload["payload_bytes"]))
            return payload
        except TokenError as exc:
            raise AnalysisError(exc.code, str(exc).split(": ", 1)[-1]) from exc

    _echo_json(_run(work), detail_level)


@report_app.command("build")
def report_build(
    case_dir: Path = typer.Option(..., "--case", help="Persisted case directory."),
    receipt: Path | None = typer.Option(
        None, "--receipt", help="evidence receipt JSON to pin into the bundle."
    ),
    now: str | None = typer.Option(None, "--now", help="Explicit ISO8601 (only clock)."),
    out: Path | None = typer.Option(None, "--out", help="Write report.json here."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Compose the release evidence bundle for a case."""

    def work() -> dict[str, object]:
        from apiforge.report.bundle import ReportError, build_report, canonical

        try:
            report = build_report(case_dir, receipt_path=receipt, now=now)
        except ReportError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc
        if out is not None:
            out.write_text(canonical(report), encoding="utf-8")
        return report

    _echo_json(_run(work), detail_level)


@report_app.command("keygen")
def report_keygen(
    name: str = typer.Option(..., "--name", help="Key name (writes <name>.pem)."),
    keys_dir: Path = typer.Option(
        Path(".apiforge/keys"), "--keys-dir", help="Directory holding PEM keys."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Generate an Ed25519 keypair — proves key possession, never identity."""

    def work() -> dict[str, object]:
        from apiforge.report.bundle import ReportError
        from apiforge.report.keys import generate_keypair

        try:
            result: dict[str, object] = dict(generate_keypair(keys_dir, name))
            return result
        except ReportError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    _echo_json(_run(work), detail_level)


@report_app.command("sign")
def report_sign(
    report: Path = typer.Option(..., "--report", help="report.json to sign."),
    key: Path | None = typer.Option(
        None, "--key", help="Ed25519 private PEM — adds cryptographic binding."
    ),
    out: Path | None = typer.Option(None, "--out", help="Write signed report here."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Append the signature block binding body/evidence/catalog hashes."""

    def work() -> dict[str, object]:
        import json as _json

        from apiforge.report.bundle import canonical
        from apiforge.report.sign import sign_report

        if not report.is_file():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(report))
        if key is not None and not key.is_file():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(key))
        signed = sign_report(_json.loads(report.read_text(encoding="utf-8")), key_path=key)
        target = out if out is not None else report
        target.write_text(canonical(signed), encoding="utf-8")
        return signed

    _echo_json(_run(work), detail_level)


@report_app.command("verify")
def report_verify(
    report: Path = typer.Option(..., "--report", help="signed report.json."),
    receipt: Path | None = typer.Option(
        None, "--receipt", help="receipt file to re-hash for the evidence check."
    ),
    pubkey: Path | None = typer.Option(
        None, "--pubkey", help="Ed25519 public PEM to verify signature_b64."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Name which part diverged: signature_version|body|evidence|catalog|signature_crypto."""

    def work() -> dict[str, object]:
        import json as _json

        from apiforge.report.bundle import ReportError
        from apiforge.report.sign import verify_report

        if not report.is_file():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(report))
        if pubkey is not None and not pubkey.is_file():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(pubkey))
        try:
            return verify_report(
                _json.loads(report.read_text(encoding="utf-8")),
                receipt_path=receipt,
                pubkey_path=pubkey,
            )
        except ReportError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc

    result = _run(work)
    _echo_json(result, detail_level)
    if isinstance(result, dict) and result.get("ok") is False:
        raise typer.Exit(code=4)


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


@context_app.command("compact")
def context_compact(
    input_path: Path = typer.Option(..., "--input", help="UTF-8 command output artifact."),
    command: str = typer.Option("unknown", "--command", help="Logical command name."),
    mode: str = typer.Option("full", "--mode", help="Caveman mode: off|lite|full|ultra|wenyan."),
    max_lines: int | None = typer.Option(None, "--max-lines", min=1),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Compact a command artifact while preserving critical evidence."""

    def work() -> dict[str, object]:
        from apiforge.agentops.compact import compact_file
        from apiforge.economy.ledger import record_compaction

        try:
            result = compact_file(
                input_path,
                command=command,
                mode=mode,
                max_lines=max_lines,
            )
            record_compaction(Path.cwd(), result)
            return result.to_dict()
        except (FileNotFoundError, ValueError) as exc:
            raise AnalysisError("AF-COMPACT-INVALID", str(exc)) from exc

    _echo_json(_run(work), detail_level)


@agentops_app.command("filters")
def agentops_filters(
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """List closed command filters used by the RTK adapter."""
    from apiforge.agentops.filters import list_filters

    _echo_json(list_filters(), detail_level)


@agentops_app.command("workflows")
def agentops_workflows(
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """List deterministic Caveman-inspired API workflows."""
    from apiforge.agentops.workflows import list_workflows

    _echo_json(list_workflows(), detail_level)


@agentops_app.command("workflow")
def agentops_workflow(
    name: str = typer.Argument(..., help="Workflow name."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Render one workflow plan; execution remains governed by TaskSpec."""
    from apiforge.agentops.workflows import plan_workflow

    try:
        _echo_json(plan_workflow(name).to_dict(), detail_level)
    except ValueError as exc:
        _fail("AF-WORKFLOW-UNKNOWN", str(exc))


@agentops_app.command("hosts")
def agentops_hosts(
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """List host adapters for Claude, GPT/Codex, Devin and Copilot."""
    from apiforge.agentops.hosts import list_hosts

    _echo_json(list_hosts(), detail_level)


@agentops_app.command("native")
def agentops_native(
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Inspect repository-native Caveman/Cavekit assets and RTK configuration."""
    from apiforge.agentops.native import native_status

    _echo_json(native_status(Path.cwd()), detail_level)


@agentops_app.command("parity")
def agentops_parity(
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Audit host discovery and capability parity without invoking a host."""
    from apiforge.agentops.parity import audit_host_parity

    _echo_json(audit_host_parity(Path.cwd()), detail_level)


@agentops_app.command("activation-plan")
def agentops_activation_plan(
    host: str = typer.Option(..., "--host", help="claude, gpt-codex, devin or copilot."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Build a host activation plan; no host configuration is mutated."""
    from apiforge.agentops.activation import build_activation_plan

    try:
        result = build_activation_plan(host, str(Path.cwd()))
    except ValueError as exc:
        raise AnalysisError("AF-HOST-ACTIVATION-INVALID", str(exc)) from exc
    _echo_json(result.model_dump(mode="json"), detail_level)


@agentops_app.command("tools")
def agentops_tools(
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """List typed Tool Adapters and their safety/evidence metadata."""
    from apiforge.agentops.tools import list_tool_adapters

    _echo_json([item.to_dict() for item in list_tool_adapters()], detail_level)


@agentops_app.command("tool")
def agentops_tool(
    name: str = typer.Argument(...),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Inspect one Tool Adapter contract."""
    from apiforge.agentops.tools import get_tool_adapter

    try:
        _echo_json(get_tool_adapter(name).to_dict(), detail_level)
    except ValueError as exc:
        _fail("AF-TOOL-ADAPTER-UNKNOWN", str(exc))


@evals_app.command("list")
def evals_list(
    path: Path = typer.Option(Path("evals/cases/platform.yaml"), "--path"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """List declarative eval cases without executing agents."""
    from apiforge.evals.suite import list_case_dicts

    _echo_json(list_case_dicts(path), detail_level)


@evals_app.command("validate")
def evals_validate(
    path: Path = typer.Option(Path("evals/cases/platform.yaml"), "--path"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Validate closed eval vocabulary and mutation/holdout requirements."""
    from apiforge.evals.suite import load_cases

    try:
        cases = load_cases(path)
        ids = [case.case_id for case in cases]
        duplicate_ids = sorted({item for item in ids if ids.count(item) > 1})
        invalid = [case.case_id for case in cases if not case.required_evidence or case.mutation == "none"]
        result = {"ok": not duplicate_ids and not invalid, "cases": len(cases), "duplicate_ids": duplicate_ids, "invalid_cases": invalid}
    except (KeyError, OSError, TypeError, ValueError) as exc:
        raise AnalysisError("AF-EVALS-INVALID", str(exc)) from exc
    _echo_json(result, detail_level)


@contract_intel_app.command("impact")
def contract_intel_impact(
    protocol: str = typer.Option(..., "--protocol", help="openapi or grpc."),
    baseline: Path = typer.Option(..., "--baseline"),
    candidate: Path = typer.Option(..., "--candidate"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Classify compatibility and expose affected contract references."""
    try:
        result = analyze_contract(ContractProtocol(protocol), baseline, candidate)
    except (OSError, ValueError, TypeError) as exc:
        raise AnalysisError("AF-CONTRACT-INTEL-INVALID", str(exc)) from exc
    _echo_json(result.model_dump(mode="json"), detail_level)


@contract_intel_app.command("twin")
def contract_intel_twin(
    contract: Path = typer.Option(..., "--contract"),
    protocol: str = typer.Option(..., "--protocol", help="openapi or grpc."),
    dependency: list[str] = typer.Option([], "--dependency", help="Declared downstream dependency."),
    scenario: str | None = typer.Option(None, "--scenario", help="Simulate one scenario after planning."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Create a no-network Digital Twin plan and optionally simulate a scenario."""
    try:
        plan = build_twin_plan(contract, ContractProtocol(protocol), tuple(dependency))
        result: object = plan.model_dump(mode="json")
        if scenario is not None:
            result = {"plan": result, "simulation": simulate_twin(plan, scenario).model_dump(mode="json")}
    except (OSError, ValueError, TypeError) as exc:
        raise AnalysisError("AF-TWIN-INVALID", str(exc)) from exc
    _echo_json(result, detail_level)


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


@knowledge_app.command("list")
def knowledge_list(
    root: Path = typer.Option(Path("knowledge"), "--root", help="Directory of knowledge packs."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """List every pack with its areas, rules and verification date."""

    def work() -> dict[str, object]:
        from apiforge.contracts.base import ContractError
        from apiforge.knowledge.loader import load_packs

        try:
            packs = load_packs(root)
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc
        return {
            "packs": [
                {
                    "areas": list(p.areas),
                    "domain": p.domain,
                    "evals": len(p.evals),
                    "has_matrix": bool(p.matrix),
                    "rule_ids": list(p.rule_ids),
                    "sources": len(p.sources),
                    "verified": p.verified,
                }
                for p in packs.values()
            ],
            "count": len(packs),
        }

    _echo_json(_run(work), detail_level)


@knowledge_app.command("show")
def knowledge_show(
    domain: str = typer.Argument(..., help="Pack directory name, e.g. rest-design."),
    root: Path = typer.Option(Path("knowledge"), "--root", help="Directory of knowledge packs."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Print one pack: summary, source authority, matrix, declared evals."""

    def work() -> dict[str, object]:
        from apiforge.contracts.base import ContractError
        from apiforge.knowledge.loader import load_pack

        try:
            pack = load_pack(root / domain)
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc
        return {
            "areas": list(pack.areas),
            "domain": pack.domain,
            "evals": list(pack.evals),
            "matrix": list(pack.matrix),
            "rule_ids": list(pack.rule_ids),
            "sources": [s.__dict__ for s in pack.sources],
            "summary": pack.summary,
            "verified": pack.verified,
            "version": pack.version,
        }

    _echo_json(_run(work), detail_level)


@knowledge_app.command("check")
def knowledge_check(
    root: Path = typer.Option(Path("knowledge"), "--root", help="Directory of knowledge packs."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Validate every pack; exit 4 when any problem is named."""

    def work() -> dict[str, object]:
        from apiforge.contracts.base import ContractError
        from apiforge.knowledge.loader import check_packs

        try:
            result = check_packs(root)
        except ContractError as exc:
            raise AnalysisError(exc.code, exc.detail) from exc
        if not result["ok"]:
            raise AnalysisError(
                "AF-KNOW-CHECK",
                "pack problems: " + "; ".join(str(p) for p in result["problems"]),
            )
        return result

    _echo_json(_run(work), detail_level)


@runtime_app.command("run")
def runtime_run(
    task_id: str = typer.Argument(..., help="TaskSpec id to execute."),
    root: Path = typer.Option(Path("."), "--root", help="Project root."),
    policy: str = typer.Option("local-ci-safe", "--policy"),
    now: str | None = typer.Option(None, "--now", help="Deterministic timestamp for replay."),
    debate: bool = typer.Option(False, "--debate", help="Request a debate room."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Execute a sealed TaskSpec with the deterministic fake adapter."""

    def work() -> object:
        from apiforge.runtime.runner import run_runtime

        return run_runtime(root, task_id, policy_id=policy, now=now, requested_debate=debate)

    try:
        _echo_json(_run(work), detail_level)
    except ContractError as exc:
        _fail(exc.code, exc.detail)


@runtime_app.command("status")
def runtime_status_cmd(
    task_id: str = typer.Argument(...),
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Show the newest persisted runtime run."""
    from apiforge.runtime.runner import runtime_status

    _echo_json(runtime_status(root, task_id), detail_level)


@runtime_app.command("resume")
def runtime_resume(
    task_id: str = typer.Argument(...),
    root: Path = typer.Option(Path("."), "--root"),
    policy: str = typer.Option("local-ci-safe", "--policy"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Resume by replaying the TaskSpec through the bounded supervisor."""
    from apiforge.runtime.runner import resume_runtime

    _echo_json(resume_runtime(root, task_id, policy_id=policy), detail_level)


@runtime_app.command("debate")
def runtime_debate(
    task_id: str = typer.Argument(...),
    root: Path = typer.Option(Path("."), "--root"),
    policy: str = typer.Option("local-ci-safe", "--policy"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Request a debate room before the runtime makes a final decision."""
    from apiforge.runtime.runner import debate_runtime

    _echo_json(debate_runtime(root, task_id, policy_id=policy), detail_level)


@runtime_app.command("approve")
def runtime_approve(
    task_id: str = typer.Argument(...),
    run_id: str = typer.Argument(...),
    approver: str = typer.Option(..., "--approver"),
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Record a local human approval artifact for a runtime run."""
    from apiforge.runtime.runner import approve_runtime

    _echo_json(approve_runtime(root, task_id, run_id, approver), detail_level)


@runtime_app.command("control-create")
def runtime_control_create(
    task_id: str = typer.Argument(...),
    step: list[str] = typer.Option(..., "--step", help="Step or step=dependency1,dependency2; repeatable."),
    root: Path = typer.Option(Path("."), "--root"),
    max_parallel: int = typer.Option(4, "--max-parallel", min=1),
    max_calls: int = typer.Option(20, "--max-calls", min=1),
    max_retries: int = typer.Option(2, "--max-retries", min=0),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Create a persistent control-plane run without executing work."""
    from apiforge.runtime.control import ControlPlane

    steps: list[tuple[str, tuple[str, ...]]] = []
    for raw in step:
        name, separator, dependencies = raw.partition("=")
        steps.append((name, tuple(item for item in dependencies.split(",") if item) if separator else ()))
    try:
        result = ControlPlane(root).create(
            task_id,
            tuple(steps),
            max_parallel=max_parallel,
            max_calls=max_calls,
            max_retries=max_retries,
        )
    except ContractError as exc:
        _fail(exc.code, exc.detail)
    else:
        _echo_json(result, detail_level)


@runtime_app.command("control-plan")
def runtime_control_plan(
    run_id: str = typer.Argument(...),
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Show ready steps and dynamic parallel width."""
    from apiforge.runtime.control import ControlPlane

    _echo_json(ControlPlane(root).plan(run_id), detail_level)


@runtime_app.command("control-start")
def runtime_control_start(
    run_id: str = typer.Argument(...),
    step_id: str = typer.Argument(...),
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Claim one ready step and consume one bounded call."""
    from apiforge.runtime.control import ControlPlane

    try:
        result = ControlPlane(root).start(run_id, step_id)
    except ContractError as exc:
        _fail(exc.code, exc.detail)
    else:
        _echo_json(result, detail_level)


@runtime_app.command("control-complete")
def runtime_control_complete(
    run_id: str = typer.Argument(...),
    step_id: str = typer.Argument(...),
    result_json: str = typer.Option("{}", "--result", help="JSON result payload."),
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Complete a running step with a content-hashed result."""
    from apiforge.runtime.control import ControlPlane

    try:
        result = ControlPlane(root).complete(run_id, step_id, json.loads(result_json))
    except (ContractError, json.JSONDecodeError) as exc:
        _fail(getattr(exc, "code", "AF-CONTROL-RESULT"), str(exc))
    else:
        _echo_json(result, detail_level)


@runtime_app.command("control-cancel")
def runtime_control_cancel(
    run_id: str = typer.Argument(...),
    actor: str = typer.Option(..., "--actor"),
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Cancel a control-plane run and persist the actor."""
    from apiforge.runtime.control import ControlPlane

    _echo_json(ControlPlane(root).cancel(run_id, actor), detail_level)


@runtime_app.command("control-review")
def runtime_control_review(
    run_id: str = typer.Argument(...),
    reviewer: str = typer.Option(..., "--reviewer"),
    verdict: Literal["approved", "rejected", "review"] = typer.Option("review", "--verdict"),
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Close a completed plan through an independent review verdict."""
    from apiforge.runtime.control import ControlPlane

    try:
        result = ControlPlane(root).review(run_id, reviewer, verdict)
    except ContractError as exc:
        _fail(exc.code, exc.detail)
    else:
        _echo_json(result, detail_level)


@grpc_app.command("analyze")
def grpc_analyze_cmd(
    source: Path = typer.Argument(..., help=".proto or descriptor source."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Build the canonical gRPC IR without invoking external toolchains."""
    from apiforge.grpc.source import load_source

    _echo_json(load_source(source), detail_level)


@grpc_app.command("discover")
def grpc_discover_cmd(
    source: Path = typer.Argument(..., help=".proto or descriptor source."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Discover a gRPC contract and expose its canonical IR."""
    from apiforge.grpc.source import load_source

    _echo_json(load_source(source), detail_level)


@grpc_app.command("diff")
def grpc_diff_cmd(
    baseline: Path = typer.Argument(...),
    candidate: Path = typer.Argument(...),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Classify protobuf evolution using deterministic compatibility rules."""
    from apiforge.grpc.compatibility import compare
    from apiforge.grpc.source import load_source

    _echo_json(compare(load_source(baseline), load_source(candidate)), detail_level)


@grpc_app.command("capabilities")
def grpc_capabilities_cmd(
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Show optional local gRPC toolchain capabilities."""
    from apiforge.grpc.capabilities import discover

    _echo_json({"capabilities": discover()}, detail_level)


@grpc_app.command("codegen")
def grpc_codegen_cmd(
    source: Path = typer.Argument(...),
    language: list[str] = typer.Option(["python"], "--language"),
    output_dir: Path = typer.Option(Path("generated"), "--output-dir"),
    tool: str = typer.Option("fake", "--tool"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Generate deterministic local artifacts or report missing toolchains."""
    from apiforge.contracts.grpc import GrpcCodegenRequest
    from apiforge.grpc.codegen import plan_codegen
    from apiforge.grpc.source import load_source

    target_languages = cast(tuple[Literal["python", "go", "java"], ...], tuple(language))
    target_tool = cast(Literal["fake", "protoc", "buf"], tool)
    request = GrpcCodegenRequest(languages=target_languages, output_dir=str(output_dir), tool=target_tool)
    _echo_json(plan_codegen(load_source(source), request), detail_level)


@grpc_app.command("gateway")
def grpc_gateway_cmd(
    source: Path = typer.Argument(...),
    gateway: list[str] = typer.Option(["openapi"], "--gateway"),
    output_dir: Path = typer.Option(Path("gateway"), "--output-dir"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Project the contract to local gateway artifacts."""
    from apiforge.contracts.grpc import GrpcGatewayRequest
    from apiforge.grpc.gateway import plan_gateway
    from apiforge.grpc.source import load_source

    target_gateways = cast(tuple[Literal["envoy", "grpc_gateway", "grpc_web", "openapi"], ...], tuple(gateway))
    request = GrpcGatewayRequest(gateways=target_gateways, output_dir=str(output_dir))
    _echo_json(plan_gateway(load_source(source), request), detail_level)


@grpc_app.command("verify")
def grpc_verify_cmd(
    source: Path = typer.Argument(...),
    baseline: Path | None = typer.Option(None, "--baseline"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Run independent local verification over a gRPC contract."""
    from apiforge.grpc.compatibility import compare
    from apiforge.grpc.source import load_source
    from apiforge.grpc.verify import verify

    candidate = load_source(source)
    compatibility = compare(load_source(baseline), candidate) if baseline else None
    _echo_json(verify(candidate, compatibility), detail_level)


@grpc_app.command("test")
def grpc_test_cmd(
    source: Path = typer.Argument(...),
    baseline: Path | None = typer.Option(None, "--baseline"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Run the offline contract test and independent verification gates."""
    from apiforge.grpc.compatibility import compare
    from apiforge.grpc.source import load_source
    from apiforge.grpc.verify import verify

    candidate = load_source(source)
    compatibility = compare(load_source(baseline), candidate) if baseline else None
    _echo_json({"tests": ["parse", "compatibility", "streaming", "security"], "verification": verify(candidate, compatibility)}, detail_level)


@grpc_app.command("benchmark")
def grpc_benchmark_cmd(
    run: Path = typer.Argument(..., help="JSON performance run."),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Evaluate RPS/TPS evidence without claiming capacity from invalid runs."""
    from apiforge.contracts.grpc import GrpcPerformanceRun
    from apiforge.grpc.performance import evaluate

    _echo_json(evaluate(GrpcPerformanceRun.model_validate(json.loads(run.read_text(encoding="utf-8")))), detail_level)


@migration_app.command("analyze")
def migration_analyze_cmd(
    project: Path = typer.Argument(..., help="Project root to inspect."),
    ecosystem: str = typer.Option(..., "--ecosystem", help="java, python or go."),
    source: str = typer.Option(..., "--source"),
    target: str = typer.Option(..., "--target"),
    matrix: Path | None = typer.Option(None, "--matrix"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Discover runtime migration impact without changing the project."""
    from apiforge.migration.contracts import Ecosystem, MigrationSpec
    from apiforge.migration.discovery import discover

    try:
        spec = MigrationSpec(
            project_root=str(project.resolve()),
            ecosystem=cast(Ecosystem, ecosystem),
            source_version=source,
            target_version=target,
        )
        result = discover(spec, matrix)
    except ContractError as exc:
        _fail(exc.code, exc.detail)
    _echo_json(result, detail_level)


@migration_app.command("plan")
def migration_plan_cmd(
    project: Path = typer.Argument(..., help="Project root to inspect."),
    ecosystem: str = typer.Option(..., "--ecosystem"),
    source: str = typer.Option(..., "--source"),
    target: str = typer.Option(..., "--target"),
    matrix: Path | None = typer.Option(None, "--matrix"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Build a closed migration TaskSpec and dependency DAG."""
    from apiforge.migration.contracts import Ecosystem, MigrationSpec
    from apiforge.migration.discovery import discover
    from apiforge.migration.planner import compile_plan

    try:
        spec = MigrationSpec(
            project_root=str(project.resolve()),
            ecosystem=cast(Ecosystem, ecosystem),
            source_version=source,
            target_version=target,
        )
        result = compile_plan(spec, discover(spec, matrix))
    except ContractError as exc:
        _fail(exc.code, exc.detail)
    _echo_json(result, detail_level)


@migration_app.command("verify")
def migration_verify_cmd(
    report: Path = typer.Argument(..., help="MigrationReport JSON."),
    evidence_ok: bool = typer.Option(False, "--evidence-ok"),
    verification_ok: bool = typer.Option(False, "--verification-ok"),
    contract_breaking: bool = typer.Option(False, "--contract-breaking"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Apply conservative status gates to a migration report."""
    from apiforge.migration.contracts import MigrationReport
    from apiforge.migration.verifier import verify_report

    try:
        payload = json.loads(report.read_text(encoding="utf-8"))
        result = verify_report(
            MigrationReport.model_validate(payload),
            evidence_ok=evidence_ok,
            verification_ok=verification_ok,
            contract_breaking=contract_breaking,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        _fail("AF-MIGRATION-REPORT", str(exc))
    _echo_json(result, detail_level)
