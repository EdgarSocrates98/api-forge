"""Governance CLI groups: policy, sdd, sandbox, evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer

from apiforge.adapters.fastapi.extractor import extract_fastapi
from apiforge.core.detail import apply_detail_level
from apiforge.evidence.build import EvidenceError, emit_receipt
from apiforge.evidence.verify import verify_receipt
from apiforge.policy.decide import ActionRequest, decide
from apiforge.policy.loader import PolicyLoadError, load_policy
from apiforge.sandbox.diff import SandboxError
from apiforge.sandbox.service import sandbox_apply, sandbox_clean
from apiforge.sdd.checks import check as sdd_check
from apiforge.sdd.checks import status as sdd_status
from apiforge.sdd.service import set_phase
from apiforge.sdd.stamp import stamp

policy_app = typer.Typer(help="Evaluate actions against the policy catalog.")
sdd_app = typer.Typer(help="Spec-driven development artifacts and gates.")
sandbox_app = typer.Typer(help="Copy-based sandbox evaluation.")
evidence_app = typer.Typer(help="Release evidence receipts.")


def _echo(value: object, detail_level: str = "normal") -> None:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    value = apply_detail_level(value, detail_level)
    typer.echo(json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2))


def _fail(exc: Exception) -> None:
    code = getattr(exc, "code", "AF-ERROR")
    detail = getattr(exc, "detail", str(exc))
    typer.echo(f"{code}: {detail}", err=True)
    raise typer.Exit(code=2)


@policy_app.command("check")
def policy_check(
    verb: str = typer.Option(..., "--verb", help="Action verb, e.g. fs.delete."),
    action_class: str | None = typer.Option(
        None, "--action-class", "--class", help="Declared autonomy class."
    ),
    args: list[str] = typer.Option([], "--arg", help="Positional arguments."),
    target: str | None = typer.Option(None, "--target", help="Action target."),
    policy: Path | None = typer.Option(
        None, "--policy", help="Policy YAML; defaults to the packaged catalog."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help="Payload level."),
) -> None:
    """Decide whether an action is allowed, gated or denied."""
    try:
        action = ActionRequest(
            verb=verb, autonomy_class=action_class, args=tuple(args), target=target
        )
        decision = decide(load_policy(policy), action)
    except (PolicyLoadError, ValueError) as exc:
        _fail(exc)
        return
    _echo(decision, detail_level)
    if decision.outcome == "deny":
        raise typer.Exit(code=3)


@sdd_app.command("check")
def sdd_check_cmd(
    root: Path = typer.Option(..., "--root", help="SDD artifacts root."),
    feature: str | None = typer.Option(None, "--feature", help="Single feature."),
    strict: bool = typer.Option(False, "--strict", help="Gaps refuse."),
    detail_level: str = typer.Option("normal", "--detail-level", help="Payload level."),
) -> None:
    """Validate the SDD hash cascade and phase metadata."""
    report = sdd_check(root, feature=feature, strict=strict)
    _echo(report, detail_level)
    if not report.ok:
        raise typer.Exit(code=3)


@sdd_app.command("status")
def sdd_status_cmd(
    root: Path = typer.Option(..., "--root", help="SDD artifacts root."),
    detail_level: str = typer.Option("normal", "--detail-level", help="Payload level."),
) -> None:
    """Summarize per-feature phase status."""
    _echo(sdd_status(root), detail_level)


@sdd_app.command("stamp")
def sdd_stamp_cmd(
    artifact: Path = typer.Option(..., "--artifact", help="Phase artifact."),
    upstream: Path = typer.Option(..., "--upstream", help="Upstream artifact."),
    detail_level: str = typer.Option("normal", "--detail-level", help="Payload level."),
) -> None:
    """Write the upstream sha256 into an artifact's frontmatter."""
    _echo(stamp(artifact, upstream), detail_level)


@sdd_app.command("set-phase")
def sdd_set_phase_cmd(
    root: Path = typer.Option(..., "--root", help="SDD artifacts root."),
    feature: str = typer.Option(..., "--feature"),
    phase: str = typer.Option(..., "--phase"),
    status: str = typer.Option(..., "--status"),
    strict: bool = typer.Option(False, "--strict"),
    override_gate: str | None = typer.Option(None, "--override-gate"),
    override_reason: str | None = typer.Option(None, "--override-reason"),
    override_actor: str | None = typer.Option(None, "--override-actor"),
    detail_level: str = typer.Option("normal", "--detail-level", help="Payload level."),
) -> None:
    """Transition a phase; under --strict, gates require evidence or override."""
    override: dict[str, str] | None = None
    if override_gate:
        override = {
            "gate": override_gate,
            "reason": override_reason or "",
            "actor": override_actor or "",
        }
    try:
        _echo(
            set_phase(
                root,
                feature,
                phase,
                status,
                strict=strict,
                override=override,
            ),
            detail_level,
        )
    except ValueError as exc:
        _fail(exc)


def _fastapi_analyze(root: Path) -> tuple[dict[str, Any], ...]:
    return tuple(
        {"rule_id": "route", "path": str(f.measures["path"])} for f in extract_fastapi(root).facts
    )


@sandbox_app.command("apply")
def sandbox_apply_cmd(
    root: Path = typer.Option(..., "--root", help="Project root to copy."),
    diff: Path = typer.Option(..., "--diff", help="Unified diff file."),
    detail_level: str = typer.Option("normal", "--detail-level", help="Payload level."),
) -> None:
    """Apply a diff to copies of the tree and report the finding delta."""
    try:
        _echo(sandbox_apply(root, diff.read_text(encoding="utf-8"), _fastapi_analyze), detail_level)
    except (SandboxError, OSError) as exc:
        _fail(exc)


@sandbox_app.command("clean")
def sandbox_clean_cmd(
    root: Path = typer.Option(..., "--root", help="Project root."),
    detail_level: str = typer.Option("normal", "--detail-level", help="Payload level."),
) -> None:
    """Remove .apiforge/sandbox and report removed ids."""
    _echo(sandbox_clean(root), detail_level)


@evidence_app.command("emit")
def evidence_emit_cmd(
    case: Path = typer.Option(..., "--case", help="Persisted case directory."),
    out: Path = typer.Option(..., "--out", help="Receipt output path."),
    now: str | None = typer.Option(
        None, "--now", help="Explicit timestamp; the only clock source."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help="Payload level."),
) -> None:
    """Emit a receipt binding artifact paths to their sha256 contents."""
    try:
        receipt = emit_receipt(case, now=now)
    except EvidenceError as exc:
        _fail(exc)
        return
    out.write_text(
        json.dumps(receipt.model_dump(mode="json"), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    _echo(receipt, detail_level)


@evidence_app.command("verify")
def evidence_verify_cmd(
    receipt: Path = typer.Option(..., "--receipt", help="Receipt JSON file."),
    root: Path | None = typer.Option(
        None, "--root", help="Artifact base dir; defaults to receipt.case."
    ),
    detail_level: str = typer.Option("normal", "--detail-level", help="Payload level."),
) -> None:
    """Re-hash every artifact a receipt lists."""
    report = verify_receipt(receipt, root=root)
    _echo(report, detail_level)
    if not report["ok"]:
        raise typer.Exit(code=3)
