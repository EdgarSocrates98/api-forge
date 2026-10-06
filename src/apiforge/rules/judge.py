"""Bounded executable rules over the API-IR.

Each rule reads the model's projections and diagnostics and emits `Finding`s
with stable IDs derived from rule id and evidence ids. Uncertainty in the
inventory (dynamic routes, parse failures, include cycles) downgrades
absence claims to `unresolved` — a missing implementation is only `confirmed`
when extraction was complete.
"""

from __future__ import annotations

from apiforge.api_ir.models import ApiModel
from apiforge.core.ids import stable_id
from apiforge.core.models import Finding, FindingStatus, Severity
from apiforge.rules.catalog import RuleMeta, load_catalog

UNCERTAIN_CODES = frozenset(
    {
        "AF-FASTAPI-DYNAMIC-ROUTE",
        "AF-FASTAPI-PARSE",
        "AF-FASTAPI-INCLUDE-CYCLE",
        "AF-FASTAPI-SYMLINK-ESCAPE",
        "AF-SPRING-UNRESOLVED-ROUTE",
        "AF-SPRING-PARSE",
        "AF-GO-UNRESOLVED-ROUTE",
        "AF-GO-PARSE",
    }
)

_SEVERITY_RANK = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
    Severity.INFO: 4,
}


def _finding(
    meta: RuleMeta,
    status: FindingStatus,
    detail: str,
    evidence: tuple[str, ...],
) -> Finding:
    return Finding(
        finding_id=stable_id(
            "finding", {"rule_id": meta.rule_id, "evidence": list(evidence), "detail": detail}
        ),
        rule_id=meta.rule_id,
        status=status,
        severity=meta.severity,
        title=meta.title,
        detail=detail,
        evidence=evidence,
        remediation=meta.remediation,
    )


def judge_api_model(
    model: ApiModel, catalog: dict[str, RuleMeta] | None = None
) -> tuple[Finding, ...]:
    """Evaluate the divergence rules over an API model."""
    meta = catalog if catalog is not None else load_catalog()
    findings: list[Finding] = []
    uncertainty = [d for d in model.diagnostics if d.code in UNCERTAIN_CODES]

    for operation in model.operations:
        label = f"{operation.method.upper()} {operation.path}"
        if operation.contract_projections and not operation.code_projections:
            rule = meta["AF-CONTRACT-001"]
            evidence = tuple(p.fact_id for p in operation.contract_projections)
            if uncertainty:
                blockers = ", ".join(sorted({d.code for d in uncertainty}))
                findings.append(
                    _finding(
                        rule,
                        FindingStatus.UNRESOLVED,
                        f"{label}: contract operation may be missing, but extraction "
                        f"uncertainty ({blockers}) prevents proving absence",
                        evidence,
                    )
                )
            else:
                findings.append(
                    _finding(
                        rule,
                        FindingStatus.CONFIRMED,
                        f"{label}: contract operation has no implementation",
                        evidence,
                    )
                )
        if len(operation.code_projections) > 1:
            findings.append(
                _finding(
                    meta["AF-CODE-001"],
                    FindingStatus.CONFIRMED,
                    f"{label}: {len(operation.code_projections)} handlers bound",
                    tuple(p.fact_id for p in operation.code_projections),
                )
            )
        if operation.code_projections and not operation.contract_projections:
            findings.append(
                _finding(
                    meta["AF-CODE-002"],
                    FindingStatus.CONFIRMED,
                    f"{label}: code route has no contract operation",
                    tuple(p.fact_id for p in operation.code_projections),
                )
            )

    rule = meta["AF-CODE-003"]
    for diagnostic in uncertainty:
        where = (
            f"{diagnostic.source.path}:{diagnostic.source.line}"
            if diagnostic.source
            else "<unknown>"
        )
        findings.append(
            _finding(
                rule,
                FindingStatus.UNRESOLVED,
                f"{diagnostic.code} at {where}: {diagnostic.message}",
                (),
            )
        )

    findings.sort(key=lambda f: (_SEVERITY_RANK[f.severity], f.rule_id, f.finding_id))
    return tuple(findings)
