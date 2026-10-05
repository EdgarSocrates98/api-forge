"""Decision Control Plane lifecycle commands (§28-§32).

Routes are declared in ``rules/control_plane.yaml``; mode transitions are an
append-only overlay under ``.apiforge/control-plane/``. Shadow evaluations
record parallel-run records and never govern; promotion to ``active`` requires
the five §31 requirements plus an approved ApprovalGate.
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


def register(control_app: typer.Typer) -> None:
    @control_app.command("routes")
    def control_routes(
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§28: every declared route with its effective lifecycle mode."""
        from apiforge.cli import _echo_json, _run
        from apiforge.governance.control_plane import all_routes

        def work() -> dict[str, object]:
            routes = all_routes(root)
            return {
                "schema": "apiforge/control-plane-routes/v1",
                "routes": [route.model_dump(mode="json") for route in routes],
            }

        _echo_json(_run(work), detail_level)

    @control_app.command("shadow")
    def control_shadow(
        route: str | None = typer.Option(None, "--route"),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§29: recorded parallel-run observations for a route."""
        from apiforge.cli import _echo_json, _run
        from apiforge.governance.control_plane import shadow_records

        def work() -> dict[str, object]:
            rows = shadow_records(root, route)
            return {
                "schema": "apiforge/shadow-records/v1",
                "route": route,
                "records": [row.model_dump(mode="json") for row in rows],
                "total": len(rows),
            }

        _echo_json(_run(work), detail_level)

    @control_app.command("eval")
    def control_eval(
        route: str = typer.Option(..., "--route"),
        candidate: str = typer.Option("{}", "--candidate", help="Candidate decision JSON."),
        legacy: str = typer.Option("{}", "--legacy", help="Legacy decision JSON."),
        confidence: float | None = typer.Option(None, "--confidence"),
        evidence: list[str] = typer.Option([], "--evidence"),
        trigger: list[str] = typer.Option([], "--trigger", help="§32 trigger names."),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§29-§32: who governs this evaluation under the route's mode."""
        from typing import get_args

        from apiforge.cli import _echo_json, _run
        from apiforge.contracts.agentic_governance import FallbackTrigger
        from apiforge.economy.run_ledger import EconomyError
        from apiforge.governance.control_plane import evaluate_route

        def work() -> dict[str, object]:
            allowed = get_args(FallbackTrigger)
            bad = [item for item in trigger if item not in allowed]
            if bad:
                raise EconomyError(
                    "AF-GOV-TRIGGER-INVALID",
                    f"unknown fallback triggers {bad}; allowed: {sorted(allowed)}",
                    field="trigger",
                    unlock="pass one of the §32 trigger names",
                )
            decision = evaluate_route(
                root,
                route,
                candidate_decision=_payload(candidate),
                legacy_decision=_payload(legacy),
                confidence=confidence,
                evidence_refs=tuple(evidence),
                triggers=tuple(trigger),  # type: ignore[arg-type]
            )
            return decision.model_dump(mode="json")

        _echo_json(_run(work), detail_level)

    @control_app.command("triggers")
    def control_triggers(
        confidence: float | None = typer.Option(None, "--confidence"),
        min_confidence: float = typer.Option(0.5, "--min-confidence"),
        evidence_incomplete: bool = typer.Option(False, "--evidence-incomplete"),
        security_issue: bool = typer.Option(False, "--security-issue"),
        provider_issue: bool = typer.Option(False, "--provider-issue"),
        budget_issue: bool = typer.Option(False, "--budget-issue"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§32: map declared signals to the closed trigger vocabulary."""
        from apiforge.cli import _echo_json, _run
        from apiforge.governance.control_plane import detect_triggers

        def work() -> dict[str, object]:
            found = detect_triggers(
                confidence=confidence,
                evidence_complete=not evidence_incomplete,
                security_issue=security_issue,
                provider_issue=provider_issue,
                budget_issue=budget_issue,
                min_confidence=min_confidence,
            )
            return {"schema": "apiforge/fallback-triggers/v1", "triggers": list(found)}

        _echo_json(_run(work), detail_level)

    @control_app.command("promote")
    def control_promote(
        route: str = typer.Option(..., "--route"),
        evidence: str = typer.Option(..., "--evidence", help="PromotionEvidence JSON or file."),
        approval: Path | None = typer.Option(None, "--approval", help="ApprovalGate JSON."),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§30-§31: one lifecycle step; ACTIVE requires the five requirements."""
        from apiforge.cli import _echo_json, _run
        from apiforge.contracts.agentic import ApprovalGate
        from apiforge.contracts.agentic_governance import PromotionEvidence
        from apiforge.governance.control_plane import promote

        def work() -> dict[str, object]:
            declared = PromotionEvidence.model_validate(_payload(evidence))
            gate = (
                ApprovalGate.model_validate(json.loads(approval.read_text(encoding="utf-8")))
                if approval
                else None
            )
            return promote(root, route, declared, approval=gate).model_dump(mode="json")

        _echo_json(_run(work), detail_level)

    @control_app.command("demote")
    def control_demote(
        route: str = typer.Option(..., "--route"),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§32: step a route back one stage — the safe direction is always open."""
        from apiforge.cli import _echo_json, _run
        from apiforge.governance.control_plane import demote

        def work() -> dict[str, object]:
            return demote(root, route).model_dump(mode="json")

        _echo_json(_run(work), detail_level)


__all__ = ["register"]
