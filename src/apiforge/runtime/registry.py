"""Declarative capability registry for runtime fan-out."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from apiforge.contracts.base import ContractError


@dataclass(frozen=True, slots=True)
class Capability:
    name: str
    agent: str
    kind: str
    risk: str


def load_capabilities(path: Path | None = None) -> dict[str, Capability]:
    source = path or Path(__file__).resolve().parents[1] / "rules" / "agentic_runtime.yaml"
    try:
        document = yaml.safe_load(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ContractError("AF-RUNTIME-REGISTRY", str(exc)) from exc
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
            )
        except KeyError as exc:
            raise ContractError("AF-RUNTIME-REGISTRY", f"capability {name!r} misses {exc}") from exc
    return capabilities


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
