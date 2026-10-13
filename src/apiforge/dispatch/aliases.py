"""Deprecated agent names → current roster names (``rules/agent_aliases.yaml``).

Resolution happens where a name enters from data (rules, stored runs,
replays). While the table is inactive it is published for evals only and
resolution is a no-op. An aliased name never raises: it resolves and carries
an ``AF-AGENT-ALIAS-DEPRECATED`` warning.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from typing import Any

import yaml

from apiforge.contracts.base import ContractError

DEPRECATED = "AF-AGENT-ALIAS-DEPRECATED"
INVALID = "AF-AGENT-ALIAS-INVALID"


@dataclass(frozen=True)
class AliasTable:
    active: bool
    deprecated_in: str
    aliases: dict[str, str]


@dataclass(frozen=True)
class AliasResolution:
    name: str
    alias_of: str | None = None

    @property
    def warning(self) -> str | None:
        if self.alias_of is None:
            return None
        return f"{DEPRECATED}: {self.alias_of} -> {self.name}"


def parse_table(data: Any) -> AliasTable:
    if not isinstance(data, dict) or not isinstance(data.get("aliases", {}), dict):
        raise ContractError(INVALID, "agent_aliases.yaml must map aliases: {old: new}")
    aliases = {str(old): str(new) for old, new in (data.get("aliases") or {}).items()}
    for old, new in aliases.items():
        if new in aliases:
            raise ContractError(INVALID, f"alias chain {old} -> {new} -> {aliases[new]}")
        if old == new:
            raise ContractError(INVALID, f"alias {old} points to itself")
    return AliasTable(
        active=bool(data.get("active", False)),
        deprecated_in=str(data.get("deprecated_in", "")),
        aliases=aliases,
    )


@lru_cache(maxsize=1)
def load_table() -> AliasTable:
    text = resources.files("apiforge.rules").joinpath("agent_aliases.yaml").read_text("utf-8")
    return parse_table(yaml.safe_load(text))


def resolve_agent(name: str, table: AliasTable | None = None) -> AliasResolution:
    current = table or load_table()
    if not current.active:
        return AliasResolution(name)
    target = current.aliases.get(name)
    return AliasResolution(target, name) if target else AliasResolution(name)


def canonical(name: str, warnings: list[str] | None = None) -> str:
    resolution = resolve_agent(name)
    if warnings is not None and resolution.warning:
        warnings.append(resolution.warning)
    return resolution.name


__all__ = [
    "DEPRECATED",
    "INVALID",
    "AliasResolution",
    "AliasTable",
    "canonical",
    "load_table",
    "parse_table",
    "resolve_agent",
]
