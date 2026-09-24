"""Vertical slice: discovery -> API-IR -> finding -> task -> sandbox ->
evidence -> brief. Every hop produces an artifact the next one consumes."""

from __future__ import annotations

import json
from pathlib import Path

from apiforge.adapters.fastapi.extractor import extract_fastapi
from apiforge.api_ir.builder import build_api_model
from apiforge.application.analyze import analyze_project
from apiforge.brief.render import brief_for_task
from apiforge.contracts.task import BriefStatus, TaskSpec
from apiforge.evidence.build import emit_receipt
from apiforge.openapi.loader import load_openapi
from apiforge.report.keys import generate_keypair
from apiforge.rules.judge import judge_api_model
from apiforge.runtime.control import ControlPlane
from apiforge.sandbox.service import sandbox_apply
from apiforge.taskspec.runner import accept_task, run_task
from apiforge.taskspec.service import create_task, review_task, seal_task

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures"
CONTRACT = FIXTURES / "openapi" / "orders-v1.yaml"
PROJECT = FIXTURES / "fastapi_orders"

NEW_ROUTE_DIFF = """\
--- /dev/null
+++ b/app/routes/orders_get.py
@@ -0,0 +1,8 @@
+from fastapi import APIRouter
+
+router = APIRouter()
+
+
+@router.get("/orders")
+def list_orders():
+    return []
"""


def _judge_side(document):
    def analyze(root: Path):
        model = build_api_model(document, extract_fastapi(root))
        return [f.model_dump(mode="json") for f in judge_api_model(model)]

    return analyze


def test_discovery_to_brief_slice(tmp_path: Path) -> None:
    # discovery -> API-IR -> findings persisted as a verified case
    case_dir = tmp_path / "case"
    result = analyze_project(CONTRACT, PROJECT, None, case_dir)
    assert result.model.operations
    assert result.findings

    # task: sealed, budgeted, executed through the recipe
    root = tmp_path / "root"
    spec = TaskSpec.model_validate(
        {
            "id": "slice-1",
            "outcome": "verify orders API surface",
            "strategy": "test-first",
            "inputs": [
                f"project={PROJECT}",
                f"contract={CONTRACT}",
                f"case={case_dir}",
            ],
        }
    )
    create_task(root, spec)
    review_task(root, "slice-1", "alice")
    key = generate_keypair(tmp_path / "keys", "sealer")["private"]
    seal_task(root, "slice-1", key, "alice")
    record = run_task(root, "slice-1", "af-extractor", now="2026-09-21T00:00:00Z")
    assert record["terminal"] == "awaiting_supervision"
    assert all(s["status"] == "ran" for s in record["steps"])

    # sandbox: a diff adding the missing GET /orders handler; main tree
    # is never touched and the before/after delta is measured
    document = load_openapi(CONTRACT)
    sandbox = sandbox_apply(PROJECT, NEW_ROUTE_DIFF, _judge_side(document))
    assert sandbox["applied"] is True
    assert sandbox["main_tree_touched"] is False
    assert "app/routes/orders_get.py" in sandbox["files_changed"]

    # evidence: receipt binds the case artifacts by sha256
    receipt = emit_receipt(case_dir, now="2026-09-21T00:00:00Z")
    assert receipt.artifacts

    # acceptance by an actor distinct from the executor -> brief DONE
    accept_task(
        root,
        "slice-1",
        "bob",
        evidence=(f"sandbox:{sandbox['id']}", f"receipt:{receipt.policy_sha256[:16]}"),
    )
    brief = brief_for_task(root, "slice-1")
    assert brief.status is BriefStatus.DONE
    assert brief.proof
    assert brief.human_action is None


def test_brief_refuses_done_without_acceptance(tmp_path: Path) -> None:
    case_dir = tmp_path / "case"
    analyze_project(CONTRACT, PROJECT, None, case_dir)
    root = tmp_path / "root"
    create_task(
        root,
        TaskSpec.model_validate(
            {
                "id": "slice-2",
                "outcome": "x",
                "strategy": "test-first",
                "inputs": [
                    f"project={PROJECT}",
                    f"contract={CONTRACT}",
                    f"case={case_dir}",
                ],
            }
        ),
    )
    review_task(root, "slice-2", "alice")
    key = generate_keypair(tmp_path / "keys", "s")["private"]
    seal_task(root, "slice-2", key, "alice")
    run_task(root, "slice-2", "af-extractor", now="2026-09-21T00:00:00Z")
    brief = brief_for_task(root, "slice-2")
    assert brief.status is not BriefStatus.DONE
    assert "accept" in (brief.human_action or "")


def test_slice_receipt_serializes(tmp_path: Path) -> None:
    case_dir = tmp_path / "case"
    analyze_project(CONTRACT, PROJECT, None, case_dir)
    receipt = emit_receipt(case_dir)
    payload = json.dumps(receipt.model_dump(mode="json"), sort_keys=True)
    assert json.loads(payload)["schema_version"] == "af-receipt/1"


def test_agentic_kernel_replay_is_persisted_end_to_end(tmp_path: Path) -> None:
    plane = ControlPlane(tmp_path)
    run = plane.create(
        "kernel-e2e",
        (("inventory", ()), ("verify", ("inventory",))),
        run_id="run:kernel-e2e",
    )
    inventory = run.steps[0]
    plane.start(run.run_id, inventory.step_id)
    plane.complete(run.run_id, inventory.step_id, {"facts": ["f1"]})
    verify = plane.ready(run.run_id)[0]
    plane.start(run.run_id, verify.step_id)
    plane.complete(run.run_id, verify.step_id, {"verified": True})
    replay = plane.replay(run.run_id)
    assert replay["run"]["status"] == "awaiting_review"
    assert [event["event"] for event in replay["events"]].count("step_succeeded") == 2
