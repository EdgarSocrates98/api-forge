"""§46–§48 deterministic evals: the Forge Protocol lifecycle end to end.

Cases declare submits (with optional governed attachments), handoffs and
health expectations; each runs on an isolated root so nothing is inferred
from shared state.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.forge_protocol import ForgeTaskRequest
from apiforge.contracts.task import TaskSpec, TaskState
from apiforge.forge.protocol import (
    attach_task,
    discover_capabilities,
    health,
    inspect_task,
    prepare_handoff,
    retrieve_evidence,
    retrieve_result,
    submit_task,
)
from apiforge.taskspec import store as taskstore
from apiforge.taskspec.service import create_task as governed_create


def load_cases(corpus: Path) -> list[dict[str, Any]]:
    cases = [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [case.get("id") for case in cases]
    if not cases or len(ids) != len(set(ids)):
        raise ContractError(
            "AF-EVALS-INVALID", f"forge-protocol corpus {corpus} empty or duplicated"
        )
    return cases


def _governed(root: Path, task_id: str, state: str | None) -> None:
    governed_create(root, TaskSpec(id=task_id, outcome="eval governed outcome"))
    if state is not None:
        spec = taskstore.load(root, task_id).model_copy(update={"state": TaskState(state)})
        taskstore.write_spec(taskstore.task_dir(root, task_id), spec)
        if state == "accepted":
            taskstore.record_event(
                root, task_id, {"event": "->accepted", "by": "eval", "evidence": ["e1"]}
            )


def _check_submit(root: Path, case: dict[str, Any], failures: list[str]) -> None:
    expect = case.get("submit") or {}
    if not expect:
        return
    request = ForgeTaskRequest(
        task_id=expect["task_id"],
        capability_id=expect["capability_id"],
        intent=expect.get("intent", "eval"),
        risk=expect.get("risk", "read_only"),
    )
    try:
        status = submit_task(root, request, acknowledge_risk=bool(expect.get("acknowledge_risk")))
    except ContractError as exc:
        refused = expect.get("refuse")
        if refused and refused in str(exc):
            return
        failures.append(f"submit refused unexpectedly: {exc}")
        return
    if expect.get("refuse"):
        failures.append(f"submit expected refusal {expect['refuse']}")
    elif status.state != expect.get("state", "accepted"):
        failures.append(f"state {status.state} != {expect.get('state', 'accepted')}")


def _check_inspect(root: Path, case: dict[str, Any], failures: list[str]) -> None:
    expect = case.get("inspect") or {}
    if not expect:
        return
    status = inspect_task(root, expect["task_id"])
    if "state" in expect and status.state != expect["state"]:
        failures.append(f"inspect state {status.state} != {expect['state']}")
    if "governed_state" in expect and status.governed_state != expect["governed_state"]:
        failures.append(f"governed_state {status.governed_state} != {expect['governed_state']}")


def _check_result(root: Path, case: dict[str, Any], failures: list[str]) -> None:
    expect = case.get("result") or {}
    if not expect:
        return
    result = retrieve_result(root, expect["task_id"])
    if result.status != expect["status"]:
        failures.append(f"result status {result.status} != {expect['status']}")
    for gap in expect.get("gaps") or ():
        if not any(gap in item for item in result.gaps):
            failures.append(f"result gap {gap!r} missing")


def _check_evidence(root: Path, case: dict[str, Any], failures: list[str]) -> None:
    expect = case.get("evidence") or {}
    if not expect:
        return
    bundle = retrieve_evidence(root, expect["task_id"])
    kinds = {a.kind for a in bundle.artifacts}
    for kind in expect.get("kinds") or ():
        if kind not in kinds:
            failures.append(f"evidence kind {kind!r} missing")
    for item in expect.get("unresolved") or ():
        if not any(item in entry for entry in bundle.unresolved):
            failures.append(f"evidence unresolved {item!r} missing")


def _check_handoff(root: Path, case: dict[str, Any], failures: list[str]) -> None:
    expect = case.get("handoff") or {}
    if not expect:
        return
    try:
        handoff = prepare_handoff(root, expect["task_id"], expect["to"])
    except ContractError as exc:
        refused = expect.get("refuse")
        if refused and refused in str(exc):
            return
        failures.append(f"handoff refused unexpectedly: {exc}")
        return
    if expect.get("refuse"):
        failures.append(f"handoff expected refusal {expect['refuse']}")
    else:
        if handoff.delivery != expect.get("delivery", "prepared"):
            failures.append(f"delivery {handoff.delivery}")
        if not handoff.evidence_refs and expect.get("evidence_refs"):
            failures.append("handoff carries no evidence refs")


def _check_health(root: Path, case: dict[str, Any], failures: list[str]) -> None:
    expect = case.get("health") or {}
    if not expect:
        return
    report = health(root)
    if "state" in expect and report.state != expect["state"]:
        failures.append(f"health state {report.state} != {expect['state']}")
    if "capabilities_min" in expect and report.capabilities < int(expect["capabilities_min"]):
        failures.append(f"capabilities {report.capabilities} < {expect['capabilities_min']}")
    for state, count in (expect.get("tasks_by_state") or {}).items():
        if report.tasks_by_state.get(state) != count:
            failures.append(
                f"tasks_by_state[{state}] {report.tasks_by_state.get(state)} != {count}"
            )


def _run_case(case: dict[str, Any], root: Path) -> dict[str, Any]:
    failures: list[str] = []
    setup = case.get("setup") or {}
    for submit in setup.get("submits") or ():
        submit_task(
            root,
            ForgeTaskRequest(
                task_id=submit["task_id"],
                capability_id=submit["capability_id"],
                intent=submit.get("intent", "eval"),
                risk=submit.get("risk", "read_only"),
            ),
            acknowledge_risk=True,
        )
    for link in setup.get("attachments") or ():
        _governed(root, link["governed"], link.get("governed_state"))
        attach_task(root, link["task_id"], link["governed"])

    capabilities_min = (case.get("capabilities") or {}).get("capabilities_min")
    if capabilities_min is not None and len(discover_capabilities()) < int(capabilities_min):
        failures.append("capability descriptor count below minimum")
    _check_submit(root, case, failures)
    _check_inspect(root, case, failures)
    _check_result(root, case, failures)
    _check_evidence(root, case, failures)
    _check_handoff(root, case, failures)
    _check_health(root, case, failures)
    return {"id": case["id"], "passed": not failures, "failures": failures}


def run_forge_protocol(corpus: Path, *, root: Path | None = None) -> dict[str, Any]:
    import tempfile

    cases = load_cases(corpus)
    results: list[dict[str, Any]] = []
    for case in cases:
        with tempfile.TemporaryDirectory(prefix="forge-eval-") as tmp:
            results.append(_run_case(case, root or Path(tmp)))
    failed = [result["id"] for result in results if not result["passed"]]
    return {
        "schema": "apiforge/forge-protocol-evals/v1",
        "corpus": str(corpus),
        "cases": results,
        "totals": {"cases": len(results), "failed": len(failed), "failed_ids": failed},
        "passed": not failed,
    }


__all__ = ["load_cases", "run_forge_protocol"]
