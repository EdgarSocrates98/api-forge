"""suggest_fix — findings -> ActionPlan. Pure composition, never applies.

Every step is derived from the rule catalog: a confirmed finding whose
rule declares a ``remediation`` produces one ``remediate`` step carrying
the remediation text and the finding's evidence fact_ids. Steps use the
``remediate`` verb on purpose — it is absent from the dispatch table, so a
plan can never execute by accident; applying a suggestion stays behind the
existing policy-gated mutation path. ``proposed_diff`` is populated only
when a mechanical, verifiable edit exists — heuristic findings carry none.
Findings without catalog remediation are named in ``reason``, not filled.
"""

from __future__ import annotations

from collections.abc import Iterable

from apiforge.contracts.core import ActionPlan, ActionRisk, ActionStep
from apiforge.core.ids import stable_id
from apiforge.core.models import Finding, FindingStatus, JsonValue


def suggest_fix(findings: Iterable[Finding]) -> ActionPlan:
    """Compose a proposed ActionPlan from confirmed findings.

    Unconfirmed findings and rules without declared remediation are skipped
    and named — a suggestion is never invented.
    """
    from apiforge.rules.catalog import load_catalog

    catalog = load_catalog()
    steps: list[ActionStep] = []
    skipped: list[str] = []
    for finding in findings:
        if finding.status is not FindingStatus.CONFIRMED:
            skipped.append(f"{finding.finding_id}({finding.status.value})")
            continue
        meta = catalog.get(finding.rule_id)
        if meta is None or not meta.remediation:
            skipped.append(f"{finding.finding_id}(no catalog remediation)")
            continue
        args: dict[str, JsonValue] = {
            "evidence": tuple(finding.evidence),
            "finding_id": finding.finding_id,
            "intent": meta.remediation,
            "reference": meta.reference,
            "rule_id": finding.rule_id,
        }
        steps.append(ActionStep(verb="remediate", args=args))
    reason = ""
    if skipped:
        reason = "skipped: " + ", ".join(skipped)
    if not steps and not skipped:
        reason = "no findings supplied"
    return ActionPlan(
        id=stable_id(
            "plan",
            {"findings": [f.finding_id for f in findings], "steps": len(steps)},
        ),
        steps=tuple(steps),
        risk=ActionRisk.LOCAL_REVERSIBLE,
        rollback="steps are proposals — discard the plan; applied edits revert via git",
        requires_approval=bool(steps),
        status="proposed",
        reason=reason,
    )
