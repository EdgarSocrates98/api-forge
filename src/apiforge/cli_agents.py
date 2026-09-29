"""Agent roster commands: contract lint, referential integrity, routing eval."""

from __future__ import annotations

import json
from pathlib import Path

import typer


def register(agents_app: typer.Typer, evals_app: typer.Typer) -> None:
    @agents_app.command("lint")
    def agents_lint(
        root: Path = typer.Option(Path("."), "--root", help="Repository root."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Agent contract lint: sections, word budget, English, description, access, owned tools."""
        from apiforge.cli import _echo_json, _run
        from apiforge.dispatch.agent_source import lint

        _echo_json(_run(lambda: lint(root)), detail_level)

    @agents_app.command("references")
    def agents_references(
        root: Path = typer.Option(Path("."), "--root", help="Repository root."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Every agent name in rules/code/tests/evals is a coordinator or an active alias."""
        from apiforge.cli import _echo_json, _run
        from apiforge.dispatch.references import check

        _echo_json(_run(lambda: check(root)), detail_level)

    @evals_app.command("agent-routing")
    def evals_agent_routing(
        root: Path = typer.Option(Path("."), "--root", help="Repository root."),
        cases: Path | None = typer.Option(None, "--cases", help="Golden cases JSON."),
        baseline: Path | None = typer.Option(
            None, "--baseline", help="Previous agent-routing report; top-1 may not regress."
        ),
        out: Path | None = typer.Option(None, "--out", help="Write the report JSON here."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Deterministic proxy-router eval: top-1/top-3, per family, protected-role misroutes."""
        from apiforge.cli import _echo_json, _run
        from apiforge.evals.agent_routing import compare, run

        def work() -> dict[str, object]:
            report = run(root, cases).model_dump(mode="json")
            if out is not None:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(
                    json.dumps(report, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
            if baseline is not None:
                report["gate"] = compare(report, json.loads(baseline.read_text(encoding="utf-8")))
            return report

        payload = _run(work)
        _echo_json(payload, detail_level)
        gate = payload.get("gate") if isinstance(payload, dict) else None
        if isinstance(gate, dict) and not gate.get("ok", True):
            raise typer.Exit(1)


__all__ = ["register"]
