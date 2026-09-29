"""Anti-agentic-theater gate (§29): what does each agent own that no other agent does?

Sources are declarative and local: ``agents/*.md`` frontmatter (``rule_areas``,
``executors``, optional ``apiforge_tools`` — legacy ``tools``), the runtime capability catalog (capability
and decision role per agent) and the agent profiles. An agent with no unique
capability, rule area, executor, tool or decision role is a
``merge-candidate``; the report names the agents whose rule areas cover it.
Nothing is removed — the verdict is evidence for a human decision.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.selective import AgentUniqueness

DECISION_KINDS = frozenset({"reviewer", "critic", "referee"})


def _frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    _, _, rest = text.partition("---")
    head, sep, _ = rest.partition("\n---")
    if not sep:
        return {}
    try:
        data = yaml.safe_load(head) or {}
    except yaml.YAMLError as exc:
        raise ContractError("AF-AGENTS-AUDIT-INVALID", f"{path.name}: {exc}") from exc
    return data if isinstance(data, dict) else {}


def _items(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return tuple(sorted({item.strip() for item in value.split(",") if item.strip()}))
    if isinstance(value, list | tuple):
        return tuple(sorted({str(item).strip() for item in value if str(item).strip()}))
    return ()


def audit_agents(root: Path, agents_dir: Path | None = None) -> dict[str, Any]:
    from apiforge.runtime.registry import load_capabilities

    folder = Path(agents_dir) if agents_dir else Path(root) / "agents"
    if not folder.is_dir():
        raise ContractError("AF-AGENTS-AUDIT-INVALID", f"no agents directory at {folder}")
    docs: dict[str, dict[str, Any]] = {}
    for path in sorted(folder.glob("*.md")):
        meta = _frontmatter(path)
        name = str(meta.get("name") or "")
        if name:
            docs[name] = meta
    capabilities: dict[str, list[str]] = {}
    roles: dict[str, list[str]] = {}
    for capability in load_capabilities().values():
        capabilities.setdefault(capability.agent, []).append(capability.name)
        if capability.kind in DECISION_KINDS:
            roles.setdefault(capability.agent, []).append(capability.kind)
    names = sorted(set(docs) | set(capabilities))
    area_count: Counter[str] = Counter()
    executor_count: Counter[str] = Counter()
    tool_count: Counter[str] = Counter()
    role_count: Counter[str] = Counter()
    capability_count: Counter[str] = Counter()
    for name in names:
        meta = docs.get(name, {})
        area_count.update(_items(meta.get("rule_areas")))
        executor_count.update(_items(meta.get("executors")))
        tool_count.update(_items(meta.get("apiforge_tools", meta.get("tools"))))
        role_count.update(set(roles.get(name, ())))
        capability_count.update(set(capabilities.get(name, ())))
    rows: list[AgentUniqueness] = []
    for name in names:
        meta = docs.get(name, {})
        areas = _items(meta.get("rule_areas"))
        executors = _items(meta.get("executors"))
        tools = _items(meta.get("apiforge_tools", meta.get("tools")))
        owned = tuple(sorted(set(capabilities.get(name, ()))))
        decision = tuple(sorted(set(roles.get(name, ()))))
        flags: dict[str, Any] = {
            "unique_capability": any(capability_count[item] == 1 for item in owned),
            "unique_expertise": any(area_count[item] == 1 for item in areas),
            "unique_validator": any(executor_count[item] == 1 for item in executors),
            "unique_tool": any(tool_count[item] == 1 for item in tools),
            "unique_decision_role": any(role_count[item] == 1 for item in decision),
        }
        verdict = "keep" if any(flags.values()) else "merge-candidate"
        overlaps: tuple[str, ...] = ()
        if verdict == "merge-candidate" and areas:
            overlaps = tuple(
                other
                for other in names
                if other != name
                and set(areas) <= set(_items(docs.get(other, {}).get("rule_areas")))
            )
        rows.append(
            AgentUniqueness(
                agent=name,
                capabilities=owned,
                decision_roles=decision,
                rule_areas=areas,
                executors=executors,
                tools=tools,
                verdict=verdict,  # type: ignore[arg-type]
                overlaps=overlaps,
                **flags,
            )
        )
    candidates = [row.agent for row in rows if row.verdict == "merge-candidate"]
    return {
        "schema": "apiforge/agent-audit/v1",
        "agents": len(rows),
        "keep": len(rows) - len(candidates),
        "merge_candidates": candidates,
        "rows": [row.model_dump(mode="json") for row in rows],
        "note": "report only; removal or merge is a human decision",
    }


__all__ = ["audit_agents"]
