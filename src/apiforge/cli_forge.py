"""Forge Protocol commands: the public §46–§48 interop façade over the
governed runtime — local-first, append-only, honest about delivery."""

from __future__ import annotations

from pathlib import Path

import typer


def register(app: typer.Typer) -> None:
    forge_app = typer.Typer(
        name="forge",
        help="Forge Protocol: capabilities, task submit/inspect/result/evidence, handoff, health.",
        no_args_is_help=True,
    )
    app.add_typer(forge_app)

    @forge_app.command("capabilities")
    def forge_capabilities_cmd(
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§46 discover: public capability descriptors other engines can call."""
        from apiforge.cli import _echo_json, _run
        from apiforge.forge.protocol import discover_capabilities

        _echo_json(
            _run(lambda: [row.model_dump(mode="json") for row in discover_capabilities()]),
            detail_level,
        )

    @forge_app.command("submit")
    def forge_submit_cmd(
        task_id: str = typer.Option(..., "--task-id", help="lowercase, digits, hyphens."),
        capability: str = typer.Option(..., "--capability", help="Public capability_id."),
        intent: str = typer.Option(..., "--intent", help="What the task must achieve."),
        risk: str = typer.Option("read_only", "--risk", help="CapabilityRisk literal."),
        inputs: str | None = typer.Option(
            None, "--inputs", help="JSON object with declared task inputs."
        ),
        requested_by: str = typer.Option("", "--requested-by"),
        origin_engine: str = typer.Option("api-forge", "--origin-engine"),
        acknowledge_risk: bool = typer.Option(
            False, "--acknowledge-risk", help="Required for gated risk classes."
        ),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§47 submit: validate capability + risk gate, persist the request."""
        import json as _json

        from apiforge.cli import _echo_json, _run
        from apiforge.contracts.base import ContractError
        from apiforge.contracts.forge_protocol import ForgeTaskRequest
        from apiforge.forge.protocol import submit_task

        def work() -> dict[str, object]:
            parsed = _json.loads(inputs) if inputs else {}
            if not isinstance(parsed, dict):
                raise ContractError("AF-INPUT-INVALID", "--inputs must be a JSON object")
            request = ForgeTaskRequest(
                task_id=task_id,
                capability_id=capability,
                intent=intent,
                inputs=parsed,
                risk=risk,  # type: ignore[arg-type]
                requested_by=requested_by,
                origin_engine=origin_engine,
            )
            return submit_task(root, request, acknowledge_risk=acknowledge_risk).model_dump(
                mode="json"
            )

        _echo_json(_run(work), detail_level)

    @forge_app.command("attach")
    def forge_attach_cmd(
        task_id: str = typer.Option(..., "--task-id"),
        governed_task: str = typer.Option(
            ..., "--governed-task", help="TaskSpec id to link (must exist)."
        ),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§47 link a forge task to its governed TaskSpec execution unit."""
        from apiforge.cli import _echo_json, _run
        from apiforge.forge.protocol import attach_task

        _echo_json(
            _run(lambda: attach_task(root, task_id, governed_task).model_dump(mode="json")),
            detail_level,
        )

    @forge_app.command("inspect")
    def forge_inspect_cmd(
        task_id: str = typer.Option(..., "--task-id"),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§47 inspect: live wire projection of forge + governed state."""
        from apiforge.cli import _echo_json, _run
        from apiforge.forge.protocol import inspect_task

        _echo_json(_run(lambda: inspect_task(root, task_id).model_dump(mode="json")), detail_level)

    @forge_app.command("result")
    def forge_result_cmd(
        task_id: str = typer.Option(..., "--task-id"),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§47 retrieve result: governed OutcomeBrief mapped, gaps named."""
        from apiforge.cli import _echo_json, _run
        from apiforge.forge.protocol import retrieve_result

        _echo_json(
            _run(lambda: retrieve_result(root, task_id).model_dump(mode="json")),
            detail_level,
        )

    @forge_app.command("evidence")
    def forge_evidence_cmd(
        task_id: str = typer.Option(..., "--task-id"),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§47 retrieve evidence: content-addressed artifact bundle."""
        from apiforge.cli import _echo_json, _run
        from apiforge.forge.protocol import retrieve_evidence

        _echo_json(
            _run(lambda: retrieve_evidence(root, task_id).model_dump(mode="json")),
            detail_level,
        )

    @forge_app.command("handoff")
    def forge_handoff_cmd(
        task_id: str = typer.Option(..., "--task-id"),
        to_engine: str = typer.Option(
            ..., "--to", help="Declared peer engine (rules/forge_protocol.yaml)."
        ),
        context_ref: list[str] = typer.Option(
            [], "--context-ref", help="ctx:// ref to carry (repeatable)."
        ),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§47/§48 handoff: portable bundle — delivery stays a human step."""
        from apiforge.cli import _echo_json, _run
        from apiforge.forge.protocol import prepare_handoff

        _echo_json(
            _run(
                lambda: prepare_handoff(
                    root, task_id, to_engine, context_refs=tuple(context_ref)
                ).model_dump(mode="json")
            ),
            detail_level,
        )

    @forge_app.command("health")
    def forge_health_cmd(
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§47 health: engine, protocol version and declared task counts."""
        from apiforge.cli import _echo_json, _run
        from apiforge.forge.protocol import health

        _echo_json(_run(lambda: health(root).model_dump(mode="json")), detail_level)


__all__ = ["register"]
