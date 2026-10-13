"""§41 dynamic tool disclosure: task -> declared class -> active tool set.

The host decides what it loads; this module is the deterministic advisory
router. Classification runs over declared keywords — first class whose
keyword appears in the task string wins, declaration order breaks ties.
Unknown classes and undeclared tool names land in ``unresolved``.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.tool_surface import ToolDisclosure

POLICY_INVALID_CODE = "AF-MCP-DISCLOSURE-POLICY"
POLICY_PATH = Path(__file__).resolve().parents[1] / "rules" / "tool_disclosure.yaml"


def _load_policy(path: Path | None = None) -> dict[str, Any]:
    policy_path = path or POLICY_PATH
    try:
        raw = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    except OSError as exc:
        raise ContractError(POLICY_INVALID_CODE, f"{policy_path}: {exc}") from exc
    if not isinstance(raw.get("task_classes"), Mapping):
        raise ContractError(POLICY_INVALID_CODE, f"{policy_path}: task_classes mapping missing")
    return {
        "task_classes": dict(raw["task_classes"]),
        "keywords": dict(raw.get("keywords") or {}),
    }


def disclose(
    task: str,
    *,
    surface: str = "full",
    task_class: str | None = None,
    policy: dict[str, Any] | None = None,
) -> ToolDisclosure:
    """Route a task string to its declared active tool set."""
    declared = policy if policy is not None else _load_policy()
    classes: dict[str, Any] = dict(declared["task_classes"])
    keywords: dict[str, Any] = dict(declared.get("keywords") or {})
    unresolved: list[str] = []

    chosen = task_class
    if chosen is None:
        lowered = task.lower()
        for name, words in keywords.items():
            if name in classes and any(str(word).lower() in lowered for word in words or ()):
                chosen = name
                break
    if chosen is None:
        chosen = "unclassified"
        unresolved.append("no declared keyword matched — falling back to the full surface")
    if chosen not in classes:
        unresolved.append(f"task class {chosen!r} not declared — full surface stays active")
        chosen = "unclassified"

    from apiforge.mcp.gateway import full_tools
    from apiforge.mcp.surface import surface_tools

    surface_names = sorted(fn.__name__ for fn in surface_tools(surface))
    if chosen == "unclassified":
        return ToolDisclosure(
            task=task,
            task_class=chosen,
            active_tools=tuple(surface_names),
            dropped_tools=(),
            basis="fallback-full",
            unresolved=tuple(unresolved),
        )

    declared_tools = sorted(str(t) for t in classes[chosen] or ())
    known = set(full_tools())
    unknown = [name for name in declared_tools if name not in known]
    if unknown:
        unresolved.append(f"declared tools not on the registry: {', '.join(unknown)}")
    active = [name for name in declared_tools if name in known]
    on_surface = [name for name in active if name in surface_names]
    if len(on_surface) != len(active):
        unresolved.append(
            f"{len(active) - len(on_surface)} declared tools not on surface {surface!r}"
        )
    dropped = tuple(name for name in surface_names if name not in set(on_surface))
    return ToolDisclosure(
        task=task,
        task_class=chosen,
        active_tools=tuple(on_surface),
        dropped_tools=dropped,
        basis="declared-policy",
        unresolved=tuple(unresolved),
    )


__all__ = ["disclose"]
