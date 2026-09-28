"""End-to-end agentic quality over recorded specialist outputs (review §P2, D10).

The economy matrix proves deterministic contract correctness and role
coverage; it does not grade what a specialist answered. This eval does, but
without calling any model from the core: every case carries recorded
specialist outputs (``responses``, a verifiable output contract with a
``verdict``) and a ground truth. The runtime runs under each profile with a
``FakeModelAdapter`` that replays those outputs; the primary specialist's
``verdict`` is scored against the ground truth. ``--responses-dir`` overlays
user-provided recorded outputs (``<case_id>.json``: capability → payload).

Claim scope: ``recorded-agentic-outputs`` — quality of the recorded answers
routed through each profile, not live model quality.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError

PROFILES = ("economy", "balanced", "deep")
NOW = "2026-09-28T00:00:00+00:00"
TASK_ID = "agentic-quality-case"
CLAIM_SCOPE = "recorded-agentic-outputs"
VERDICTS = {"breaking", "compatible", "unresolved"}


def load_cases(corpus: Path) -> list[dict[str, Any]]:
    rows = [
        yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [str(row.get("id")) for row in rows]
    if not rows or len(ids) != len(set(ids)):
        raise ContractError(
            "AF-EVALS-INVALID", f"agentic-quality corpus {corpus} empty or duplicated"
        )
    for row in rows:
        if str(row.get("ground_truth")) not in VERDICTS:
            raise ContractError(
                "AF-EVALS-INVALID", f"case {row.get('id')}: ground_truth must be one of {VERDICTS}"
            )
    return rows


def _payload(verdict: str, note: str = "") -> dict[str, object]:
    return {
        "facts": [f"fact:recorded:{verdict}"],
        "assumptions": [],
        "risks": [],
        "unresolved": [],
        "recommendation": f"{verdict}: {note}".strip(": "),
        "verdict": verdict,
        "confidence": 0.9,
    }


def _responses(case: Mapping[str, Any], overlay: Path | None) -> dict[str, dict[str, object]]:
    from apiforge.runtime.registry import load_capabilities

    default = case.get("default_verdict")
    base: dict[str, dict[str, object]] = (
        {name: _payload(str(default)) for name in load_capabilities()} if default else {}
    )
    for name, value in dict(case.get("responses") or {}).items():
        base[str(name)] = _payload(str(value)) if isinstance(value, str) else dict(value)
    if overlay is not None:
        path = Path(overlay) / f"{case['id']}.json"
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ContractError("AF-EVALS-INVALID", f"{path}: capability -> payload object")
            base.update({str(key): dict(value) for key, value in data.items()})
    return base


def _run_case(
    case: Mapping[str, Any], profile: str, root: Path, overlay: Path | None
) -> dict[str, Any]:
    from apiforge.contracts.task import Budgets, TaskRisk, TaskSize, TaskSpec, TaskState
    from apiforge.runtime.adapters import FakeModelAdapter
    from apiforge.runtime.runner import run_runtime
    from apiforge.taskspec.store import create

    project = root / "project"
    project.mkdir(parents=True, exist_ok=True)
    sensitive = str(case.get("risk", "read_only")) == "sensitive"
    create(
        root,
        TaskSpec(
            id=TASK_ID,
            outcome=str(case.get("outcome", "evaluate the contract change")),
            size=TaskSize.M if sensitive else TaskSize.S,
            inputs=(f"project={project}",),
            expected_proofs=("specialist artifact",),
            acceptance_criteria=("specialist verdict matches the ground truth",),
            rollback="discard local run artifacts",
            risk=TaskRisk.SENSITIVE if sensitive else TaskRisk.READ_ONLY,
            state=TaskState.SEALED,
            revision=1,
            budgets=Budgets(max_calls=20),
        ),
    )
    result = run_runtime(
        root, TASK_ID, adapter=FakeModelAdapter(_responses(case, overlay)), now=NOW, profile=profile
    )
    plan_path = Path(str(result.get("run_dir", ""))) / "routing-plan.json"
    primary = (
        json.loads(plan_path.read_text(encoding="utf-8")).get("primary")
        if plan_path.is_file()
        else None
    )
    raw_artifacts = result.get("artifacts")
    artifacts: list[dict[str, Any]] = (
        [item for item in raw_artifacts if isinstance(item, dict)]
        if isinstance(raw_artifacts, list)
        else []
    )
    economy: Any = result.get("economy") or {}
    chosen = next(
        (item for item in artifacts if item.get("capability") == primary),
        next((item for item in artifacts if "verdict" in (item.get("payload") or {})), None),
    )
    answer = (chosen or {}).get("payload", {}).get("verdict")
    expected = str(case["ground_truth"])
    return {
        "case_id": str(case["id"]),
        "profile": profile,
        "primary": primary,
        "answer": answer,
        "expected": expected,
        "answered": answer in VERDICTS,
        "correct": answer == expected,
        "status": str(result.get("status", "")),
        "calls": int(economy.get("calls_used", 0) or 0),
    }


def _refusal(code: str, detail: str, field: str, unlock: str) -> ContractError:
    error = ContractError(code, detail)
    error.field = field  # type: ignore[attr-defined]
    error.unlock = unlock  # type: ignore[attr-defined]
    return error


def load_baseline(path: Path) -> tuple[dict[str, float], str]:
    """A previous agentic-quality report: its per-profile accuracy and sha256."""
    try:
        raw = Path(path).read_bytes()
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict) or data.get("schema") != "apiforge/agentic-quality-eval/v1":
            raise ValueError("not an apiforge/agentic-quality-eval/v1 report")
        accuracy = {str(key): float(value) for key, value in dict(data["accuracy"]).items()}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise _refusal(
            "AF-EVALS-BASELINE-INVALID",
            f"{path}: {exc}",
            "baseline",
            "pass a report saved from `apiforge evals agentic-quality > baseline.json`",
        ) from exc
    return accuracy, hashlib.sha256(raw).hexdigest()


def run_agentic_quality(
    corpus: Path,
    responses_dir: Path | None = None,
    *,
    min_accuracy: float = 1.0,
    baseline: Path | None = None,
) -> dict[str, Any]:
    """Gate = absolute floor per profile AND non-regression (vs deep, vs a baseline).

    Relative gates alone would pass when every profile is equally wrong.
    """
    if not 0.0 <= float(min_accuracy) <= 1.0:
        raise _refusal(
            "AF-EVALS-INPUT-INVALID",
            f"min_accuracy {min_accuracy} is outside [0, 1]",
            "min_accuracy",
            "pass a value between 0 and 1 (1.0 for the canonical corpus)",
        )
    baseline_accuracy, baseline_sha = load_baseline(baseline) if baseline else ({}, None)
    cases = load_cases(Path(corpus))
    rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="af-agentic-quality-") as tmp:
        for index, case in enumerate(cases):
            for profile in PROFILES:
                work = Path(tmp) / f"{index}-{profile}"
                work.mkdir(parents=True)
                rows.append(_run_case(case, profile, work, responses_dir))
    accuracy: dict[str, float] = {}
    for profile in PROFILES:
        mine = [row for row in rows if row["profile"] == profile]
        accuracy[profile] = (
            round(sum(row["correct"] for row in mine) / len(mine), 4) if mine else 0.0
        )
    blocked = [row for row in rows if row["status"] == "BLOCKED"]
    gates: dict[str, bool] = {
        f"{profile}_quality_floor": accuracy[profile] >= min_accuracy for profile in PROFILES
    }
    gates["economy_not_below_deep"] = accuracy["economy"] >= accuracy["deep"]
    gates["balanced_not_below_deep"] = accuracy["balanced"] >= accuracy["deep"]
    for profile in PROFILES:
        if profile in baseline_accuracy:
            gates[f"{profile}_not_below_baseline"] = accuracy[profile] >= baseline_accuracy[profile]
    gates["every_case_answered"] = all(row["answered"] for row in rows)
    gates["no_blocked_runs"] = not blocked
    return {
        "schema": "apiforge/agentic-quality-eval/v1",
        "claim_scope": CLAIM_SCOPE,
        "cases": len(cases),
        "min_accuracy": min_accuracy,
        "baseline_sha256": baseline_sha,
        "baseline_accuracy": baseline_accuracy or None,
        "accuracy": accuracy,
        "gates": gates,
        "passed": all(gates.values()),
        "rows": rows,
    }


__all__ = ["CLAIM_SCOPE", "load_baseline", "load_cases", "run_agentic_quality"]
