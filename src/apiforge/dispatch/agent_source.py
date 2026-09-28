"""Parse ``agents/*.md`` and lint each coordinator against the agent contract.

A source without ``access`` is legacy: it still renders (verbatim mirrors) and
is linted in report mode, so the roster can migrate one agent at a time.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from apiforge.contracts.agents import (
    REQUIRED_SECTIONS,
    AgentFinding,
    AgentLintReport,
    AgentSource,
)
from apiforge.contracts.base import ContractError

MIN_WORDS = 250
MAX_WORDS = 600
MAX_DESCRIPTION = 300
_FRONT = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", re.DOTALL)
_HEADING = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_PT_MARKERS = frozenset(
    {
        "não",
        "você",
        "quando",
        "para",
        "uma",
        "com",
        "sem",
        "são",
        "também",
        "deve",
        "nunca",
        "entra",
        "pela",
        "pelo",
        "dos",
        "das",
        "ou",
        "é",
    }
)


def _items(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return tuple(item.strip() for item in value.split(",") if item.strip())
    if isinstance(value, list | tuple):
        return tuple(str(item).strip() for item in value if str(item).strip())
    return ()


def parse_agent(path: Path) -> AgentSource:
    raw = path.read_bytes().decode("utf-8")
    match = _FRONT.match(raw.replace("\r\n", "\n"))
    if match is None:
        raise ContractError("AF-AGENT-CONTRACT-FRONTMATTER", f"{path.name}: missing frontmatter")
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        raise ContractError("AF-AGENT-CONTRACT-FRONTMATTER", f"{path.name}: {exc}") from exc
    if not isinstance(meta, dict):
        raise ContractError("AF-AGENT-CONTRACT-FRONTMATTER", f"{path.name}: not a mapping")
    tools = meta.get("apiforge_tools", meta.get("tools"))
    try:
        return AgentSource(
            name=str(meta.get("name") or path.stem),
            stem=path.stem,
            description=" ".join(str(meta.get("description") or "").split()),
            access=meta.get("access"),
            write_scope=meta.get("write_scope"),
            model_tier=meta.get("model_tier"),
            rule_areas=_items(meta.get("rule_areas")),
            executors=_items(meta.get("executors")),
            apiforge_tools=_items(tools),
            replaces=_items(meta.get("replaces")),
            body=match.group(2).strip(),
            raw=raw,
        )
    except ValidationError as exc:
        raise ContractError(
            "AF-AGENT-CONTRACT-FRONTMATTER", f"{path.name}: {str(exc).splitlines()[0]}"
        ) from exc


def coordinator_paths(root: Path) -> list[Path]:
    folder = Path(root) / "agents"
    return sorted(path for path in folder.glob("*.md") if path.is_file())


def load_roster(root: Path) -> tuple[AgentSource, ...]:
    return tuple(parse_agent(path) for path in coordinator_paths(root))


def sections(body: str) -> dict[str, str]:
    found: dict[str, str] = {}
    headings = list(_HEADING.finditer(body))
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(body)
        found[heading.group(1)] = body[heading.end() : end].strip()
    return found


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _portuguese(text: str) -> bool:
    words = re.findall(r"[a-zà-ÿ]+", text.lower())
    if not words:
        return False
    hits = sum(1 for word in words if word in _PT_MARKERS)
    return hits / len(words) > 0.02


def _finding(agent: str, code: str, field: str, detail: str, unlock: str) -> AgentFinding:
    return AgentFinding(agent=agent, code=code, field=field, detail=detail, unlock=unlock)


def lint_agent(agent: AgentSource) -> list[AgentFinding]:
    found: list[AgentFinding] = []
    name = agent.name
    if agent.name != agent.stem:
        found.append(
            _finding(
                name,
                "AF-AGENT-CONTRACT-NAME",
                "name",
                f"name {agent.name} differs from file {agent.stem}.md",
                "make frontmatter name equal the file stem",
            )
        )
    description = agent.description
    if (
        not description
        or len(description) > MAX_DESCRIPTION
        or "Use when" not in description
        or "Not for" not in description
    ):
        found.append(
            _finding(
                name,
                "AF-AGENT-CONTRACT-DESCRIPTION",
                "description",
                f"{len(description)} chars; needs 'Use when' and 'Not for', at most {MAX_DESCRIPTION}",
                "write: Use when <trigger>. Not for <case> (-> <sibling agent>).",
            )
        )
    if agent.access is None:
        found.append(
            _finding(
                name,
                "AF-AGENT-CONTRACT-ACCESS",
                "access",
                "access is not declared",
                "declare access: read-only | writer",
            )
        )
    elif agent.access == "writer" and not agent.write_scope:
        found.append(
            _finding(
                name,
                "AF-AGENT-CONTRACT-ACCESS",
                "write_scope",
                "writer without write_scope",
                "declare write_scope (where the agent may write)",
            )
        )
    present = sections(agent.body)
    missing = [title for title in REQUIRED_SECTIONS if title not in present]
    if missing:
        found.append(
            _finding(
                name,
                "AF-AGENT-CONTRACT-SECTIONS",
                "body",
                f"missing sections: {', '.join(missing)}",
                "add every required '## <section>' heading",
            )
        )
    words = word_count(agent.body)
    if not MIN_WORDS <= words <= MAX_WORDS:
        found.append(
            _finding(
                name,
                "AF-AGENT-CONTRACT-WORDS",
                "body",
                f"{words} words; allowed {MIN_WORDS}-{MAX_WORDS}",
                "keep the body within the budget; shared rules belong in AGENT_PROTOCOL.md",
            )
        )
    if _portuguese(f"{description} {agent.body}"):
        found.append(
            _finding(
                name,
                "AF-AGENT-CONTRACT-LANGUAGE",
                "body",
                "text is not English",
                "write description and body in English",
            )
        )
    if not agent.apiforge_tools:
        found.append(
            _finding(
                name,
                "AF-AGENT-CONTRACT-TOOLS",
                "apiforge_tools",
                "no owned apiforge command declared",
                "list the apiforge commands this agent owns",
            )
        )
    return found


def lint_roster(roster: tuple[AgentSource, ...]) -> AgentLintReport:
    findings: list[AgentFinding] = []
    owners: dict[str, list[str]] = defaultdict(list)
    for agent in roster:
        findings.extend(lint_agent(agent))
        for tool in agent.apiforge_tools:
            owners[tool].append(agent.name)
    for tool, names in sorted(owners.items()):
        if len(names) > 1:
            for name in sorted(names):
                findings.append(
                    _finding(
                        name,
                        "AF-AGENT-CONTRACT-TOOL-OWNER",
                        "apiforge_tools",
                        f"{tool!r} is owned by {', '.join(sorted(names))}",
                        "assign every apiforge command to exactly one agent",
                    )
                )
    failing = {item.agent for item in findings}
    return AgentLintReport(
        agents=len(roster),
        passing=sum(1 for agent in roster if agent.name not in failing),
        findings=tuple(sorted(findings, key=lambda item: (item.agent, item.code, item.field))),
        ok=not findings,
    )


def lint(root: Path) -> AgentLintReport:
    return lint_roster(load_roster(root))


__all__ = [
    "MAX_DESCRIPTION",
    "MAX_WORDS",
    "MIN_WORDS",
    "coordinator_paths",
    "lint",
    "lint_agent",
    "lint_roster",
    "load_roster",
    "parse_agent",
    "sections",
    "word_count",
]
