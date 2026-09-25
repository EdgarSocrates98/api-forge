"""Evidence-gated promotion and evolution policy loading."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.routing_evolution import (
    EvolutionMode,
    EvolutionPolicy,
    PromotionGate,
    PromotionState,
)
from apiforge.runtime.evidence_gate import build_evidence_coverage


def _evolution_policy_path() -> Path:
    return Path(__file__).resolve().parents[1] / "rules" / "agentic_runtime.yaml"


def load_evolution_policy(path: Path | None = None) -> EvolutionPolicy:
    """Load the bounded evolution policy from the runtime YAML."""
    source = path or _evolution_policy_path()
    try:
        document = yaml.safe_load(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ContractError("AF-EVOLUTION-POLICY", str(exc)) from exc
    raw = (
        document.get("runtime", {}).get("routing_evolution") if isinstance(document, dict) else None
    )
    if not isinstance(raw, dict):
        raise ContractError("AF-EVOLUTION-POLICY", "missing runtime.routing_evolution")
    adaptive = raw.get("adaptive_plan", {})
    if not isinstance(adaptive, dict):
        raise ContractError("AF-EVOLUTION-POLICY", "adaptive_plan must be a mapping")
    try:
        return EvolutionPolicy.model_validate(
            {
                "active_wave": raw.get("active_wave", 0),
                "mode": raw.get("mode", "local"),
                "promotion": raw.get("promotion", "evidence_gated"),
                "fallback": raw.get("fallback", "static-routing"),
                "allow_external_mutation": raw.get("allow_external_mutation", False),
                "require_rollback_ref": raw.get("require_rollback_ref", True),
                "unknown_evidence": raw.get("unknown_evidence", "unresolved"),
                "adaptive_plan_enabled": adaptive.get("enabled", False),
                "adaptive_plan_max_steps": adaptive.get("max_steps"),
            }
        )
    except (TypeError, ValueError) as exc:
        raise ContractError("AF-EVOLUTION-POLICY", f"invalid routing_evolution: {exc}") from exc


def decide_promotion(
    *,
    decision_id: str,
    policy: EvolutionPolicy,
    required_evidence: Iterable[str],
    available_evidence: Iterable[str],
    rollback_ref: str | None = None,
    limitations: Iterable[str] = (),
) -> PromotionGate:
    """Return an auditable promotion state without external side effects."""
    coverage = build_evidence_coverage(
        required_evidence,
        available_evidence,
        limitations=limitations,
    )
    gaps = list(coverage.missing)
    gaps.extend(coverage.limitations)
    state: PromotionState
    mode: EvolutionMode = policy.mode
    if coverage.state != "complete":
        state = "blocked"
    elif mode == "local":
        if policy.require_rollback_ref and rollback_ref is None:
            state = "blocked"
            gaps.append("rollback reference is required for active promotion")
        else:
            state = "active"
    elif mode == "replay":
        state = "simulated"
    else:
        state = "observed"
    return PromotionGate(
        decision_id=decision_id,
        mode=mode,
        state=state,
        coverage=coverage,
        evidence_refs=coverage.available,
        gaps=tuple(sorted(set(gaps))),
        fallback=policy.fallback,
        policy_version=f"routing-evolution/wave-{policy.active_wave}",
        rollback_ref=rollback_ref,
        limitations=coverage.limitations,
    )


def is_active(gate: PromotionGate) -> bool:
    """Return whether the gate authorizes the local active path."""
    return gate.state == "active" and gate.mode == "local"
