"""Caveman-inspired, deterministic API investigation workflow catalog."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Workflow(StrEnum):
    INVESTIGATE = "investigate"
    REVIEW = "review"
    MIGRATION = "migration"
    SAFE_REFACTOR = "safe-refactor"
    PERFORMANCE = "performance"
    VERIFY = "verify"


@dataclass(frozen=True)
class WorkflowPlan:
    workflow: str
    phases: tuple[str, ...]
    required_evidence: tuple[str, ...]
    mutation_allowed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "workflow": self.workflow,
            "phases": list(self.phases),
            "required_evidence": list(self.required_evidence),
            "mutation_allowed": self.mutation_allowed,
        }


_PLANS: dict[Workflow, WorkflowPlan] = {
    Workflow.INVESTIGATE: WorkflowPlan(
        "investigate", ("case", "next-step", "collect", "extract", "judge"), ("facts", "findings")
    ),
    Workflow.REVIEW: WorkflowPlan(
        "review",
        ("contract", "security", "architecture", "verify"),
        ("contract", "threat-model", "verification"),
    ),
    Workflow.MIGRATION: WorkflowPlan(
        "migration",
        ("discover", "matrix", "plan", "sandbox", "verify"),
        ("runtime-matrix", "compatibility", "holdout"),
    ),
    Workflow.SAFE_REFACTOR: WorkflowPlan(
        "safe-refactor",
        ("inventory", "impact", "plan", "sandbox", "tests", "verify"),
        ("impact", "test-results", "receipt"),
    ),
    Workflow.PERFORMANCE: WorkflowPlan(
        "performance",
        ("baseline", "scenario", "load", "compare", "verdict"),
        ("baseline", "performance-run", "verdict"),
    ),
    Workflow.VERIFY: WorkflowPlan(
        "verify",
        ("evidence", "independent-check", "holdout", "brief"),
        ("evidence-receipt", "holdout", "outcome-brief"),
    ),
}


def plan_workflow(name: Workflow | str) -> WorkflowPlan:
    try:
        return _PLANS[Workflow(name)]
    except (KeyError, ValueError) as exc:
        raise ValueError(f"AF-WORKFLOW-UNKNOWN: {name!r}") from exc


def list_workflows() -> list[dict[str, object]]:
    return [plan.to_dict() for plan in _PLANS.values()]
