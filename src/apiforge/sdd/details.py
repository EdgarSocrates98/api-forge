"""Per-phase content checks: coverage, claims, results and ship evidence."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from apiforge.core.io import text_sha256
from apiforge.sdd.models import SddArtifact, SddIssue
from apiforge.sdd.phases import _emit, _rel_exists


def _check_phase_details(
    root: Path,
    name: str,
    stem: str,
    artifact: SddArtifact,
    artifacts: Mapping[str, SddArtifact],
    refused: list[SddIssue],
    unresolved: list[SddIssue],
    strict: bool,
) -> None:
    meta = artifact.meta
    if stem == "architecture":
        decisions = meta.get("decisions")
        if isinstance(decisions, (list, tuple)):
            for index, decision in enumerate(decisions):
                if isinstance(decision, Mapping) and not decision.get("rollback"):
                    _emit(
                        "AF-SDD-SCHEMA-INVALID",
                        name,
                        f"decisions[{index}] lacks rollback",
                        artifact,
                        refused,
                        unresolved,
                        field=f"decisions[{index}].rollback",
                    )
    if stem == "plan":
        tasks = meta.get("tasks")
        if isinstance(tasks, (list, tuple)):
            for index, task in enumerate(tasks):
                if not isinstance(task, Mapping):
                    continue
                if not task.get("covers"):
                    _emit(
                        "AF-SDD-TASK-WITHOUT-TEST",
                        name,
                        f"tasks[{index}] has no covers",
                        artifact,
                        refused,
                        unresolved,
                        field=f"tasks[{index}].covers",
                    )
                target = task.get("test") or task.get("proof")
                if target is None:
                    _emit(
                        "AF-SDD-TASK-WITHOUT-TEST",
                        name,
                        f"tasks[{index}] declares neither test nor proof",
                        artifact,
                        refused,
                        unresolved,
                        field=f"tasks[{index}]",
                        unlock="add a test or proof path",
                    )
                elif not _rel_exists(root, target):
                    _emit(
                        "AF-SDD-GAP-TEST-NOT-WRITTEN",
                        name,
                        f"tasks[{index}] target {target!r} does not exist yet",
                        artifact,
                        refused,
                        unresolved,
                        gap=True,
                        strict=strict,
                        field=f"tasks[{index}].test",
                    )
            # acceptance coverage: every intent success id must be covered
            intent = artifacts.get("intent")
            if intent is not None and not intent.error:
                success = intent.meta.get("success")
                if isinstance(success, (list, tuple)):
                    covered: set[str] = set()
                    for t in tasks:
                        if not isinstance(t, Mapping):
                            continue
                        task_covers = t.get("covers")
                        if isinstance(task_covers, (list, tuple)):
                            covered.update(str(c) for c in task_covers)
                    for item in success:
                        if str(item) not in covered:
                            _emit(
                                "AF-SDD-ACCEPTANCE-UNCOVERED",
                                name,
                                f"success {item!r} is covered by no plan task",
                                artifact,
                                refused,
                                unresolved,
                                field="tasks[].covers",
                            )
    if stem == "build":
        claims = meta.get("claims")
        if isinstance(claims, (list, tuple)):
            for index, claim in enumerate(claims):
                if (
                    isinstance(claim, Mapping)
                    and claim.get("evidence")
                    and not _rel_exists(root, claim["evidence"])
                ):
                    _emit(
                        "AF-SDD-GAP-FACT-NOT-COLLECTED",
                        name,
                        f"claims[{index}] evidence {claim['evidence']!r} missing",
                        artifact,
                        refused,
                        unresolved,
                        gap=True,
                        strict=strict,
                        field=f"claims[{index}].evidence",
                    )
    if stem == "verify":
        results = meta.get("results")
        if isinstance(results, (list, tuple)):
            for index, result in enumerate(results):
                if (
                    isinstance(result, Mapping)
                    and result.get("finding")
                    and result.get("observed") is not True
                ):
                    _emit(
                        "AF-SDD-GAP-FINDING-NOT-OBSERVED",
                        name,
                        f"results[{index}] expected finding {result['finding']!r} not observed",
                        artifact,
                        refused,
                        unresolved,
                        gap=True,
                        strict=strict,
                        field=f"results[{index}].observed",
                    )
    if stem == "ship":
        evidence = meta.get("evidence")
        if isinstance(evidence, (list, tuple)):
            for index, item in enumerate(evidence):
                if not isinstance(item, Mapping) or not item.get("path"):
                    continue
                ev_path = root.parent / str(item["path"])
                if not ev_path.is_file():
                    _emit(
                        "AF-SDD-GAP-FACT-NOT-COLLECTED",
                        name,
                        f"evidence[{index}] {item['path']!r} does not exist",
                        artifact,
                        refused,
                        unresolved,
                        gap=True,
                        strict=strict,
                        field=f"evidence[{index}].path",
                    )
                elif item.get("sha256") and item["sha256"] != text_sha256(ev_path):
                    _emit(
                        "AF-SDD-EVIDENCE-MISMATCH",
                        name,
                        f"evidence[{index}] {item['path']!r} hash diverges",
                        artifact,
                        refused,
                        unresolved,
                        field=f"evidence[{index}].sha256",
                        unlock="recompute the hash or fix the artifact",
                    )
