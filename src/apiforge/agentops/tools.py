"""Typed Tool Adapter Registry over the existing allowlisted runners."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolAdapter:
    name: str
    category: str
    input_schema: str
    output_schema: str
    parser: str
    evidence_producer: str
    safety_class: str
    compact_filter: str
    capabilities: tuple[str, ...]
    modes: tuple[str, ...]
    runnable: bool
    needs_network: bool
    needs_credentials: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "category": self.category,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "parser": self.parser,
            "evidence_producer": self.evidence_producer,
            "safety_class": self.safety_class,
            "compact_filter": self.compact_filter,
            "capabilities": list(self.capabilities),
            "modes": list(self.modes),
            "runnable": self.runnable,
            "needs_network": self.needs_network,
            "needs_credentials": self.needs_credentials,
        }


def _safety(meta: dict[str, Any]) -> str:
    if meta.get("needs_network") or meta.get("needs_credentials"):
        return "network_or_credentialed"
    return "local_read_only"


def list_tool_adapters() -> list[ToolAdapter]:
    from apiforge.run_tools import TOOL_REGISTRY

    return [
        ToolAdapter(
            name=name,
            category=str(meta["category"]),
            input_schema=str(meta["input"]),
            output_schema=str(meta.get("output", "opaque")),
            parser=str(meta["parser"]),
            evidence_producer=str(meta["evidence_producer"]),
            safety_class=_safety(meta),
            compact_filter=name,
            capabilities=tuple(str(item) for item in meta["capabilities"]),
            modes=tuple(str(item) for item in meta["modes"]),
            runnable=bool(meta["runnable"]),
            needs_network=bool(meta["needs_network"]),
            needs_credentials=bool(meta["needs_credentials"]),
        )
        for name, meta in sorted(TOOL_REGISTRY.items())
    ]


def get_tool_adapter(name: str) -> ToolAdapter:
    for adapter in list_tool_adapters():
        if adapter.name == name:
            return adapter
    raise ValueError(f"AF-TOOL-ADAPTER-UNKNOWN: {name!r}")


def tool_adapter_schema(name: str) -> dict[str, object]:
    return get_tool_adapter(name).to_dict()
