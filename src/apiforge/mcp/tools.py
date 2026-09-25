"""MCP tool bodies: call application services, project, record economy bytes.

Each function mirrors a CLI verb's payload exactly — same dicts, same
projection — so CLI and MCP answers cannot diverge. ``verb`` records as
``mcp:<name>`` in the economy ledger under ``Path.cwd()``.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Literal, TypeVar, cast

from apiforge.core.detail import apply_detail_level

T = TypeVar("T")


def _call(verb: str, fn: Callable[[], Any], detail_level: str) -> Any:
    value = fn()
    if isinstance(value, list):
        value = [v.model_dump(mode="json") if hasattr(v, "model_dump") else v for v in value]
    elif hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    elif is_dataclass(value):
        value = asdict(cast(Any, value))
    value = apply_detail_level(value, detail_level)
    from apiforge.economy.ledger import record

    record(
        Path.cwd(),
        verb=f"mcp:{verb}",
        detail_level=detail_level,
        payload_bytes=len(json.dumps(value, sort_keys=True).encode("utf-8")),
    )
    return value


def discover(project: str, detail_level: str = "normal") -> dict[str, Any]:
    """Statically inventory framework routes without executing code."""
    from apiforge.application.platform import ApiForgePlatform

    def work() -> dict[str, Any]:
        return ApiForgePlatform(Path.cwd()).discover(Path(project))

    out: dict[str, Any] = _call("discover", work, detail_level)
    return out


def analyze(
    contract: str,
    project: str,
    out_dir: str = ".apiforge",
    framework: str = "auto",
    baseline: str | None = None,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Run the full deterministic slice and persist a case."""
    from apiforge.application.platform import ApiForgePlatform

    def work() -> dict[str, Any]:
        result = ApiForgePlatform(Path.cwd()).analyze(
            Path(contract),
            Path(project),
            Path(out_dir),
            baseline=Path(baseline) if baseline else None,
            framework=framework,
        )
        return {
            "case_id": result.manifest.case_id,
            "out_dir": out_dir,
            "artifacts": {k: v.path for k, v in result.manifest.artifacts.items()},
            "operations": len(result.model.operations),
            "findings": len(result.findings),
            "changes": len(result.changes),
            "diagnostics": len(result.diagnostics),
        }

    out: dict[str, Any] = _call("analyze", work, detail_level)
    return out


def judge(contract: str, project: str, detail_level: str = "normal") -> list[Any]:
    """Judge contract/code divergence and return findings."""
    from apiforge.adapters.fastapi.extractor import extract_fastapi
    from apiforge.api_ir.builder import build_api_model
    from apiforge.openapi.loader import load_openapi
    from apiforge.rules.judge import judge_api_model

    def work() -> list[Any]:
        model = build_api_model(load_openapi(Path(contract)), extract_fastapi(Path(project)))
        return [f.model_dump(mode="json") for f in judge_api_model(model)]

    out: list[Any] = _call("judge", work, detail_level)
    return out


def model_build(contract: str, project: str, detail_level: str = "normal") -> dict[str, Any]:
    """Compose the API-IR from contract + code inventory."""
    from apiforge.adapters.fastapi.extractor import extract_fastapi
    from apiforge.api_ir.builder import build_api_model
    from apiforge.openapi.loader import load_openapi

    def work() -> Any:
        return build_api_model(load_openapi(Path(contract)), extract_fastapi(Path(project)))

    out: dict[str, Any] = _call("model_build", work, detail_level)
    return out


def model_api_gateway(path: str, detail_level: str = "normal") -> dict[str, Any]:
    """Read an API Gateway dump into facts — offline, no credentials."""
    from apiforge.adapters.apigateway.extract import extract_apigateway

    def work() -> dict[str, Any]:
        inventory = extract_apigateway(Path(path))
        return {
            "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
            "facts": [f.model_dump(mode="json") for f in inventory.facts],
            "framework": inventory.framework,
            "input_hashes": dict(inventory.input_hashes),
        }

    out: dict[str, Any] = _call("model_api_gateway", work, detail_level)
    return out


def diff_contract(baseline: str, candidate: str, detail_level: str = "normal") -> list[Any]:
    """Classify bounded breaking changes between two contracts."""
    from apiforge.openapi.diff import diff_contracts
    from apiforge.openapi.loader import load_openapi

    def work() -> list[Any]:
        return [
            c.model_dump(mode="json")
            for c in diff_contracts(load_openapi(Path(baseline)), load_openapi(Path(candidate)))
        ]

    out: list[Any] = _call("diff_contract", work, detail_level)
    return out


def next_step(findings: str, phase: str, detail_level: str = "normal") -> dict[str, Any]:
    """Recommend the specialist agent for the dominant finding area."""
    from apiforge.application.artifacts import load_findings
    from apiforge.application.next_step import next_step as route

    def work() -> Any:
        parsed = load_findings(Path(findings))
        return route(parsed, phase)

    out: dict[str, Any] = _call("next_step", work, detail_level)
    return out


def portable_inspect(root: str = ".", detail_level: str = "normal") -> dict[str, Any]:
    """Inspect installed assets and bounded local discovery."""
    from apiforge.application.portable import inspect

    return cast(dict[str, Any], _call("inspect", lambda: inspect(Path(root)), detail_level))


def portable_init(
    root: str = ".",
    workspace: bool = False,
    name: str | None = None,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Create a minimal project or workspace manifest locally."""
    from apiforge.application.portable import initialize

    return cast(
        dict[str, Any],
        _call("init", lambda: initialize(Path(root), workspace=workspace, name=name), detail_level),
    )


def portable_status(root: str = ".", detail_level: str = "normal") -> dict[str, Any]:
    """Return canonical project/workspace status."""
    from apiforge.application.portable import status

    return cast(dict[str, Any], _call("status", lambda: status(Path(root)), detail_level))


def portable_doctor(root: str = ".", detail_level: str = "normal") -> dict[str, Any]:
    """Return offline installation and optional capability diagnostics."""
    from apiforge.application.portable import doctor

    return cast(dict[str, Any], _call("doctor", lambda: doctor(Path(root)), detail_level))


def workspace_discover(root: str = ".", detail_level: str = "normal") -> dict[str, Any]:
    from apiforge.application.workspace import discover

    return cast(
        dict[str, Any], _call("workspace_discover", lambda: discover(Path(root)), detail_level)
    )


def workspace_status(root: str = ".", detail_level: str = "normal") -> dict[str, Any]:
    from apiforge.application.workspace import status

    return cast(dict[str, Any], _call("workspace_status", lambda: status(Path(root)), detail_level))


def workspace_add(repository: str, root: str = ".", detail_level: str = "normal") -> dict[str, Any]:
    from apiforge.application.workspace import add

    return cast(
        dict[str, Any],
        _call("workspace_add", lambda: add(Path(root), Path(repository)), detail_level),
    )


def context_resolve(
    root: str = ".",
    scope: str = "repo",
    target: str | None = None,
    impact: str | None = None,
    detail_level: str = "normal",
) -> dict[str, Any]:
    from apiforge.application.context import resolve_context

    return cast(
        dict[str, Any],
        _call(
            "context_resolve",
            lambda: resolve_context(Path(root), scope=scope, target=target, impact=impact),
            detail_level,
        ),
    )


def change_control_run(
    bundle: str,
    out_dir: str = ".apiforge/change-control",
    framework: str = "auto",
    phase: str = "verify",
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Run the read-only API/Git/CI change-control pipeline from a replay bundle."""
    from apiforge.application.change_control import run_change_control
    from apiforge.application.change_errors import ChangeControlError
    from apiforge.contracts.change_control import ChangeControlResult
    from apiforge.integrations.replay import ReplayAdapter

    def work() -> object:
        try:
            return run_change_control(
                ReplayAdapter().load(Path(bundle)),
                Path(out_dir),
                framework=framework,
                phase=phase,
            )
        except (ChangeControlError, OSError, ValueError) as exc:
            error_code = getattr(exc, "code", "AF-MCP-CHANGE-CONTROL")
            return ChangeControlResult(
                state="unresolved",
                status="failed",
                gaps=(str(exc),),
                error_code=error_code,
                payload={
                    "error_field": getattr(exc, "field", "change-control"),
                    "error_unlock": getattr(
                        exc,
                        "unlock",
                        "inspect the documented contract and rerun the verifier",
                    ),
                },
            )

    return cast(dict[str, Any], _call("change_control_run", work, detail_level))


def change_control_collect(
    repository: str,
    base_sha: str,
    head_sha: str,
    pull_number: int | None = None,
    contract: str | None = None,
    baseline: str | None = None,
    project: str | None = None,
    api_base: str = "https://api.github.com",
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Collect GitHub context with the GET-only adapter into a local bundle."""
    import os

    from apiforge.application.change_errors import ChangeControlError
    from apiforge.contracts.change_control import ChangeCollectRequest
    from apiforge.integrations.github import GitHubReadOnlyAdapter, UrllibReadOnlyTransport

    def work() -> object:
        try:
            token = os.environ.get("APIFORGE_GITHUB_READ_ONLY_TOKEN")
            if not token:
                raise ChangeControlError(
                    "AF-GITHUB-AUTH",
                    "read-only token is absent; use artifact replay",
                    field="APIFORGE_GITHUB_READ_ONLY_TOKEN",
                    unlock="provide a host-managed read-only token or use replay",
                )
            request = ChangeCollectRequest(
                repository=repository,
                base_sha=base_sha,
                head_sha=head_sha,
                pull_number=pull_number,
                contract=contract,
                baseline=baseline,
                project=project,
                api_base=api_base,
            )
            return GitHubReadOnlyAdapter(
                UrllibReadOnlyTransport(
                    api_base,
                    token=token,
                )
            ).collect(request)
        except (OSError, RuntimeError, ValueError) as exc:
            return {
                "capability_id": "git.read-context",
                "state": "unresolved",
                "status": "failed",
                "gaps": (str(exc),),
                "error_code": getattr(exc, "code", "AF-MCP-GITHUB-COLLECT"),
                "error_field": getattr(exc, "field", "github collection"),
                "error_unlock": getattr(
                    exc,
                    "unlock",
                    "inspect the provider evidence and retry through the read-only adapter",
                ),
            }

    return cast(dict[str, Any], _call("change_control_collect", work, detail_level))


def change_control_publish(
    run_dir: str,
    junit: str | None = None,
    markdown: str | None = None,
    sarif: str | None = None,
    html: str | None = None,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Publish a canonical change-control result to CI and host formats."""
    from apiforge.application.change_publishers import publish_change_control_reports

    return cast(
        dict[str, Any],
        _call(
            "change_control_publish",
            lambda: publish_change_control_reports(
                Path(run_dir),
                junit_path=Path(junit) if junit else None,
                markdown_path=Path(markdown) if markdown else None,
                sarif_path=Path(sarif) if sarif else None,
                html_path=Path(html) if html else None,
            ),
            detail_level,
        ),
    )


def change_control_surface(
    run_dir: str,
    surface: Literal["ide", "ui"] = "ide",
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Return the canonical result through the requested IDE/UI surface."""
    from apiforge.surfaces.change_control_host import surface_projection

    return cast(
        dict[str, Any],
        _call(
            "change_control_surface",
            lambda: surface_projection(Path(run_dir), surface),
            detail_level,
        ),
    )


def integration_github_issues(
    repository: str,
    state: str = "open",
    api_base: str = "https://api.github.com",
    max_age: int = 300,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Read GitHub issues through the GET-only adapter."""
    import os

    from apiforge.integrations.external import GitHubIssuesReadOnlyAdapter
    from apiforge.integrations.github import UrllibReadOnlyTransport

    return cast(
        dict[str, Any],
        _call(
            "integration_github_issues",
            lambda: GitHubIssuesReadOnlyAdapter(
                UrllibReadOnlyTransport(api_base, token=os.environ.get("GITHUB_TOKEN"))
            ).read(repository, state=state, max_age_seconds=max_age),
            detail_level,
        ),
    )


def integration_health(
    url: str,
    max_age: int = 60,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Read a remote health endpoint and return its freshness receipt."""
    import os

    from apiforge.integrations.external import adapter_for_url

    return cast(
        dict[str, Any],
        _call(
            "integration_health",
            lambda: adapter_for_url(url, token=os.environ.get("APIFORGE_HOST_TOKEN")).read(
                url, max_age_seconds=max_age
            ),
            detail_level,
        ),
    )


def integration_json(
    url: str,
    max_age: int = 300,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Read a generic external JSON endpoint without mutation."""
    import os
    from urllib.parse import urlsplit

    from apiforge.integrations.external import HttpJsonReadOnlyAdapter
    from apiforge.integrations.github import UrllibReadOnlyTransport

    parsed = urlsplit(url)
    return cast(
        dict[str, Any],
        _call(
            "integration_json",
            lambda: HttpJsonReadOnlyAdapter(
                UrllibReadOnlyTransport(
                    f"{parsed.scheme}://{parsed.netloc}",
                    token=os.environ.get("APIFORGE_EXTERNAL_READ_TOKEN"),
                    accept="application/json",
                )
            ).read(url, max_age_seconds=max_age),
            detail_level,
        ),
    )


def platform_verify_runtime(
    root: str = ".",
    verticals: tuple[str, ...] = (),
    now: str | None = None,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Execute the same allowlisted local vertical probes as the CLI."""
    from apiforge.application.platform_runtime import (
        VERTICALS,
        runtime_summary,
        verify_platform_runtime,
    )

    receipt = verify_platform_runtime(Path(root), verticals=verticals or VERTICALS, now=now)
    return cast(
        dict[str, Any],
        _call(
            "platform_verify_runtime",
            lambda: receipt.model_dump(mode="json") | {"summary": runtime_summary(receipt)},
            detail_level,
        ),
    )


def capabilities_list(
    capability_id: str | None = None,
    detail_level: str = "normal",
) -> list[Any]:
    """List the shared evidence-backed capability records."""
    from apiforge.capabilities.registry import load_capabilities

    def work() -> list[Any]:
        records = load_capabilities()
        selected = [
            item for item in records if capability_id is None or item.capability_id == capability_id
        ]
        return [item.model_dump(mode="json") for item in selected]

    return cast(list[Any], _call("capabilities_list", work, detail_level))


def capabilities_verify(detail_level: str = "normal") -> dict[str, Any]:
    """Verify public capability documentation and proof metadata."""
    from apiforge.capabilities.registry import load_capabilities
    from apiforge.capabilities.verify import verify_capabilities

    return cast(
        dict[str, Any],
        _call(
            "capabilities_verify",
            lambda: verify_capabilities(load_capabilities(), root=Path.cwd()),
            detail_level,
        ),
    )


def rules_list(area: str | None = None, detail_level: str = "normal") -> dict[str, Any]:
    """List rule ids, titles and severities by area."""
    from apiforge.rules.catalog import load_catalog

    def work() -> dict[str, Any]:
        by_area: dict[str, list[dict[str, str]]] = {}
        for rule_id, meta in sorted(load_catalog().items()):
            if area is not None and meta.area.upper() != area.upper():
                continue
            by_area.setdefault(meta.area, []).append(
                {"id": rule_id, "severity": meta.severity.value, "title": meta.title}
            )
        return {"areas": by_area, "count": sum(len(v) for v in by_area.values())}

    out: dict[str, Any] = _call("rules_list", work, detail_level)
    return out


def rules_lookup(rule_id: str, detail_level: str = "normal") -> dict[str, Any]:
    """Print one rule's full guidance."""
    from apiforge.application.analyze import AnalysisError
    from apiforge.rules.catalog import load_catalog

    def work() -> dict[str, Any]:
        meta = load_catalog().get(rule_id.upper())
        if meta is None:
            raise AnalysisError("AF-RULE-NOT-FOUND", f"no rule {rule_id!r} in the catalog")
        return meta.model_dump(mode="json") | {"id": rule_id.upper()}

    out: dict[str, Any] = _call("rules_lookup", work, detail_level)
    return out


def playbook(coordinator: str, detail_level: str = "normal") -> dict[str, Any]:
    """Render the declared executor decomposition for a coordinator."""
    from apiforge.application.analyze import AnalysisError
    from apiforge.rules.catalog import load_playbooks

    def work() -> dict[str, Any]:
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

    out: dict[str, Any] = _call("playbook", work, detail_level)
    return out


def economy_report(root: str = ".", detail_level: str = "normal") -> dict[str, Any]:
    """Aggregate recorded call sizes; detail_level_effect shows what summary saves."""
    from apiforge.economy.ledger import report

    out: dict[str, Any] = _call("economy_report", lambda: report(Path(root)), detail_level)
    return out


def context_funnel(case_dir: str, detail_level: str = "normal") -> dict[str, Any]:
    """Measure the context funnel of a persisted case — bytes per stage."""
    from apiforge.application.funnel import measure_funnel

    out: dict[str, Any] = _call(
        "context_funnel", lambda: measure_funnel(Path(case_dir)), detail_level
    )
    return out


def graph_query(
    graph: str,
    kind: str | None = None,
    edge_kind: str | None = None,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Filter graph nodes/edges by closed vocabulary — no free text."""
    from apiforge.graph.query import query_graph

    out: dict[str, Any] = _call(
        "graph_query",
        lambda: query_graph(Path(graph), kind=kind, edge_kind=edge_kind),
        detail_level,
    )
    return out


def graph_impact(
    graph: str, node: str, max_depth: int = 4, detail_level: str = "normal"
) -> dict[str, Any]:
    """Reverse traversal: everything that transitively depends on the node."""
    from apiforge.graph.query import impact

    out: dict[str, Any] = _call(
        "graph_impact",
        lambda: impact(Path(graph), node, max_depth=max_depth),
        detail_level,
    )
    return out


def graph_trace(
    graph: str, from_id: str, to_id: str, detail_level: str = "normal"
) -> dict[str, Any]:
    """Shortest directed path between two nodes; absent path is named."""
    from apiforge.graph.query import trace

    out: dict[str, Any] = _call(
        "graph_trace", lambda: trace(Path(graph), from_id, to_id), detail_level
    )
    return out


def graph_coverage(graph: str, detail_level: str = "normal") -> dict[str, Any]:
    """Structural gaps: unverified findings, unimplemented ops, unreferenced facts."""
    from apiforge.graph.query import coverage

    out: dict[str, Any] = _call("graph_coverage", lambda: coverage(Path(graph)), detail_level)
    return out


def index_status(project: str, root: str = ".", detail_level: str = "normal") -> dict[str, Any]:
    """Name added/changed/removed source files against the built index."""
    from apiforge.index.build import index_status as status

    out: dict[str, Any] = _call(
        "index_status", lambda: status(Path(project), Path(root)), detail_level
    )
    return out


def task_status(task_id: str, root: str = ".", detail_level: str = "normal") -> dict[str, Any]:
    """Task spec + append-only history — read-only view of the lifecycle."""
    from apiforge.taskspec.runner import task_status as status

    out: dict[str, Any] = _call("task_status", lambda: status(Path(root), task_id), detail_level)
    return out


def task_compile(
    task_id: str,
    outcome: str,
    contract: str,
    project: str,
    case: str,
    root: str = ".",
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Compile a local API intention into a TaskSpec draft."""
    from apiforge.taskspec.compiler import compile_intent
    from apiforge.taskspec.service import create_task

    out: dict[str, Any] = _call(
        "task_compile",
        lambda: create_task(
            Path(root),
            compile_intent(
                task_id,
                outcome,
                contract=Path(contract),
                project=Path(project),
                case=Path(case),
            ),
        ),
        detail_level,
    )
    return out


def task_plan(task_id: str, root: str = ".", detail_level: str = "normal") -> dict[str, Any]:
    """Persist the closed plan for a sealed task."""
    from apiforge.taskspec.planner import plan_task

    out: dict[str, Any] = _call("task_plan", lambda: plan_task(Path(root), task_id), detail_level)
    return out


def task_verify(
    task_id: str,
    project: str,
    contract: str,
    manifest: str | None = None,
    root: str = ".",
    run_id: str = "manual",
    by: str = "af-verifier",
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Persist an independent VerificationRecord for a task."""
    from apiforge.taskspec.planner import plan_task
    from apiforge.verification.holdout import run_holdouts
    from apiforge.verification.service import verify_task

    def work() -> Any:
        task_root = Path(root)
        plan_path = task_root / ".apiforge" / "tasks" / task_id / "plan.json"
        if not plan_path.is_file():
            plan_task(task_root, task_id)
        holdout = (
            run_holdouts(task_root, Path(project), Path(contract), Path(manifest))
            if manifest is not None
            else ()
        )
        return verify_task(
            task_root,
            task_id,
            project=Path(project),
            contract=Path(contract),
            run_id=run_id,
            holdout=holdout,
            verified_by=by,
        )

    out: dict[str, Any] = _call("task_verify", work, detail_level)
    return out


def brief_show(task_id: str, root: str = ".", detail_level: str = "normal") -> dict[str, Any]:
    """Outcome Brief for a task — DONE is refused while gaps remain."""
    from apiforge.brief.render import brief_payload

    out: dict[str, Any] = _call(
        "brief_show", lambda: brief_payload(Path(root), task_id), detail_level
    )
    return out


def contract_list(detail_level: str = "normal") -> dict[str, Any]:
    """List registered canonical contracts."""
    from apiforge.contracts.registry import contract_names

    out: dict[str, Any] = _call(
        "contract_list", lambda: {"contracts": contract_names()}, detail_level
    )
    return out


def contract_show(name: str, detail_level: str = "normal") -> dict[str, Any]:
    """Emit the JSON schema of one registered contract."""
    from apiforge.contracts.registry import contract_schema

    out: dict[str, Any] = _call("contract_show", lambda: contract_schema(name), detail_level)
    return out


_DUMP_READERS: dict[str, str] = {
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


def model_dump(service: str, path: str, detail_level: str = "normal") -> dict[str, Any]:
    """Read a `collect <service>` dump into facts — closed service set."""
    from apiforge.application.analyze import AnalysisError

    def work() -> dict[str, Any]:
        import importlib

        dotted = _DUMP_READERS.get(service)
        if dotted is None:
            raise AnalysisError(
                "AF-INPUT-INVALID",
                f"service {service!r} not in {sorted(_DUMP_READERS)}",
            )
        dump = Path(path)
        if not dump.is_dir():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(dump))
        module, _, func = dotted.rpartition(".")
        inventory = getattr(importlib.import_module(module), func)(dump)
        return {
            "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
            "facts": [f.model_dump(mode="json") for f in inventory.facts],
            "framework": inventory.framework,
            "input_hashes": dict(inventory.input_hashes),
        }

    out: dict[str, Any] = _call("model_dump", work, detail_level)
    return out


def model_redis(path: str, detail_level: str = "normal") -> dict[str, Any]:
    """Static Redis/Valkey call-site scan -> data.redis.* facts + IR."""
    from apiforge.adapters.redis_.extract import extract_redis
    from apiforge.adapters.redis_.ir import build_data_access_ir

    def work() -> dict[str, Any]:
        inventory = extract_redis(Path(path))
        return {
            "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
            "facts": [f.model_dump(mode="json") for f in inventory.facts],
            "framework": inventory.framework,
            "input_hashes": dict(inventory.input_hashes),
            "data_access_ir": build_data_access_ir(inventory).model_dump(mode="json"),
        }

    out: dict[str, Any] = _call("model_redis", work, detail_level)
    return out


def model_otel(path: str, detail_level: str = "normal") -> dict[str, Any]:
    """OTLP/JSON trace export -> perf.otel.* facts + a PerformanceRun."""
    from apiforge.adapters.otel.extract import extract_otel
    from apiforge.adapters.otel.run import build_performance_run
    from apiforge.application.analyze import AnalysisError

    def work() -> dict[str, Any]:
        source = Path(path)
        if not source.is_file():
            raise AnalysisError("AF-INPUT-NOT-FOUND", str(source))
        inventory = extract_otel(source)
        return {
            "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
            "facts": [f.model_dump(mode="json") for f in inventory.facts],
            "framework": inventory.framework,
            "input_hashes": dict(inventory.input_hashes),
            "performance_run": build_performance_run(inventory, source.name).model_dump(
                mode="json"
            ),
        }

    out: dict[str, Any] = _call("model_otel", work, detail_level)
    return out


def _load_run_path(raw: str) -> Any:
    """PerformanceRun from a JSON file — bare or `performance_run`-wrapped."""
    from apiforge.application.analyze import AnalysisError
    from apiforge.contracts.stubs import PerformanceRun

    try:
        payload = json.loads(Path(raw).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise AnalysisError("AF-PERF-RUN-INVALID", f"{raw}: {exc}") from exc
    if isinstance(payload, dict) and isinstance(payload.get("performance_run"), dict):
        payload = payload["performance_run"]
    try:
        return PerformanceRun.model_validate(payload)
    except Exception as exc:
        raise AnalysisError("AF-PERF-RUN-INVALID", f"{raw}: {exc}") from exc


def _repeat_runs(directory: str | None) -> tuple[Any, ...]:
    if not directory:
        return ()
    path = Path(directory)
    if not path.is_dir():
        from apiforge.application.analyze import AnalysisError

        raise AnalysisError("AF-PERF-RUN-INVALID", f"{directory}: not a directory")
    return tuple(_load_run_path(str(p)) for p in sorted(path.glob("*.json")))


def perf_compare(
    baseline: str,
    candidate: str,
    threshold_pct: float = 10.0,
    min_samples: int = 3,
    repeat_baseline: str | None = None,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """compare_runs over two PerformanceRun payloads (bare or wrapped).

    ``repeat_baseline`` is a directory of repeated baseline run JSONs; it
    measures the noise floor and suppresses deltas inside it.
    """
    from apiforge.perf.compare import compare_runs

    def work() -> dict[str, Any]:
        return compare_runs(
            _load_run_path(baseline),
            _load_run_path(candidate),
            threshold_pct=threshold_pct,
            min_samples=min_samples,
            repeat_baselines=_repeat_runs(repeat_baseline),
        ).model_dump(mode="json")

    out: dict[str, Any] = _call("perf_compare", work, detail_level)
    return out


def perf_verdict(
    run: str,
    repeat_baseline: str | None = None,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """passed / failed / inconclusive over a PerformanceRun payload."""
    from apiforge.perf.verdict import verdict

    def work() -> dict[str, Any]:
        return verdict(
            _load_run_path(run),
            repeat_baselines=_repeat_runs(repeat_baseline),
        ).model_dump(mode="json")

    out: dict[str, Any] = _call("perf_verdict", work, detail_level)
    return out


def perf_memory_search(
    root: str = ".",
    subject: str | None = None,
    tool: str | None = None,
    since: str | None = None,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """search_performance_memory — filters declared fields, never infers."""
    from apiforge.perf.run_store import search_runs

    def work() -> dict[str, Any]:
        runs = search_runs(Path(root), subject=subject, tool=tool, since=since)
        return {"count": len(runs), "runs": runs}

    out: dict[str, Any] = _call("perf_memory_search", work, detail_level)
    return out


def perf_suggest(
    findings: str,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """suggest_fix — emits an ActionPlan; never applies it."""
    from apiforge.application.analyze import AnalysisError
    from apiforge.core.models import Finding
    from apiforge.perf.suggest import suggest_fix

    def work() -> dict[str, Any]:
        try:
            doc = json.loads(Path(findings).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AnalysisError("AF-PERF-SUGGEST-INPUT", f"{findings}: {exc}") from exc
        payload = doc if isinstance(doc, list) else doc.get("findings", [])
        try:
            parsed = [Finding.model_validate(f) for f in payload]
        except Exception as exc:
            raise AnalysisError("AF-PERF-SUGGEST-INPUT", f"{findings}: {exc}") from exc
        return suggest_fix(parsed).model_dump(mode="json")

    out: dict[str, Any] = _call("perf_suggest", work, detail_level)
    return out


def autonomy_status(root: str = ".", detail_level: str = "normal") -> dict[str, Any]:
    """Current autonomy mode + append-only ledger — read-only."""
    from apiforge.autonomy.modes import load_mode
    from apiforge.autonomy.service import read_ledger

    def work() -> dict[str, Any]:
        state = load_mode(Path(root))
        return {
            "mode": state.mode.value,
            "set_by": state.set_by,
            "set_at": state.set_at,
            "reason": state.reason,
            "ledger": read_ledger(Path(root)),
        }

    out: dict[str, Any] = _call("autonomy_status", work, detail_level)
    return out


def knowledge_list(root: str = "knowledge", detail_level: str = "normal") -> dict[str, Any]:
    """List every pack with areas, rules and verification date."""
    from apiforge.knowledge.loader import load_packs

    def work() -> dict[str, Any]:
        packs = load_packs(Path(root))
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

    out: dict[str, Any] = _call("knowledge_list", work, detail_level)
    return out


def knowledge_show(
    domain: str, root: str = "knowledge", detail_level: str = "normal"
) -> dict[str, Any]:
    """One pack: summary, source authority, matrix, declared evals."""
    from apiforge.knowledge.loader import load_pack

    def work() -> dict[str, Any]:
        pack = load_pack(Path(root) / domain)
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

    out: dict[str, Any] = _call("knowledge_show", work, detail_level)
    return out


def knowledge_check(root: str = "knowledge", detail_level: str = "normal") -> dict[str, Any]:
    """Validate every pack — problems are named, never raised away."""
    from apiforge.application.analyze import AnalysisError
    from apiforge.knowledge.loader import check_packs

    def work() -> dict[str, Any]:
        result = check_packs(Path(root))
        if not result["ok"]:
            raise AnalysisError(
                "AF-KNOW-CHECK",
                "pack problems: " + "; ".join(str(p) for p in result["problems"]),
            )
        return result

    out: dict[str, Any] = _call("knowledge_check", work, detail_level)
    return out


def plan_architecture(profile: str, detail_level: str = "normal") -> dict[str, Any]:
    """Architecture Decision Engine over a WorkloadProfile payload."""
    from apiforge.application.analyze import AnalysisError
    from apiforge.contracts.stubs import WorkloadProfile
    from apiforge.plan.architecture import recommend

    def work() -> dict[str, Any]:
        try:
            payload = json.loads(Path(profile).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AnalysisError("AF-PLAN-PROFILE-INVALID", f"{profile}: {exc}") from exc
        if isinstance(payload, dict) and isinstance(payload.get("workload_profile"), dict):
            payload = payload["workload_profile"]
        try:
            wp = WorkloadProfile.model_validate(payload)
        except Exception as exc:
            raise AnalysisError("AF-PLAN-PROFILE-INVALID", f"{profile}: {exc}") from exc
        return dict(recommend(wp))

    out: dict[str, Any] = _call("plan_architecture", work, detail_level)
    return out


def run_list(detail_level: str = "normal") -> dict[str, Any]:
    """Tool registry — declared metadata plus measured install status."""
    from apiforge.run_tools import list_tools

    def work() -> dict[str, Any]:
        return {"tools": list_tools()}

    out: dict[str, Any] = _call("run_list", work, detail_level)
    return out


def perf_scenario(tool: str, scenario: str, detail_level: str = "normal") -> dict[str, Any]:
    """Generate a k6/JMeter/Locust script for a declared scenario file."""
    from apiforge.application.analyze import AnalysisError
    from apiforge.perf.scenario import generate_scenario
    from apiforge.run_tools import RunError

    def work() -> dict[str, Any]:
        try:
            spec = json.loads(Path(scenario).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AnalysisError("AF-SCENARIO-SCHEMA", f"{scenario}: {exc}") from exc
        try:
            return dict(generate_scenario(tool, spec))
        except RunError as exc:
            raise AnalysisError(exc.code, str(exc).split(": ", 1)[-1]) from exc

    out: dict[str, Any] = _call("perf_scenario", work, detail_level)
    return out


def perf_chaos(detail_level: str = "normal") -> dict[str, Any]:
    """List the declared controlled failure-injection scenarios (CHAOS-001..013)."""
    from apiforge.perf.chaos import list_scenarios

    def work() -> dict[str, Any]:
        return {"scenarios": list_scenarios()}

    out: dict[str, Any] = _call("perf_chaos", work, detail_level)
    return out


def model_resilience(path: str, detail_level: str = "normal") -> dict[str, Any]:
    """Static resilience scan of a project tree — heuristic, blind spots named."""
    from apiforge.adapters.resilience import extract_resilience
    from apiforge.application.analyze import AnalysisError

    def work() -> dict[str, Any]:
        root = Path(path)
        if not root.is_dir():
            raise AnalysisError("AF-INPUT-NOT-FOUND", path)
        inventory = extract_resilience(root)
        return {
            "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
            "facts": [f.model_dump(mode="json") for f in inventory.facts],
            "framework": inventory.framework,
            "input_hashes": dict(inventory.input_hashes),
        }

    out: dict[str, Any] = _call("model_resilience", work, detail_level)
    return out


def runtime_run(
    task_id: str,
    root: str = ".",
    policy: str = "local-ci-safe",
    now: str | None = None,
    debate: bool = False,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Execute a bounded local runtime run for a TaskSpec."""
    from apiforge.runtime.runner import run_runtime

    def work() -> dict[str, Any]:
        return run_runtime(Path(root), task_id, policy_id=policy, now=now, requested_debate=debate)

    return cast(dict[str, Any], _call("runtime_run", work, detail_level))


def runtime_status(task_id: str, root: str = ".", detail_level: str = "normal") -> dict[str, Any]:
    """Read the newest persisted runtime run."""
    from apiforge.runtime.runner import runtime_status as read_status

    return cast(
        dict[str, Any],
        _call("runtime_status", lambda: read_status(Path(root), task_id), detail_level),
    )


def runtime_resume(
    task_id: str, root: str = ".", policy: str = "local-ci-safe", detail_level: str = "normal"
) -> dict[str, Any]:
    """Resume a bounded runtime execution."""
    from apiforge.runtime.runner import resume_runtime

    return cast(
        dict[str, Any],
        _call(
            "runtime_resume",
            lambda: resume_runtime(Path(root), task_id, policy_id=policy),
            detail_level,
        ),
    )


def runtime_debate(
    task_id: str, root: str = ".", policy: str = "local-ci-safe", detail_level: str = "normal"
) -> dict[str, Any]:
    """Request a debate room for a bounded runtime execution."""
    from apiforge.runtime.runner import debate_runtime

    return cast(
        dict[str, Any],
        _call(
            "runtime_debate",
            lambda: debate_runtime(Path(root), task_id, policy_id=policy),
            detail_level,
        ),
    )


def runtime_approve(
    task_id: str,
    run_id: str,
    approver: str,
    root: str = ".",
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Persist a human approval artifact for a runtime run."""
    from apiforge.runtime.runner import approve_runtime

    return cast(
        dict[str, Any],
        _call(
            "runtime_approve",
            lambda: approve_runtime(Path(root), task_id, run_id, approver),
            detail_level,
        ),
    )


def observability_ingest(
    source: str,
    service: str | None = None,
    slo: str | None = None,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Normalize an offline telemetry fixture and evaluate optional SLO."""
    from apiforge.observability.supervisor import run_fixture

    definition = json.loads(Path(slo).read_text(encoding="utf-8")) if slo else None
    return cast(
        dict[str, Any],
        _call(
            "observability_ingest",
            lambda: run_fixture(Path.cwd(), Path(source), service, definition),
            detail_level,
        ),
    )


def observability_capabilities(detail_level: str = "normal") -> dict[str, Any]:
    """Return vendor capabilities without resolving credentials."""
    from apiforge.observability.registry import capabilities

    return cast(dict[str, Any], _call("observability_capabilities", capabilities, detail_level))


def grpc_analyze(source: str, detail_level: str = "normal") -> dict[str, Any]:
    """Analyze a protobuf source into the canonical gRPC IR."""
    from apiforge.grpc.source import load_source

    return cast(
        dict[str, Any], _call("grpc_analyze", lambda: load_source(Path(source)), detail_level)
    )


def grpc_diff(baseline: str, candidate: str, detail_level: str = "normal") -> dict[str, Any]:
    """Compare two protobuf contracts with deterministic compatibility rules."""
    from apiforge.grpc.compatibility import compare
    from apiforge.grpc.source import load_source

    return cast(
        dict[str, Any],
        _call(
            "grpc_diff",
            lambda: compare(load_source(Path(baseline)), load_source(Path(candidate))),
            detail_level,
        ),
    )


def grpc_capabilities(detail_level: str = "normal") -> dict[str, Any]:
    from apiforge.grpc.capabilities import discover

    return cast(
        dict[str, Any],
        _call("grpc_capabilities", lambda: {"capabilities": discover()}, detail_level),
    )


def grpc_codegen(
    source: str,
    languages: tuple[str, ...] = ("python",),
    output_dir: str = "generated",
    tool: str = "fake",
    detail_level: str = "normal",
) -> dict[str, Any]:
    from apiforge.contracts.grpc import GrpcCodegenRequest
    from apiforge.grpc.codegen import plan_codegen
    from apiforge.grpc.source import load_source

    target_languages = cast(tuple[Literal["python", "go", "java"], ...], languages)
    target_tool = cast(Literal["fake", "protoc", "buf"], tool)
    work = lambda: plan_codegen(
        load_source(Path(source)),
        GrpcCodegenRequest(languages=target_languages, output_dir=output_dir, tool=target_tool),
    )
    return cast(dict[str, Any], _call("grpc_codegen", work, detail_level))


def grpc_gateway(
    source: str,
    gateways: tuple[str, ...] = ("openapi",),
    output_dir: str = "gateway",
    detail_level: str = "normal",
) -> dict[str, Any]:
    from apiforge.contracts.grpc import GrpcGatewayRequest
    from apiforge.grpc.gateway import plan_gateway
    from apiforge.grpc.source import load_source

    target_gateways = cast(
        tuple[Literal["envoy", "grpc_gateway", "grpc_web", "openapi"], ...], gateways
    )
    work = lambda: plan_gateway(
        load_source(Path(source)),
        GrpcGatewayRequest(gateways=target_gateways, output_dir=output_dir),
    )
    return cast(dict[str, Any], _call("grpc_gateway", work, detail_level))


def grpc_verify(
    source: str, baseline: str | None = None, detail_level: str = "normal"
) -> dict[str, Any]:
    from apiforge.grpc.compatibility import compare
    from apiforge.grpc.source import load_source
    from apiforge.grpc.verify import verify

    def work() -> object:
        candidate = load_source(Path(source))
        compatibility = compare(load_source(Path(baseline)), candidate) if baseline else None
        return verify(candidate, compatibility)

    return cast(dict[str, Any], _call("grpc_verify", work, detail_level))


def grpc_benchmark(run: dict[str, object], detail_level: str = "normal") -> dict[str, Any]:
    from apiforge.contracts.grpc import GrpcPerformanceRun
    from apiforge.grpc.performance import evaluate

    return cast(
        dict[str, Any],
        _call(
            "grpc_benchmark", lambda: evaluate(GrpcPerformanceRun.model_validate(run)), detail_level
        ),
    )


def migration_analyze(
    project: str,
    ecosystem: str,
    source: str,
    target: str,
    matrix: str | None = None,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Discover runtime migration impact without changing the project."""
    from apiforge.migration.contracts import Ecosystem, MigrationSpec
    from apiforge.migration.discovery import discover as run_discovery

    spec = MigrationSpec(
        project_root=str(Path(project).resolve()),
        ecosystem=cast(Ecosystem, ecosystem),
        source_version=source,
        target_version=target,
    )
    return cast(
        dict[str, Any],
        _call(
            "migration_analyze",
            lambda: run_discovery(spec, Path(matrix) if matrix else None),
            detail_level,
        ),
    )


def migration_plan(
    project: str,
    ecosystem: str,
    source: str,
    target: str,
    matrix: str | None = None,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Build a closed migration TaskSpec and dependency DAG."""
    from apiforge.migration.contracts import Ecosystem, MigrationSpec
    from apiforge.migration.discovery import discover as run_discovery
    from apiforge.migration.planner import compile_plan

    spec = MigrationSpec(
        project_root=str(Path(project).resolve()),
        ecosystem=cast(Ecosystem, ecosystem),
        source_version=source,
        target_version=target,
    )
    return cast(
        dict[str, Any],
        _call(
            "migration_plan",
            lambda: compile_plan(spec, run_discovery(spec, Path(matrix) if matrix else None)),
            detail_level,
        ),
    )


def migration_verify(
    report: str,
    evidence_ok: bool = False,
    verification_ok: bool = False,
    contract_breaking: bool = False,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """Apply conservative status gates to a migration report JSON file."""
    from apiforge.migration.contracts import MigrationReport
    from apiforge.migration.verifier import verify_report

    payload = json.loads(Path(report).read_text(encoding="utf-8"))
    return cast(
        dict[str, Any],
        _call(
            "migration_verify",
            lambda: verify_report(
                MigrationReport.model_validate(payload),
                evidence_ok=evidence_ok,
                verification_ok=verification_ok,
                contract_breaking=contract_breaking,
            ),
            detail_level,
        ),
    )


TOOLS: tuple[Callable[..., Any], ...] = (
    discover,
    analyze,
    judge,
    model_build,
    model_api_gateway,
    diff_contract,
    next_step,
    portable_inspect,
    portable_init,
    portable_status,
    portable_doctor,
    workspace_discover,
    workspace_status,
    workspace_add,
    context_resolve,
    change_control_run,
    change_control_collect,
    change_control_publish,
    change_control_surface,
    integration_github_issues,
    integration_health,
    integration_json,
    platform_verify_runtime,
    capabilities_list,
    capabilities_verify,
    rules_list,
    rules_lookup,
    playbook,
    economy_report,
    context_funnel,
    graph_query,
    graph_impact,
    graph_trace,
    graph_coverage,
    index_status,
    task_status,
    task_compile,
    task_plan,
    task_verify,
    brief_show,
    contract_list,
    contract_show,
    model_dump,
    model_redis,
    model_otel,
    perf_compare,
    perf_verdict,
    perf_memory_search,
    perf_suggest,
    autonomy_status,
    knowledge_list,
    knowledge_show,
    knowledge_check,
    plan_architecture,
    run_list,
    perf_scenario,
    perf_chaos,
    model_resilience,
    runtime_run,
    runtime_status,
    runtime_resume,
    runtime_debate,
    runtime_approve,
)

OBSERVABILITY_TOOLS: tuple[Callable[..., Any], ...] = (
    observability_ingest,
    observability_capabilities,
)

GRPC_TOOLS: tuple[Callable[..., Any], ...] = (
    grpc_analyze,
    grpc_diff,
    grpc_capabilities,
    grpc_codegen,
    grpc_gateway,
    grpc_verify,
    grpc_benchmark,
)

MIGRATION_TOOLS: tuple[Callable[..., Any], ...] = (
    migration_analyze,
    migration_plan,
    migration_verify,
)
