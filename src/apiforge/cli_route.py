"""Model routing and adaptive retrieval commands (§33-§39).

``route model`` ranks declared candidates against declared inputs and §34
scorecards; ``route promote`` moves the model_routing route through the
control-plane lifecycle — scorecard evidence is required so a small
synthetic benchmark alone never promotes (§35).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer


def _payload(value: str) -> dict[str, Any]:
    path = Path(value)
    raw = path.read_text(encoding="utf-8") if path.is_file() else value
    data = json.loads(raw)
    return data if isinstance(data, dict) else {"value": data}


def register(route_app: typer.Typer) -> None:
    @route_app.command("model")
    def route_model(
        inputs: str = typer.Option(..., "--inputs", help="ModelRouteInputs JSON or file."),
        scorecards: str | None = typer.Option(
            None, "--scorecards", help="ModelEvaluation JSONL or scorecards JSON file."
        ),
        task_class: str | None = typer.Option(None, "--task-class"),
        shadow_root: Path | None = typer.Option(
            None, "--shadow-root", help="Record candidate vs legacy in Decision Plane shadow mode."
        ),
        legacy_selected: str | None = typer.Option(None, "--legacy-selected"),
        policy: Path | None = typer.Option(None, "--policy"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§33: rank declared model candidates; quality history is a constraint."""
        from apiforge.cli import _echo_json, _run
        from apiforge.contracts.model_routing import (
            ModelEvaluation,
            ModelRouteInputs,
        )
        from apiforge.runtime.model_router import (
            load_model_router_policy,
            route_model,
            route_model_shadow,
        )
        from apiforge.runtime.model_scorecard import aggregate_scorecards, scorecard_map

        def work() -> dict[str, object]:
            declared = ModelRouteInputs.model_validate(_payload(inputs))
            rules = load_model_router_policy(policy)
            cards = None
            if scorecards:
                raw = Path(scorecards)
                rows = [
                    ModelEvaluation.model_validate(json.loads(line))
                    for line in raw.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
                cards = scorecard_map(
                    aggregate_scorecards(rows),
                    task_class=task_class,  # type: ignore[arg-type]
                )
            if shadow_root is not None:
                return route_model_shadow(
                    shadow_root,
                    declared,
                    rules["candidates"],
                    cards,
                    legacy_decision={"selected": legacy_selected} if legacy_selected else {},
                    policy=rules,
                )
            return route_model(declared, rules["candidates"], cards, policy=rules).model_dump(
                mode="json"
            )

        _echo_json(_run(work), detail_level)

    @route_app.command("scorecard")
    def route_scorecard(
        evaluations: str = typer.Option(..., "--evaluations", help="ModelEvaluation JSONL."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§34: fold evaluation rows into scorecards per provider/model/class."""
        from apiforge.cli import _echo_json, _run
        from apiforge.contracts.model_routing import ModelEvaluation
        from apiforge.runtime.model_scorecard import aggregate_scorecards

        def work() -> dict[str, object]:
            rows = [
                ModelEvaluation.model_validate(json.loads(line))
                for line in Path(evaluations).read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            cards = aggregate_scorecards(rows)
            return {
                "schema": "apiforge/model-scorecards/v1",
                "scorecards": [card.model_dump(mode="json") for card in cards.values()],
            }

        _echo_json(_run(work), detail_level)

    @route_app.command("promote")
    def route_promote(
        route: str = typer.Option("model_routing", "--route"),
        evidence: str = typer.Option(..., "--evidence", help="PromotionEvidence JSON."),
        approval: Path | None = typer.Option(None, "--approval"),
        evaluations: str | None = typer.Option(
            None, "--evaluations", help="ModelEvaluation JSONL proving real traffic"
        ),
        task_class: str | None = typer.Option(None, "--task-class"),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§35: lifecycle promotion gated on scorecard evidence, not benchmarks."""
        from apiforge.cli import _echo_json, _run
        from apiforge.contracts.agentic import ApprovalGate
        from apiforge.contracts.agentic_governance import PromotionEvidence
        from apiforge.contracts.model_routing import ModelEvaluation
        from apiforge.economy.run_ledger import EconomyError
        from apiforge.governance.control_plane import promote
        from apiforge.runtime.model_router import load_model_router_policy
        from apiforge.runtime.model_scorecard import aggregate_scorecards

        def work() -> dict[str, object]:
            declared = PromotionEvidence.model_validate(_payload(evidence))
            rules = load_model_router_policy()
            if evaluations:
                rows = [
                    ModelEvaluation.model_validate(json.loads(line))
                    for line in Path(evaluations).read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
                cards = aggregate_scorecards(rows)
                strong = [
                    card
                    for (provider, model, klass), card in cards.items()
                    if (task_class is None or klass == task_class)
                    and card.evaluation_count >= rules["min_evaluations"]
                    and (card.quality or 0.0) >= rules["quality_floor"]
                ]
                if not strong:
                    raise EconomyError(
                        "AF-ROUTE-PROMOTION-EVIDENCE",
                        "no scorecard reaches min_evaluations + quality_floor; "
                        "a small synthetic benchmark never promotes",
                        field="evaluations",
                        unlock="collect real evaluation traffic for the candidate",
                    )
            gate = (
                ApprovalGate.model_validate(json.loads(approval.read_text(encoding="utf-8")))
                if approval
                else None
            )
            return promote(root, route, declared, approval=gate).model_dump(mode="json")

        _echo_json(_run(work), detail_level)


def register_retrieval(knowledge_app: typer.Typer) -> None:
    @knowledge_app.command("adaptive")
    def knowledge_adaptive(
        query: str = typer.Option(..., "--query"),
        max_level: str = typer.Option("L4", "--max-level", help="L0..L4 ceiling."),
        semantic: bool = typer.Option(False, "--semantic", help="Declare the local adapter."),
        root: Path | None = typer.Option(None, "--root", help="Directory of knowledge packs."),
        graph_dir: Path | None = typer.Option(None, "--graph-dir", help="Graph JSONL directory."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§36: L0→L4 ladder; escalates only while the level is insufficient."""
        from apiforge.cli import _echo_json, _run
        from apiforge.knowledge.levels import adaptive_retrieve
        from apiforge.knowledge.semantic import load_semantic_adapter

        def work() -> dict[str, object]:
            adapter = load_semantic_adapter() if semantic else None
            return adaptive_retrieve(
                query,
                root=root,
                graph_dir=graph_dir,
                semantic=adapter,
                max_level=max_level,  # type: ignore[arg-type]
            ).model_dump(mode="json")

        _echo_json(_run(work), detail_level)

    @knowledge_app.command("rewrite")
    def knowledge_rewrite(
        query: str = typer.Option(..., "--query"),
        deterministic_hits: int = typer.Option(0, "--deterministic-hits"),
        profile: str = typer.Option("balanced", "--profile"),
        budget: str = typer.Option("{}", "--budget", help="budget_remaining JSON."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§39: rewrite only when deterministic retrieval failed + gates allow."""
        from apiforge.cli import _echo_json, _run
        from apiforge.knowledge.rewrite import rewrite_query

        def work() -> dict[str, object]:
            return rewrite_query(
                query,
                deterministic_hits=deterministic_hits,
                budget_remaining=_payload(budget),
                profile=profile,
            ).model_dump(mode="json")

        _echo_json(_run(work), detail_level)


__all__ = ["register", "register_retrieval"]
