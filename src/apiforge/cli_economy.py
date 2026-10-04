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

    @economy_app.command("ledger")
    def economy_ledger(
        run_id: str = typer.Option(..., "--run-id"),
        root: Path = typer.Option(Path(".apiforge"), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Per-basis token rollup for a run — observed and estimated never mix."""
        from apiforge.cli import _echo_json, _run
        from apiforge.economy.token_ledger import build_ledger, load_entries

        def work() -> dict[str, object]:
            rows, unparsed = load_entries(root, run_id)
            ledger = build_ledger(run_id, rows)
            payload = ledger.model_dump(mode="json")
            if unparsed:
                payload["unparsed_rows"] = unparsed
            return payload

        _echo_json(_run(work), detail_level)

    @economy_app.command("record-usage")
    def economy_record_usage(
        run_id: str = typer.Option(..., "--run-id"),
        task_id: str | None = typer.Option(None, "--task-id"),
        agent: str | None = typer.Option(None, "--agent"),
        transcript: Path | None = typer.Option(
            None, "--transcript", help="Host transcript JSONL; derives observed rows."
        ),
        estimate: int | None = typer.Option(
            None, "--estimate", help="Declared token estimate; derives an estimated row."
        ),
        method: str = typer.Option("caller-declared", "--method"),
        recorded_at: str = typer.Option(..., "--recorded-at"),
        root: Path = typer.Option(Path(".apiforge"), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Append usage rows for a run; the file is append-only."""
        from apiforge.cli import _echo_json, _run
        from apiforge.contracts.token_economics import TokenLedgerEntry
        from apiforge.economy.token_ledger import (
            append_usage,
            entry_id,
            estimated_accounting,
            transcript_accounting,
        )
        from apiforge.economy.tokens import read_transcript

        def work() -> dict[str, object]:
            written: list[str] = []
            if transcript is not None:
                observed = read_transcript(transcript)
                for model, usage in observed["models"].items():
                    accounting = transcript_accounting(model, usage, recorded=str(transcript))
                    record = TokenLedgerEntry(
                        entry_id=entry_id(run_id, accounting, recorded_at),
                        run_id=run_id,
                        task_id=task_id,
                        agent=agent,
                        accounting=accounting,
                        recorded_at=recorded_at,
                        provenance=(f"transcript:{transcript}",),
                    )
                    append_usage(root, record)
                    written.append(record.entry_id)
            if estimate is not None:
                accounting = estimated_accounting(estimate, method=method)
                record = TokenLedgerEntry(
                    entry_id=entry_id(run_id, accounting, recorded_at),
                    run_id=run_id,
                    task_id=task_id,
                    agent=agent,
                    accounting=accounting,
                    recorded_at=recorded_at,
                    provenance=("caller:declared-estimate",),
                )
                append_usage(root, record)
                written.append(record.entry_id)
            if not written:
                from apiforge.economy.run_ledger import EconomyError

                raise EconomyError(
                    "AF-ECONOMY-USAGE-EMPTY",
                    "record-usage requires --transcript and/or --estimate",
                    field="run_id",
                    unlock="pass --transcript <jsonl> or --estimate <tokens>",
                )
            return {"written": written, "run_id": run_id}

        _echo_json(_run(work), detail_level)

    @economy_app.command("pricing")
    def economy_pricing(
        pricing: Path | None = typer.Option(None, "--pricing"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """List the declared pricing catalog — prices are never hardcoded."""
        from apiforge.cli import _echo_json, _run
        from apiforge.economy.pricing import describe_catalog, load_pricing

        def work() -> dict[str, object]:
            catalog = load_pricing(pricing) if pricing is not None else load_pricing()
            return describe_catalog(catalog)

        _echo_json(_run(work), detail_level)

    @economy_app.command("cost")
    def economy_cost(
        provider: str = typer.Option(..., "--provider"),
        model: str = typer.Option(..., "--model"),
        accounting: str = typer.Option(..., "--accounting", help="TokenAccounting JSON or file."),
        at: str | None = typer.Option(None, "--at"),
        pricing: Path | None = typer.Option(None, "--pricing"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Price an accounting under the declared catalog; gaps stay named."""
        from apiforge.cli import _echo_json, _run
        from apiforge.contracts.token_economics import TokenAccounting
        from apiforge.economy.pricing import cost_for, load_pricing, price_for

        def work() -> dict[str, object]:
            catalog = load_pricing(pricing) if pricing is not None else load_pricing()
            row = price_for(catalog, provider, model, at=at)
            if row is None:
                from apiforge.economy.run_ledger import EconomyError

                raise EconomyError(
                    "AF-ECONOMY-PRICING-MISSING",
                    f"no pricing row for {provider}/{model}" + (f" at {at}" if at else ""),
                    field="pricing",
                    unlock="declare a ProviderPricing entry in the catalog yaml",
                )
            usage = TokenAccounting.model_validate(_json_value(accounting))
            return cost_for(usage, row).model_dump(mode="json")

        _echo_json(_run(work), detail_level)

    @economy_app.command("reconcile")
    def economy_reconcile(
        run_id: str = typer.Option(..., "--run-id"),
        estimate: str = typer.Option(
            ..., "--estimate", help="Estimate JSON/yaml or file: tokens/cost/tool_calls/elapsed_ms."
        ),
        observed_cost: float | None = typer.Option(None, "--observed-cost"),
        root: Path = typer.Option(Path(".apiforge"), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§22 estimated vs observed for a run, with calibration error per axis."""
        from apiforge.cli import _echo_json, _run
        from apiforge.economy.reconciliation import estimate_axis, reconcile, run_observed
        from apiforge.economy.token_ledger import load_usage_estimate

        def work() -> dict[str, object]:
            path = Path(estimate)
            raw = load_usage_estimate(path) if path.is_file() else json.loads(estimate)
            result = reconcile(
                f"run:{run_id}",
                estimate_axis(raw),
                run_observed(root, run_id, observed_cost=observed_cost),
            )
            return result.model_dump(mode="json")

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
