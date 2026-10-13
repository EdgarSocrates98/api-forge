"""Field-validation commands: record, annotate, verify, report, export."""

from __future__ import annotations

from pathlib import Path

import typer

field_app = typer.Typer(
    name="field",
    help="Pre-registered field validation: evidence-joined run records and gap report.",
    no_args_is_help=True,
)


@field_app.command("record")
def field_record(
    task: str = typer.Option(
        ..., "--task", help="Task id pre-registered in docs/field/corpus.yaml."
    ),
    run: list[str] = typer.Option(..., "--run", help="Linked runtime run_id (repeatable)."),
    phase: str = typer.Option("baseline", "--phase", help="baseline | ab_on"),
    started: str = typer.Option(..., "--started", help="RFC3339 wall-clock task start."),
    ended: str = typer.Option(..., "--ended", help="RFC3339 wall-clock task end."),
    executor: str = typer.Option(
        ...,
        "--executor",
        help="Who executed the task: human:sha256:<64 hex> or agent:<roster-name>.",
    ),
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    """Join ledger, summary and checkpoint of linked runs into a field-run/v1 record."""
    from apiforge.cli import _echo_json, _run
    from apiforge.field.annotate import PHASES, _enum
    from apiforge.field.record import record

    def work() -> object:
        checked = _enum(phase, PHASES, "phase")
        return record(
            root,
            task_id=task,
            run_ids=tuple(run),
            phase=checked,  # type: ignore[arg-type]
            started_at=started,
            ended_at=ended,
            executor=executor,
        )

    _echo_json(_run(work), detail_level)


@field_app.command("annotate")
def field_annotate(
    task: str = typer.Option(..., "--task"),
    phase: str = typer.Option("baseline", "--phase"),
    completed: bool | None = typer.Option(None, "--completed/--not-completed"),
    exit_reason: str | None = typer.Option(None, "--exit-reason"),
    manual_context: bool | None = typer.Option(None, "--manual-context/--no-manual-context"),
    human_intervention: bool | None = typer.Option(
        None, "--human-intervention/--no-human-intervention"
    ),
    false_positives: int | None = typer.Option(None, "--false-positives"),
    false_negatives: int | None = typer.Option(None, "--false-negatives"),
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    """Record human fields with closed enums."""
    from apiforge.cli import _echo_json, _run
    from apiforge.field.annotate import annotate

    _echo_json(
        _run(
            lambda: annotate(
                root,
                task_id=task,
                phase=phase,
                task_completed=completed,
                exit_reason=exit_reason,
                manual_context_required=manual_context,
                human_intervention=human_intervention,
                false_positives=false_positives,
                false_negatives=false_negatives,
            )
        ),
        detail_level,
    )


@field_app.command("verify")
def field_verify(
    task: str = typer.Option(..., "--task"),
    verdict: str = typer.Option(..., "--verdict", help="agree | disagree | unresolved"),
    verifier: str = typer.Option(
        ...,
        "--verifier",
        help="Independent verifier: human:sha256:<64 hex> or agent:<roster-name>.",
    ),
    phase: str = typer.Option("baseline", "--phase"),
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    """Blind verifier verdict; never echoes the human labels."""
    from apiforge.cli import _echo_json, _run
    from apiforge.field.annotate import verify

    _echo_json(
        _run(lambda: verify(root, task_id=task, phase=phase, verdict=verdict, verifier=verifier)),
        detail_level,
    )


@field_app.command("report")
def field_report(
    root: Path = typer.Option(Path("."), "--root"),
    ab: bool = typer.Option(False, "--ab", help="Include baseline vs ab_on deltas."),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    """Counts, Wilson 95% CI, theme qualification and H1 verdict from verified runs."""
    from apiforge.cli import _echo_json, _run
    from apiforge.field.report import build_report

    _echo_json(_run(lambda: build_report(root, ab=ab)), detail_level)


@field_app.command("export")
def field_export(
    root: Path = typer.Option(Path("."), "--root"),
    out: Path | None = typer.Option(None, "--out"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    """Write anonymized verified tasks into evals/corpus/field."""
    from apiforge.cli import _echo_json, _run
    from apiforge.field.export import export

    _echo_json(_run(lambda: export(root, out_dir=out)), detail_level)


def register(app: typer.Typer) -> None:
    app.add_typer(field_app, name="field")


__all__ = ["field_app", "register"]
