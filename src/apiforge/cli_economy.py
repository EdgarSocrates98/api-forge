"""Economy attribution commands: stats by run/source and rule-based explain."""

from __future__ import annotations

import json
from pathlib import Path

import typer


def register(economy_app: typer.Typer) -> None:
    @economy_app.command("stats")
    def economy_stats(
        root: Path = typer.Option(Path("."), "--root"),
        run_id: str | None = typer.Option(None, "--run-id"),
        transcript: Path | None = typer.Option(
            None, "--transcript", help="Host transcript JSONL; unlocks observed tokens."
        ),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Bytes attributed per run and source; tokens stay unresolved without a transcript."""
        from apiforge.cli import _echo_json, _run
        from apiforge.economy.run_ledger import stats

        _echo_json(_run(lambda: _with_tokens(stats(root, run_id=run_id), transcript)), detail_level)

    @economy_app.command("explain")
    def economy_explain(
        run_id: str = typer.Argument(..., help="run_id printed by `context capsule`."),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Why each ref of a run was spent, from recorded provenance rules only."""
        from apiforge.cli import _echo_json, _run
        from apiforge.economy.run_ledger import explain

        _echo_json(_run(lambda: explain(root, run_id)), detail_level)

    @economy_app.command("roi")
    def economy_roi(
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Per extra capability: calls, facts and unresolved added, outcome changed vs primary."""
        from apiforge.cli import _echo_json, _run
        from apiforge.economy.roi import role_roi

        _echo_json(_run(lambda: role_roi(root)), detail_level)

    @economy_app.command("budget-plan")
    def economy_budget_plan(
        plan: Path = typer.Option(
            ..., "--plan", help="JSON declaration with task_id, limits and created_at."
        ),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Register an immutable hierarchical budget plan."""
        from apiforge.cli import _echo_json, _run
        from apiforge.contracts.agentic_governance import BudgetLimit
        from apiforge.governance.budget import build_plan, persist_plan

        def work() -> dict[str, object]:
            data = json.loads(plan.read_text(encoding="utf-8"))
            limits = tuple(BudgetLimit.model_validate(item) for item in data["limits"])
            built = build_plan(
                task_id=str(data["task_id"]),
                limits=limits,
                created_at=str(data["created_at"]),
                metadata=data.get("metadata"),
            )
            return persist_plan(root, built)

        _echo_json(_run(work), detail_level)

    @economy_app.command("budget-check")
    def economy_budget_check(
        plan_id: str = typer.Option(..., "--plan-id"),
        task_id: str = typer.Option(..., "--task-id"),
        phase: str = typer.Option(..., "--phase"),
        role: str = typer.Option(..., "--role"),
        tool: str = typer.Option(..., "--tool"),
        spend_id: str = typer.Option(..., "--spend-id"),
        cost: str = typer.Option(..., "--cost", help="CostVector JSON or JSON file."),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Check a proposed spend without appending it."""
        from apiforge.cli import _echo_json, _run
        from apiforge.contracts.economy import CostVector
        from apiforge.governance.budget import check_budget, load_plan

        def work() -> object:
            value = _json_value(cost)
            return check_budget(
                root,
                load_plan(root, plan_id),
                task_id=task_id,
                phase=phase,
                role=role,
                tool=tool,
                cost=CostVector.model_validate(value),
                spend_id=spend_id,
            )

        _echo_json(_run(work), detail_level)

    @economy_app.command("budget-spend")
    def economy_budget_spend(
        plan_id: str = typer.Option(..., "--plan-id"),
        spend_id: str = typer.Option(..., "--spend-id"),
        task_id: str = typer.Option(..., "--task-id"),
        phase: str = typer.Option(..., "--phase"),
        role: str = typer.Option(..., "--role"),
        tool: str = typer.Option(..., "--tool"),
        cost: str = typer.Option(..., "--cost", help="CostVector JSON or JSON file."),
        observed_at: str = typer.Option(..., "--now"),
        provenance: list[str] = typer.Option([], "--provenance"),
        evidence: list[str] = typer.Option([], "--evidence"),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Admit and append one measured spend receipt."""
        from apiforge.cli import _echo_json, _run
        from apiforge.contracts.agentic_governance import BudgetSpend
        from apiforge.contracts.economy import CostVector
        from apiforge.governance.budget import load_plan, record_spend

        def work() -> object:
            spend = BudgetSpend(
                spend_id=spend_id,
                plan_id=plan_id,
                task_id=task_id,
                phase=phase,
                role=role,
                tool=tool,
                cost=CostVector.model_validate(_json_value(cost)),
                observed_at=observed_at,
                provenance=tuple(provenance),
                evidence_refs=tuple(evidence),
            )
            return record_spend(root, load_plan(root, plan_id), spend)

        _echo_json(_run(work), detail_level)


def _with_tokens(payload: dict[str, object], transcript: Path | None) -> dict[str, object]:
    if transcript is None:
        return payload
    from apiforge.economy.tokens import read_transcript

    payload["tokens"] = read_transcript(transcript)
    payload["tokens_unresolved"] = False
    return payload


def _json_value(value: str) -> object:
    path = Path(value)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else json.loads(value)


__all__ = ["register"]
