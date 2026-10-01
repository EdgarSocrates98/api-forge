"""Runtime policies, gates and evidence-bound trigger decisions."""

from __future__ import annotations

from pathlib import Path

import yaml

from apiforge.contracts.agentic import AgenticPolicy
from apiforge.contracts.base import ContractError


def _policy_path() -> Path:
    return Path(__file__).resolve().parents[1] / "rules" / "agentic_runtime.yaml"


def load_policies(path: Path | None = None) -> dict[str, AgenticPolicy]:
    source = path or _policy_path()
    try:
        document = yaml.safe_load(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ContractError("AF-RUNTIME-POLICY", str(exc)) from exc
    raw = document.get("runtime", {}).get("policies") if isinstance(document, dict) else None
    if not isinstance(raw, dict):
        raise ContractError("AF-RUNTIME-POLICY", "missing runtime.policies")
    policies: dict[str, AgenticPolicy] = {}
    for policy_id, values in raw.items():
        if not isinstance(values, dict):
            raise ContractError("AF-RUNTIME-POLICY", f"policy {policy_id!r} is not a mapping")
        policies[str(policy_id)] = AgenticPolicy(policy_id=str(policy_id), **values)
    return policies


def load_policy(policy_id: str = "local-ci-safe", path: Path | None = None) -> AgenticPolicy:
    policies = load_policies(path)
    try:
        return policies[policy_id]
    except KeyError as exc:
        raise ContractError("AF-RUNTIME-POLICY", f"unknown policy {policy_id!r}") from exc


def should_open_room(
    *,
    policy: AgenticPolicy,
    risk: str,
    confidence: float | None,
    unresolved: tuple[str, ...],
    conflicting_facts: bool,
    requested_by_user: bool,
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if requested_by_user and "user_requested" in policy.debate_triggers:
        reasons.append("user_requested")
    if conflicting_facts and "conflicting_evidence" in policy.debate_triggers:
        reasons.append("conflicting_evidence")
    if risk in policy.critic_risks and "high_risk" in policy.debate_triggers:
        reasons.append("high_risk")
    if unresolved:
        reasons.append("unresolved")
    if confidence is not None and confidence < 0.70 and "low_confidence" in policy.debate_triggers:
        reasons.append("low_confidence")
    return bool(reasons), tuple(sorted(set(reasons)))


def requires_critic(policy: AgenticPolicy, risk: str) -> bool:
    return risk in policy.critic_risks


def requires_human_gate(policy: AgenticPolicy, reasons: tuple[str, ...]) -> bool:
    return bool(set(reasons).intersection(policy.human_gate_reasons))


def validate_tool(policy: AgenticPolicy, tool_name: str, *, external_mutation: bool) -> None:
    if external_mutation and not policy.allow_external_mutation:
        raise ContractError("AF-RUNTIME-MUTATION", f"tool {tool_name!r} is externally mutating")
    if not tool_name or tool_name.startswith("shell:"):
        raise ContractError("AF-RUNTIME-TOOL", f"tool {tool_name!r} is not allowlisted")
