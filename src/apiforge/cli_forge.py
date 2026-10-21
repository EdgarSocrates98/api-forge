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

    doctor_app = typer.Typer(
        name="doctor",
        help="forge-doctor-api delegation: discover, governed read-only scan, before/after compare.",
        no_args_is_help=True,
    )
    forge_app.add_typer(doctor_app)

    @doctor_app.command("discover")
    def doctor_discover_cmd(
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Measured presence of forge-doctor-api: absent | untrusted | verified."""
        from apiforge.cli import _echo_json, _run
        from apiforge.forge.doctor import discover_doctor

        _echo_json(_run(lambda: discover_doctor().model_dump(mode="json")), detail_level)

    @doctor_app.command("scan")
    def doctor_scan_cmd(
        target: Path = typer.Option(
            Path("."), "--target", help="Project directory the doctor scans."
        ),
        correlation_id: str | None = typer.Option(None, "--correlation-id"),
        fail_on: str | None = typer.Option(
            None,
            "--fail-on",
            help="Doctor gate categories, comma-separated: breaking,security,policy.",
        ),
        timeout: int = typer.Option(300, "--timeout", help="Seconds before the scan is refused."),
        max_hops: int = typer.Option(4, "--max-hops", help="Chain hop ceiling."),
        allow_unverified: bool = typer.Option(
            False,
            "--allow-unverified",
            help="Run when the doctor identity is discovered but not verified.",
        ),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Governed read-only delegation: `forge-doctor-api scan --format agent`.

        The doctor diagnoses; plan/implement stay with the host. Every refusal
        persists a refused record under .apiforge/forge/delegations/.
        """
        from apiforge.cli import _echo_json, _run
        from apiforge.forge.doctor import DelegationError, delegate_doctor_scan

        def work() -> dict[str, object]:
            categories = [p.strip() for p in (fail_on or "").split(",") if p.strip()]
            try:
                return delegate_doctor_scan(
                    root,
                    target,
                    correlation_id=correlation_id,
                    fail_on=categories,
                    timeout=timeout,
                    max_hops=max_hops,
                    allow_unverified=allow_unverified,
                ).model_dump(mode="json")
            except DelegationError as exc:
                from apiforge.application.analyze import AnalysisError

                raise AnalysisError(exc.code, str(exc).split(": ", 1)[-1]) from exc

        _echo_json(_run(work), detail_level)

    @doctor_app.command("compare")
    def doctor_compare_cmd(
        baseline: str = typer.Option(..., "--baseline", help="Baseline delegation run id."),
        current: str = typer.Option(..., "--current", help="Current delegation run id."),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Before/after revalidation: diff two persisted doctor scans."""
        from apiforge.cli import _echo_json, _run
        from apiforge.forge.doctor import DelegationError, compare_delegations

        def work() -> dict[str, object]:
            try:
                return compare_delegations(root, baseline, current).model_dump(mode="json")
            except DelegationError as exc:
                from apiforge.application.analyze import AnalysisError

                raise AnalysisError(exc.code, str(exc).split(": ", 1)[-1]) from exc

        _echo_json(_run(work), detail_level)

    @doctor_app.command("list")
    def doctor_list_cmd(
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """List persisted delegation runs (completed and refused)."""
        from apiforge.cli import _echo_json, _run
        from apiforge.forge import store

        def work() -> dict[str, object]:
            rows = []
            for run_id in store.delegation_ids(root):
                try:
                    record = store.load_delegation(root, run_id)
                    rows.append(
                        {
                            "run_id": run_id,
                            "status": record.status,
                            "created_at": record.created_at,
                            "findings": len(record.findings),
                            "error": record.error.code if record.error else None,
                        }
                    )
                except Exception as exc:  # noqa: BLE001 — corrupt row is data, not a crash
                    rows.append({"run_id": run_id, "status": "unresolved", "error": str(exc)[:200]})
            return {"delegations": rows}

        _echo_json(_run(work), detail_level)

    @doctor_app.command("show")
    def doctor_show_cmd(
        run_id: str = typer.Option(..., "--run", help="Delegation run id."),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Show a persisted delegation record (refusals included)."""
        from apiforge.cli import _echo_json, _run
        from apiforge.forge import store

        _echo_json(
            _run(lambda: store.load_delegation(root, run_id).model_dump(mode="json")),
            detail_level,
        )


__all__ = ["register"]
