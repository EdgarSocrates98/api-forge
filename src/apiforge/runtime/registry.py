"""Declarative capability registry for runtime fan-out."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from apiforge.contracts.agentic import AgentCapabilityProfile, AgentScorecard
from apiforge.contracts.base import ContractError


@dataclass(frozen=True, slots=True)
class Capability:
    name: str
    agent: str
    kind: str
    risk: str
    state: str = "supported"
    evidence: tuple[str, ...] = ()
    prerequisites: tuple[str, ...] = ()


def _load_yaml(path: Path, code: str) -> object:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ContractError(code, str(exc)) from exc


def load_capabilities(path: Path | None = None) -> dict[str, Capability]:
    source = path or Path(__file__).resolve().parents[1] / "rules" / "agentic_runtime.yaml"
    document = _load_yaml(source, "AF-RUNTIME-REGISTRY")
    values = document.get("runtime", {}).get("capabilities") if isinstance(document, dict) else None
    if not isinstance(values, dict):
        raise ContractError("AF-RUNTIME-REGISTRY", "missing runtime.capabilities")
    capabilities: dict[str, Capability] = {}
    for name, raw in values.items():
        if not isinstance(raw, dict):
            raise ContractError("AF-RUNTIME-REGISTRY", f"capability {name!r} is not a mapping")
        try:
            capabilities[str(name)] = Capability(
                name=str(name),
                agent=str(raw["agent"]),
                kind=str(raw["kind"]),
                risk=str(raw["risk"]),
                state=str(raw.get("state", "supported")),
                evidence=tuple(str(item) for item in raw.get("evidence", ())),
                prerequisites=tuple(str(item) for item in raw.get("prerequisites", ())),
            )
        except KeyError as exc:
            raise ContractError("AF-RUNTIME-REGISTRY", f"capability {name!r} misses {exc}") from exc
    return capabilities


def load_profiles(path: Path | None = None) -> dict[str, AgentCapabilityProfile]:
    source = path or Path(__file__).resolve().parents[1] / "rules" / "agent_profiles.yaml"
    document = _load_yaml(source, "AF-RUNTIME-PROFILES")
    values = document.get("profiles") if isinstance(document, dict) else None
    if not isinstance(values, dict):
        raise ContractError("AF-RUNTIME-PROFILES", "missing profiles mapping")
    profiles: dict[str, AgentCapabilityProfile] = {}
    for profile_id, raw in values.items():
        if not isinstance(raw, dict):
            raise ContractError("AF-RUNTIME-PROFILES", f"profile {profile_id!r} is not a mapping")
        try:
            profile = AgentCapabilityProfile.model_validate({"profile_id": str(profile_id), **raw})
        except (TypeError, ValueError) as exc:
            raise ContractError("AF-RUNTIME-PROFILES", f"profile {profile_id!r}: {exc}") from exc
        profiles[profile.profile_id] = profile
    return profiles


def select_capabilities(
    capabilities: dict[str, Capability],
    *,
    requested: tuple[str, ...] = (),
    risk: str,
) -> tuple[Capability, ...]:
    selected = [capabilities[name] for name in requested if name in capabilities]
    if not selected:
        selected = [item for item in capabilities.values() if item.kind == "specialist"]
    if risk in {"sensitive", "destructive", "irreversible"}:
        selected = [item for item in selected if item.name != "api-data-review"] or selected
    return tuple(sorted(selected, key=lambda item: item.name))


def select_eligible_capabilities(
    capabilities: dict[str, Capability],
    profiles: dict[str, AgentCapabilityProfile],
    *,
    requested: tuple[str, ...] = (),
    risk: str,
    available_evidence: tuple[str, ...] = (),
    scorecards: tuple[AgentScorecard, ...] = (),
) -> tuple[Capability, ...]:
    """Return the legacy eligible projection for existing callers.

    New runtime routing uses ``apiforge.runtime.routing`` so eligibility and
    ranking remain separate and the full decision trace is persisted.
    """
    candidates = select_capabilities(capabilities, requested=requested, risk=risk)
    evidence = set(available_evidence)
    by_agent = {item.agent: item for item in scorecards}
    eligible: list[Capability] = []
    for capability in candidates:
        profile = profiles.get(capability.name)
        if (
            profile is None
            or not profile.enabled
            or capability.state in {"unsupported", "unresolved"}
            or risk not in profile.accepted_risks
        ):
            continue
        required = set(profile.required_evidence) | set(capability.prerequisites)
        if not required.issubset(evidence):
            continue
        eligible.append(capability)
    return tuple(
        sorted(
            eligible,
            key=lambda item: (
                -by_agent.get(
                    item.agent,
                    AgentScorecard(
                        agent=item.agent,
                        profile_id=item.name,
                    ),
                ).quality_score,
                item.name,
            ),
        )
    )
