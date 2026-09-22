"""Independent verification for adapter and sandbox boundaries."""

from __future__ import annotations

from apiforge.contracts.adapter import AdapterExecution
from apiforge.contracts.sandbox import SandboxCommandResult
from apiforge.contracts.verification import VerificationCheck


def verify_adapter_execution(execution: AdapterExecution) -> VerificationCheck:
    """Verify that adapter claims match its declared execution boundary."""

    evidence = tuple(sorted(execution.evidence_refs))
    if execution.mode == "live_mutation":
        return VerificationCheck(
            check_id="adapter-mutation-boundary",
            axis="security",
            verdict="fail" if execution.status != "blocked" else "pass",
            evidence=evidence,
            gaps=() if execution.status == "blocked" else ("mutation adapter is not blocked",),
            limitation="mutation approval is verified by policy, not by this function",
        )
    if execution.mode == "static" or execution.evidence_level == "heuristic":
        return VerificationCheck(
            check_id="adapter-evidence-level",
            axis="adapter",
            verdict="inconclusive",
            evidence=evidence,
            gaps=("static or heuristic output is not runtime proof",),
            limitation="requires a live read-only observation or an independent fixture oracle",
        )
    passed = execution.status == "completed" and bool(execution.evidence_refs) and not execution.unresolved
    return VerificationCheck(
        check_id="adapter-live-read",
        axis="adapter",
        verdict="pass" if passed else "inconclusive",
        evidence=evidence if passed else (),
        gaps=() if passed else ("live adapter lacks complete evidence or has unresolved diagnostics",),
    )


def verify_sandbox_result(result: SandboxCommandResult) -> VerificationCheck:
    """Verify a sandbox command independently from the process runner."""

    if result.status == "passed" and result.return_code == 0 and result.evidence_refs:
        return VerificationCheck(
            check_id="sandbox-command",
            axis="execution",
            verdict="pass",
            evidence=result.evidence_refs,
            limitation="process isolation strength is host-dependent",
        )
    if result.status in {"blocked", "timed_out", "inconclusive"} or (
        result.status == "passed" and result.return_code == 0
    ):
        return VerificationCheck(
            check_id="sandbox-command",
            axis="execution",
            verdict="inconclusive",
            gaps=(f"sandbox result is {result.status}",),
            limitation="the command must be rerun or explicitly reviewed",
        )
    return VerificationCheck(
        check_id="sandbox-command",
        axis="execution",
        verdict="fail",
        gaps=("sandbox command returned a non-zero exit code",),
    )
