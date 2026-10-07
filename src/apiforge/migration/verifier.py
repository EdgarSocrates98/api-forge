"""Conservative migration status and evidence verification."""

from __future__ import annotations

from apiforge.contracts.task import BriefStatus, OutcomeBrief
from apiforge.migration.contracts import MigrationReport


def decide_status(
    *,
    critical_gaps: tuple[str, ...],
    evidence_ok: bool,
    contract_breaking: bool,
    verification_ok: bool,
) -> BriefStatus:
    if critical_gaps or contract_breaking:
        return BriefStatus.BLOCKED
    if not evidence_ok or not verification_ok:
        return BriefStatus.REVIEW
    return BriefStatus.DONE


def verify_report(
    report: MigrationReport,
    *,
    evidence_ok: bool = False,
    verification_ok: bool = False,
    contract_breaking: bool = False,
) -> MigrationReport:
    gaps = list(report.gaps)
    gaps.extend(
        f"{finding.rule_id}: {finding.message}"
        for finding in report.plan.findings
        if finding.blocking
    )
    gap_values = tuple(sorted(set(gaps)))
    status = decide_status(
        critical_gaps=gap_values,
        evidence_ok=evidence_ok,
        contract_breaking=contract_breaking,
        verification_ok=verification_ok,
    )
    outcome = OutcomeBrief(
        status=status,
        outcome=f"verification of {report.spec_identity}",
        proof=report.evidence if status is BriefStatus.DONE else (),
        gaps=gap_values,
        human_action=None
        if status is BriefStatus.DONE
        else "review migration gaps and provide missing evidence",
        open=gap_values,
    )
    return report.model_copy(update={"gaps": gap_values, "outcome": outcome})
