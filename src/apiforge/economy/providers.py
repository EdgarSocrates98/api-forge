"""Provider-agnostic tiering (§61–63): capabilities and evidence choose the tier, not names.

``decide_tier`` returns T0 for capabilities with a deterministic
implementation, T3 for high-risk work, T1 only when a fresh promoted
scorecard proves the cheap tier for that task family at or above the quality
floor, and T2 otherwise — "cheap model is enough" is never assumed.
"""

from __future__ import annotations

from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.agentic import AgentScorecard
from apiforge.contracts.base import ContractError
from apiforge.contracts.economy_extras import ProviderCapability, TierDecision

PROVIDERS_FILE = Path(__file__).resolve().parents[1] / "rules" / "providers.yaml"


@lru_cache(maxsize=2)
def load_providers(path: Path = PROVIDERS_FILE) -> dict[str, Any]:
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ContractError("AF-PROVIDER-POLICY-INVALID", f"{path}: {exc}") from exc
    if raw.get("schema") != "apiforge/providers/v1":
        raise ContractError("AF-PROVIDER-POLICY-INVALID", f"{path}: unexpected schema")
    return {
        "quality_floor": float(raw.get("quality_floor", 0.95)),
        "providers": tuple(
            ProviderCapability.model_validate(row) for row in raw.get("providers") or ()
        ),
        "deterministic": frozenset(
            str(item) for item in raw.get("deterministic_capabilities") or ()
        ),
        "high_risk": frozenset(str(item) for item in raw.get("high_risk") or ()),
    }


def _providers(tier: str) -> tuple[str, ...]:
    return tuple(item.provider for item in load_providers()["providers"] if item.tier == tier)


def decide_tier(
    capability: str,
    risk: str,
    *,
    family: str | None = None,
    scorecards: Sequence[AgentScorecard] = (),
) -> TierDecision:
    table = load_providers()
    base: dict[str, Any] = {"capability": capability, "risk": risk, "family": family}
    if capability in table["deterministic"]:
        return TierDecision(
            **base, tier="T0", reason="deterministic implementation answers without a model"
        )
    if risk in table["high_risk"]:
        return TierDecision(
            **base,
            tier="T3",
            providers=_providers("T3"),
            reason=f"risk {risk} requires the strongest tier",
        )
    wanted = f"{family or capability}@T1"
    proof = next(
        (
            card
            for card in scorecards
            if card.profile_id == wanted
            and card.freshness_state == "fresh"
            and card.quality_promoted
            and card.quality_score >= table["quality_floor"]
        ),
        None,
    )
    if proof is not None:
        return TierDecision(
            **base,
            tier="T1",
            providers=_providers("T1"),
            reason=(
                f"scorecard {proof.profile_id} proves quality {proof.quality_score:.2f} "
                f">= floor {table['quality_floor']:.2f} over {proof.evaluation_count} evaluations"
            ),
        )
    return TierDecision(
        **base,
        tier="T2",
        providers=_providers("T2"),
        reason="no benchmark evidence for a cheaper tier in this task family",
    )


def list_providers() -> dict[str, Any]:
    table = load_providers()
    return {
        "schema": "apiforge/provider-capabilities/v1",
        "quality_floor": table["quality_floor"],
        "providers": [item.model_dump(mode="json") for item in table["providers"]],
        "deterministic_capabilities": sorted(table["deterministic"]),
    }


__all__ = ["decide_tier", "list_providers", "load_providers"]
