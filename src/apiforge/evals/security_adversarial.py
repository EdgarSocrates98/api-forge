"""§25 synthesized adversarial cases against the platform's own defense
surfaces — memory gates, trust propagation, tool authorization and the
data-is-not-instruction boundary.

Everything runs locally against the real modules; no external call is
ever made. A case passes when the observed defense verdict matches the
expected one: ``refused`` = hard deny carrying an AF-* code,
``contained`` = stopped without promotion (quarantine, taint preserved,
authority kept at ``none``), ``escaped`` = the defense failed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.agentic_memory import (
    MemoryCandidate,
    MemoryPolicy,
    MemoryRecord,
)
from apiforge.contracts.base import ContractError
from apiforge.contracts.eval_plane import AdversarialCaseResult, SecurityAdversarialReport
from apiforge.contracts.trust import TrustUnit
from apiforge.memory.security import evaluate_gates
from apiforge.trust.plane import trust_unit
from apiforge.trust.propagation import propagate
from apiforge.trust.tools import authorize, load_tool_risk

NOW = "2026-10-06T00:00:00+00:00"


def load_cases(corpus: Path) -> list[dict[str, Any]]:
    cases = [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [case.get("id") for case in cases]
    if not cases or len(ids) != len(set(ids)):
        raise ContractError(
            "AF-EVALS-INVALID", f"security-adversarial corpus {corpus} empty or duplicated"
        )
    return cases


def _candidate(params: dict[str, Any]) -> MemoryCandidate:
    record_params = dict(params.get("record") or {})
    record = MemoryRecord(
        memory_id=str(record_params.pop("memory_id", "memory:00000000000000aa")),
        content_sha256=str(record_params.pop("content_sha256", "0" * 64)),
        created_at=str(record_params.pop("created_at", NOW)),
        **record_params,
    )
    return MemoryCandidate(
        candidate_id=str(params.get("candidate_id", "candidate:00000000000000bb")),
        record=record,
        proposed_by=str(params.get("proposed_by", "eval-attacker")),
        reason=str(params.get("reason", "adversarial eval")),
        unresolved=tuple(params.get("unresolved") or ()),
    )


def _policy(params: dict[str, Any]) -> MemoryPolicy:
    return MemoryPolicy(
        policy_id=str(params.get("policy_id", "eval-policy")),
        **{key: value for key, value in params.items() if key != "policy_id"},
    )


def _run_memory_gate(params: dict[str, Any]) -> tuple[str, str, str]:
    """Verdict: refused (reject with code) / contained (quarantine) / escaped (persist)."""
    try:
        result = evaluate_gates(
            _candidate(params.get("candidate") or {}),
            _policy(params.get("policy") or {}),
            now=NOW,
        )
    except ValueError as exc:
        return "refused", str(exc).split(":")[0], str(exc)
    verdict = str(result.verdict)
    if verdict == "reject":
        return "refused", str(result.code or ""), str(result.reason)
    if verdict == "quarantine":
        return "contained", str(result.code or ""), str(result.reason)
    return "escaped", "", f"gates returned {verdict!r}"


def _run_tool_authorize(params: dict[str, Any]) -> tuple[str, str, str]:
    profiles, permissions = load_tool_risk()
    decision = authorize(
        str(params["subject"]),
        str(params["tool"]),
        profiles=profiles,
        permissions=permissions,
    )
    if decision.decision == "deny":
        return "refused", str(decision.code or ""), str(decision.reason)
    return "escaped", "", f"{params['subject']} authorized for {params['tool']}"


def _run_trust_propagate(params: dict[str, Any]) -> tuple[str, str, str]:
    try:
        sources = tuple(TrustUnit(**raw) for raw in params.get("sources") or ())
        outcome = propagate(
            sources,
            transform=params.get("transform", "verbatim"),
            subject=str(params.get("subject", "eval-derived")),
            evidence_refs=tuple(params.get("evidence_refs") or ()),
        )
    except ValueError as exc:
        return "refused", str(exc).split(":")[0], str(exc)
    derived = outcome.derived
    escaped = []
    if derived.instruction_authority != "none" and params.get("expect_authority_none", True):
        escaped.append(f"authority={derived.instruction_authority}")
    max_level = params.get("max_trust_level")
    if max_level:
        order = ["untrusted", "candidate", "observed", "verified", "attested"]
        if order.index(str(derived.trust_level)) > order.index(str(max_level)):
            escaped.append(f"trust_level={derived.trust_level} > {max_level}")
    if escaped:
        return "escaped", "", "; ".join(escaped)
    return (
        "contained",
        "",
        f"authority={derived.instruction_authority} trust={derived.trust_level} taint={sorted(derived.taint)}",
    )


def _run_data_promotion(params: dict[str, Any]) -> tuple[str, str, str]:
    try:
        unit = trust_unit(
            str(params.get("origin", "external_untrusted")),  # type: ignore[arg-type]
            subject=str(params.get("subject", "eval-unit")),
            boundary=str(params.get("boundary", "context_capsule")),  # type: ignore[arg-type]
            trust_level=str(params.get("trust_level", "untrusted")),  # type: ignore[arg-type]
            taint=tuple(params.get("taint") or ("external",)),
            scope=str(params.get("scope", "task")),
            evidence_refs=tuple(params.get("evidence_refs") or ()),
        )
    except ValueError as exc:
        return "refused", str(exc).split(":")[0], str(exc)
    if unit.instruction_authority == "none":
        return "contained", "", "data cannot promote itself to instruction"
    return "escaped", "", f"instruction_authority={unit.instruction_authority}"


_VECTORS = {
    "memory_gate": _run_memory_gate,
    "tool_authorize": _run_tool_authorize,
    "trust_propagate": _run_trust_propagate,
    "data_promotion": _run_data_promotion,
}


def _run_case(case: dict[str, Any]) -> AdversarialCaseResult:
    vector = case.get("vector") or {}
    runner = _VECTORS.get(str(vector.get("type")))
    expected = str((case.get("expect") or {}).get("verdict", "contained"))
    if runner is None:
        return AdversarialCaseResult(
            case_id=str(case["id"]),
            attack_class=str(case.get("attack_class", "undeclared")),
            defense=str(vector.get("type", "none")),
            expected=expected,  # type: ignore[arg-type]
            observed="escaped",
            passed=False,
            detail=f"unknown vector {vector.get('type')!r}",
        )
    observed, code, detail = runner(vector.get("params") or {})
    expected_code = (case.get("expect") or {}).get("code")
    passed = observed == expected and (expected_code is None or expected_code in code)
    if expected_code is not None and expected_code not in code and observed == expected:
        detail = f"{detail} (code {code!r} != expected {expected_code!r})"
    return AdversarialCaseResult(
        case_id=str(case["id"]),
        attack_class=str(case.get("attack_class", "undeclared")),
        defense=str(vector["type"]),
        expected=expected,  # type: ignore[arg-type]
        observed=observed,  # type: ignore[arg-type]
        code=code,
        passed=passed,
        detail=detail,
    )


def run_security_adversarial(corpus: Path) -> dict[str, Any]:
    cases = load_cases(corpus)
    results = [_run_case(case) for case in cases]
    report = SecurityAdversarialReport(
        cases=tuple(results),
        totals={
            "cases": len(results),
            "passed": sum(1 for r in results if r.passed),
            "refused": sum(1 for r in results if r.observed == "refused"),
            "contained": sum(1 for r in results if r.observed == "contained"),
            "escaped": sum(1 for r in results if r.observed == "escaped"),
        },
    )
    failed = [result.case_id for result in results if not result.passed]
    return {
        "schema": "apiforge/security-adversarial-evals/v1",
        "corpus": str(corpus),
        "report": report.model_dump(mode="json"),
        "cases": [
            {"id": r.case_id, "passed": r.passed, "observed": r.observed, "detail": r.detail}
            for r in results
        ],
        "totals": {**report.totals, "failed": len(failed), "failed_ids": failed},
        "passed": not failed,
    }


__all__ = ["load_cases", "run_security_adversarial"]
