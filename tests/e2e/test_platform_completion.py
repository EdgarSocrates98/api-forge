from __future__ import annotations

import json
from pathlib import Path

from apiforge.application.analyze import analyze_project
from apiforge.application.artifacts import load_findings
from apiforge.application.next_step import next_step
from apiforge.brief.render import brief_payload
from apiforge.capabilities.registry import load_capabilities
from apiforge.contracts.platform import CapabilityRequest
from apiforge.contracts.task import TaskSpec
from apiforge.evidence.build import emit_receipt
from apiforge.graph.build import build_graph
from apiforge.surfaces.ide import handle as ide_handle
from apiforge.surfaces.projection import project_capability
from apiforge.surfaces.ui import handle as ui_handle
from apiforge.taskspec.service import create_task

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
CONTRACT = FIXTURES / "openapi" / "orders-v1.yaml"
PROJECT = FIXTURES / "fastapi_orders"


def test_platform_chain(tmp_path: Path) -> None:
    case_dir = tmp_path / "case"
    result = analyze_project(CONTRACT, PROJECT, None, case_dir)
    assert result.manifest.artifacts

    step = next_step(load_findings(case_dir / "findings.json"), "contract")
    assert step.recommended_agent == "api-contract-architect"

    graph_dir = tmp_path / "graph"
    graph = build_graph(case_dir, graph_dir)
    assert graph.node_count > 0
    assert (graph_dir / "nodes.jsonl").is_file()

    receipt = emit_receipt(case_dir, now="2026-09-22T00:00:00Z")
    assert receipt.artifacts

    task_root = tmp_path / "tasks"
    create_task(task_root, TaskSpec(id="platform-chain", outcome="review platform chain"))
    brief = brief_payload(task_root, "platform-chain")
    assert brief["status"] == "DECIDE"
    assert json.loads((case_dir / "findings.json").read_text(encoding="utf-8"))["findings"]


def test_surface_projections_preserve_the_canonical_result() -> None:
    request = CapabilityRequest(
        capability_id="api.analyze",
        intent="inspect an API",
        surface="cli",
    )
    records = load_capabilities()
    canonical = project_capability(request, records).model_dump(mode="json")
    ide = ide_handle(request.model_dump(mode="json"))
    ui = ui_handle({**request.model_dump(mode="json"), "surface": "ui"})
    assert ide == canonical
    assert ui == {**canonical, "version": 1}
