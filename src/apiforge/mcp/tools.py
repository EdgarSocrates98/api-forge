"""MCP tool bodies: call application services, project, record economy bytes.

Each function mirrors a CLI verb's payload exactly — same dicts, same
projection — so CLI and MCP answers cannot diverge. ``verb`` records as
``mcp:<name>`` in the economy ledger under ``Path.cwd()``.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from apiforge.core.detail import apply_detail_level
from apiforge.core.models import Finding

T = TypeVar("T")


def _call(verb: str, fn: Callable[[], Any], detail_level: str) -> Any:
    value = fn()
    if isinstance(value, list):
        value = [
            v.model_dump(mode="json") if hasattr(v, "model_dump") else v for v in value
        ]
    elif hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
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
    from apiforge.adapters.fastapi.extractor import extract_fastapi

    def work() -> dict[str, Any]:
        inventory = extract_fastapi(Path(project))
        return {
            "routes": [f.model_dump(mode="json") for f in inventory.facts],
            "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
            "input_hashes": dict(inventory.input_hashes),
        }

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
    from apiforge.application.analyze import analyze_project

    def work() -> dict[str, Any]:
        result = analyze_project(
            Path(contract),
            Path(project),
            Path(baseline) if baseline else None,
            Path(out_dir),
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


def diff_contract(
    baseline: str, candidate: str, detail_level: str = "normal"
) -> list[Any]:
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
    from apiforge.application.next_step import next_step as route

    def work() -> Any:
        data = json.loads(Path(findings).read_text(encoding="utf-8"))
        parsed = tuple(Finding.model_validate(f) for f in data)
        return route(parsed, phase)

    out: dict[str, Any] = _call("next_step", work, detail_level)
    return out


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

    out: dict[str, Any] = _call("context_funnel", lambda: measure_funnel(Path(case_dir)), detail_level)
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

    out: dict[str, Any] = _call(
        "graph_coverage", lambda: coverage(Path(graph)), detail_level
    )
    return out


def index_status(
    project: str, root: str = ".", detail_level: str = "normal"
) -> dict[str, Any]:
    """Name added/changed/removed source files against the built index."""
    from apiforge.index.build import index_status as status

    out: dict[str, Any] = _call(
        "index_status", lambda: status(Path(project), Path(root)), detail_level
    )
    return out


def task_status(
    task_id: str, root: str = ".", detail_level: str = "normal"
) -> dict[str, Any]:
    """Task spec + append-only history — read-only view of the lifecycle."""
    from apiforge.taskspec.runner import task_status as status

    out: dict[str, Any] = _call(
        "task_status", lambda: status(Path(root), task_id), detail_level
    )
    return out


def brief_show(
    task_id: str, root: str = ".", detail_level: str = "normal"
) -> dict[str, Any]:
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

    out: dict[str, Any] = _call(
        "contract_show", lambda: contract_schema(name), detail_level
    )
    return out


TOOLS: tuple[Callable[..., Any], ...] = (
    discover,
    analyze,
    judge,
    model_build,
    model_api_gateway,
    diff_contract,
    next_step,
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
    brief_show,
    contract_list,
    contract_show,
)
