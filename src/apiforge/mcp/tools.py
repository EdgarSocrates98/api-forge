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
}


def model_dump(
    service: str, path: str, detail_level: str = "normal"
) -> dict[str, Any]:
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
            "diagnostics": [
                d.model_dump(mode="json") for d in inventory.diagnostics
            ],
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
            "diagnostics": [
                d.model_dump(mode="json") for d in inventory.diagnostics
            ],
            "facts": [f.model_dump(mode="json") for f in inventory.facts],
            "framework": inventory.framework,
            "input_hashes": dict(inventory.input_hashes),
            "data_access_ir": build_data_access_ir(inventory).model_dump(
                mode="json"
            ),
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
            "diagnostics": [
                d.model_dump(mode="json") for d in inventory.diagnostics
            ],
            "facts": [f.model_dump(mode="json") for f in inventory.facts],
            "framework": inventory.framework,
            "input_hashes": dict(inventory.input_hashes),
            "performance_run": build_performance_run(
                inventory, source.name
            ).model_dump(mode="json"),
        }

    out: dict[str, Any] = _call("model_otel", work, detail_level)
    return out


def perf_compare(
    baseline: str,
    candidate: str,
    threshold_pct: float = 10.0,
    min_samples: int = 3,
    detail_level: str = "normal",
) -> dict[str, Any]:
    """compare_runs over two PerformanceRun payloads (bare or wrapped)."""
    from apiforge.application.analyze import AnalysisError
    from apiforge.contracts.stubs import PerformanceRun
    from apiforge.perf.compare import compare_runs

    def load_run(raw: str) -> PerformanceRun:
        try:
            payload = json.loads(Path(raw).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AnalysisError("AF-PERF-RUN-INVALID", f"{raw}: {exc}") from exc
        if isinstance(payload, dict) and isinstance(
            payload.get("performance_run"), dict
        ):
            payload = payload["performance_run"]
        try:
            return PerformanceRun.model_validate(payload)
        except Exception as exc:
            raise AnalysisError("AF-PERF-RUN-INVALID", f"{raw}: {exc}") from exc

    def work() -> dict[str, Any]:
        return compare_runs(
            load_run(baseline),
            load_run(candidate),
            threshold_pct=threshold_pct,
            min_samples=min_samples,
        ).model_dump(mode="json")

    out: dict[str, Any] = _call("perf_compare", work, detail_level)
    return out


def perf_verdict(run: str, detail_level: str = "normal") -> dict[str, Any]:
    """passed / failed / inconclusive over a PerformanceRun payload."""
    from apiforge.application.analyze import AnalysisError
    from apiforge.contracts.stubs import PerformanceRun
    from apiforge.perf.verdict import verdict

    def work() -> dict[str, Any]:
        try:
            payload = json.loads(Path(run).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AnalysisError("AF-PERF-RUN-INVALID", f"{run}: {exc}") from exc
        if isinstance(payload, dict) and isinstance(
            payload.get("performance_run"), dict
        ):
            payload = payload["performance_run"]
        try:
            run_obj = PerformanceRun.model_validate(payload)
        except Exception as exc:
            raise AnalysisError("AF-PERF-RUN-INVALID", f"{run}: {exc}") from exc
        return verdict(run_obj).model_dump(mode="json")

    out: dict[str, Any] = _call("perf_verdict", work, detail_level)
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


def knowledge_list(
    root: str = "knowledge", detail_level: str = "normal"
) -> dict[str, Any]:
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


def knowledge_check(
    root: str = "knowledge", detail_level: str = "normal"
) -> dict[str, Any]:
    """Validate every pack — problems are named, never raised away."""
    from apiforge.application.analyze import AnalysisError
    from apiforge.knowledge.loader import check_packs

    def work() -> dict[str, Any]:
        result = check_packs(Path(root))
        if not result["ok"]:
            raise AnalysisError(
                "AF-KNOW-CHECK",
                "pack problems: "
                + "; ".join(str(p) for p in result["problems"]),
            )
        return result

    out: dict[str, Any] = _call("knowledge_check", work, detail_level)
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
    model_dump,
    model_redis,
    model_otel,
    perf_compare,
    perf_verdict,
    autonomy_status,
    knowledge_list,
    knowledge_show,
    knowledge_check,
)
