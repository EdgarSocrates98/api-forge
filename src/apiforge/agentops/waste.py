"""§56–§57 token waste detector: declared thresholds, labeled findings.

Every finding names its evidence basis — ``observed`` when the ledger or
span store proves it, ``estimated`` when a reasonable derivation exists and
``hypothesis`` when only a suspicious shape is visible. Detectors never
hardcode a number; thresholds come from ``rules/agentops_waste.yaml``.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.agentops_report import WasteFinding, WasteReport
from apiforge.contracts.base import ContractError
from apiforge.economy import run_ledger, token_ledger
from apiforge.runtime.agent_telemetry import _directory, _read

POLICY_INVALID_CODE = "AF-AGENTOPS-WASTE-POLICY"
POLICY_PATH = Path(__file__).resolve().parents[1] / "rules" / "agentops_waste.yaml"


def _load_policy(path: Path | None = None) -> dict[str, Any]:
    policy_path = path or POLICY_PATH
    try:
        raw = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    except OSError as exc:
        raise ContractError(POLICY_INVALID_CODE, f"{policy_path}: {exc}") from exc
    if not isinstance(raw.get("detectors"), Mapping):
        raise ContractError(POLICY_INVALID_CODE, f"{policy_path}: detectors mapping missing")
    return dict(raw["detectors"])


def detect_waste(
    root: Path,
    run_id: str,
    *,
    risk: str | None = None,
    policy: dict[str, Any] | None = None,
) -> WasteReport:
    """Run the §56 detector set over one run's ledger, spans and context uses."""
    detectors = policy if policy is not None else _load_policy()
    unresolved: list[str] = []
    findings: list[WasteFinding] = []

    entries, _legacy = run_ledger.entries(root)
    rows = [entry for entry in entries if entry.run_id == run_id]
    spans = [span for span in _read(_directory(root)) if span.run_id == run_id]
    usage = token_ledger.load_entries(root, run_id)[0]

    from apiforge.context.quality import uses_from_ledger

    uses = uses_from_ledger(root, run_id)

    def limit(name: str, key: str, default: int) -> int:
        value = detectors.get(name, {})
        return int(value.get(key, default)) if isinstance(value, Mapping) else default

    # duplicate_context — same ref loaded/assigned beyond the threshold.
    loaded: dict[str, int] = {}
    for use in uses:
        if use.action in ("loaded", "assigned"):
            loaded[use.ref_uri] = loaded.get(use.ref_uri, 0) + 1
    threshold = limit("duplicate_context", "min_loads", 2)
    for uri, count in sorted(loaded.items()):
        if count >= threshold:
            findings.append(
                WasteFinding(
                    kind="duplicate_context",
                    evidence="observed",
                    detail=f"{uri} loaded {count}x in one run",
                    refs=(uri,),
                )
            )

    # duplicate_retrieval — same retrieval/knowledge verb repeated.
    retrieval_verbs = [
        row.verb
        for row in rows
        if row.verb.startswith(("knowledge", "context expand", "knowledge adaptive"))
    ]
    verb_counts: dict[str, int] = {}
    for verb in retrieval_verbs:
        verb_counts[verb] = verb_counts.get(verb, 0) + 1
    threshold = limit("duplicate_retrieval", "min_calls", 2)
    for verb, count in sorted(verb_counts.items()):
        if count >= threshold:
            findings.append(
                WasteFinding(
                    kind="duplicate_retrieval",
                    evidence="observed",
                    detail=f"{verb} ran {count}x",
                    refs=(verb,),
                )
            )

    # repeated_tool_call — identical (verb, sorted refs) rows repeated.
    signatures: dict[tuple[str, tuple[str, ...]], int] = {}
    for row in rows:
        signature = (row.verb, tuple(sorted(ref.uri for ref in row.refs)))
        signatures[signature] = signatures.get(signature, 0) + 1
    threshold = limit("repeated_tool_call", "min_calls", 3)
    for (verb, uris), count in sorted(signatures.items()):
        if uris and count >= threshold:
            findings.append(
                WasteFinding(
                    kind="repeated_tool_call",
                    evidence="observed",
                    detail=f"{verb} with identical refs ran {count}x",
                    refs=tuple(uris[:5]),
                )
            )

    # repeated_rule_lookup — the same rules file ref read repeatedly.
    rule_prefix = str(
        detectors.get("repeated_rule_lookup", {}).get("ref_prefix", "rules/")
        if isinstance(detectors.get("repeated_rule_lookup"), Mapping)
        else "rules/"
    )
    rule_reads: dict[str, int] = {}
    for row in rows:
        for ref in row.refs:
            if rule_prefix in ref.uri:
                rule_reads[ref.uri] = rule_reads.get(ref.uri, 0) + 1
    threshold = limit("repeated_rule_lookup", "min_reads", 3)
    for uri, count in sorted(rule_reads.items()):
        if count >= threshold:
            findings.append(
                WasteFinding(
                    kind="repeated_rule_lookup",
                    evidence="observed",
                    detail=f"{uri} looked up {count}x",
                    refs=(uri,),
                )
            )

    # redundant_agent — distinct agent names on the same run (hypothesis).
    agents = {span.agent_name for span in spans if span.agent_name}
    threshold = limit("redundant_agent", "min_distinct_agents", 2)
    if len(agents) >= threshold:
        findings.append(
            WasteFinding(
                kind="redundant_agent",
                evidence="hypothesis",
                detail=f"{len(agents)} distinct agents on one run — verify role disjointness",
                refs=tuple(sorted(agents)),
            )
        )

    # redundant_review — review spans beyond the first.
    reviews = [span for span in spans if span.operation == "review"]
    threshold = limit("redundant_review", "min_reviews", 2)
    if len(reviews) >= threshold:
        findings.append(
            WasteFinding(
                kind="redundant_review",
                evidence="observed",
                detail=f"{len(reviews)} review spans in one run",
                refs=tuple(span.span_id for span in reviews[:5]),
            )
        )

    # unnecessary_debate — debate spans while declared risk is low.
    debates = [span for span in spans if span.operation == "debate"]
    low = set(detectors.get("unnecessary_debate", {}).get("low_risk_values", ("micro", "low")))
    if debates and risk is not None and risk in low:
        findings.append(
            WasteFinding(
                kind="unnecessary_debate",
                evidence="hypothesis",
                detail=f"{len(debates)} debate spans under declared risk {risk!r}",
                refs=tuple(span.span_id for span in debates[:5]),
            )
        )
    elif debates and risk is None:
        unresolved.append("unnecessary_debate requires the run's declared risk")

    # oversized_tool_output — tool_result_bytes above the declared cap.
    cap = limit("oversized_tool_output", "max_bytes", 32768)
    for row in rows:
        if row.cost.tool_result_bytes > cap:
            findings.append(
                WasteFinding(
                    kind="oversized_tool_output",
                    evidence="observed",
                    detail=f"{row.verb} returned {row.cost.tool_result_bytes}B > {cap}B",
                    refs=tuple(ref.uri for ref in row.refs[:3]),
                )
            )

    # full_file_read — file refs loaded while a symbol verb exists in the run.
    file_cfg = detectors.get("full_file_read", {})
    suffixes = (
        tuple(file_cfg.get("file_suffixes", (".py",)))
        if isinstance(file_cfg, Mapping)
        else (".py",)
    )
    symbol_verbs = (
        tuple(file_cfg.get("symbol_verbs", ("graph",)))
        if isinstance(file_cfg, Mapping)
        else ("graph",)
    )
    has_symbol_verb = any(row.verb.startswith(tuple(symbol_verbs)) for row in rows)
    file_refs = {ref.uri for row in rows for ref in row.refs if ref.uri.endswith(suffixes)}
    if has_symbol_verb and file_refs:
        findings.append(
            WasteFinding(
                kind="full_file_read",
                evidence="estimated",
                detail=f"{len(file_refs)} source files loaded while symbol lookups exist in the run",
                refs=tuple(sorted(file_refs)[:5]),
            )
        )

    # premium_model_misuse — premium-tier model billed on a low-risk run.
    premium = set(
        detectors.get("premium_model_misuse", {}).get("premium_tiers", ("T3",))
        if isinstance(detectors.get("premium_model_misuse"), Mapping)
        else {"T3"}
    )
    if usage:
        if risk is not None and risk in low:
            for entry in usage:
                model = entry.accounting.model or ""
                if any(tier in model for tier in premium):
                    findings.append(
                        WasteFinding(
                            kind="premium_model_misuse",
                            evidence="estimated",
                            detail=f"{model} billed on declared risk {risk!r}",
                            refs=(entry.entry_id,),
                        )
                    )
        elif risk is None:
            unresolved.append("premium_model_misuse requires the run's declared risk")

    # repeated_summary — summary verbs repeated.
    summary_cfg = detectors.get("repeated_summary", {})
    summary_verbs = (
        tuple(summary_cfg.get("verbs", ("brief",)))
        if isinstance(summary_cfg, Mapping)
        else ("brief",)
    )
    threshold = limit("repeated_summary", "min_calls", 2)
    summary_hits = [
        row.verb
        for row in rows
        if any(row.verb.startswith(verb) or verb in row.verb for verb in summary_verbs)
    ]
    if len(summary_hits) >= threshold:
        findings.append(
            WasteFinding(
                kind="repeated_summary",
                evidence="observed",
                detail=f"{len(summary_hits)} summary/brief verbs in one run",
                refs=tuple(summary_hits[:5]),
            )
        )

    # unused_context_expansion — expanded refs never cited or used.
    expanded = {use.ref_uri for use in uses if use.action == "expanded"}
    cited = {use.ref_uri for use in uses if use.action in ("cited", "artifact")}
    unused = expanded - cited
    if unused and len(expanded) >= limit("unused_context_expansion", "min_expanded", 1):
        findings.append(
            WasteFinding(
                kind="unused_context_expansion",
                evidence="estimated",
                detail=f"{len(unused)} expanded refs never cited",
                refs=tuple(sorted(unused)[:5]),
            )
        )

    if not rows and not spans and not uses:
        unresolved.append("run has no ledger rows, spans or context uses to inspect")
    return WasteReport(run_id=run_id, findings=tuple(findings), unresolved=tuple(unresolved))


__all__ = ["POLICY_INVALID_CODE", "detect_waste"]
