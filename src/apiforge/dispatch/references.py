"""Referential integrity: every agent name used by rules, code, tests and evals exists.

A name is valid when it is a coordinator in ``agents/`` or an alias key of an
active alias table. Alias keys are also allowed inside the alias table itself
and in ``replaces:`` frontmatter.
"""

from __future__ import annotations

import re
from pathlib import Path

from apiforge.dispatch.agent_source import load_roster
from apiforge.dispatch.aliases import AliasTable, load_table

_SUFFIXES = (
    "engineer",
    "architect",
    "reviewer",
    "specialist",
    "planner",
    "verifier",
    "critic",
    "referee",
    "guardian",
    "selector",
    "orchestrator",
    "strategist",
    "control-plane",
)
AGENT_NAME = re.compile(
    r"(?<![A-Za-z0-9_/.-])(aws-api-infra-reviewer|terraform-reviewer|api(?!-forge-)(?:-[a-z0-9]+)*?-(?:"
    + "|".join(_SUFFIXES)
    + r"))(?![A-Za-z0-9_-])"
)
SCOPES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("src/apiforge", (".py", ".yaml", ".yml", ".json")),
    ("scripts", (".py",)),
    ("tests", (".py", ".yaml", ".json")),
    ("evals", (".json", ".yaml", ".yml")),
)
EXCLUDED = ("src/apiforge/rules/agent_aliases.yaml",)
_SKIP_PARTS = {"__pycache__", "fixtures", ".apiforge"}


def _files(root: Path) -> list[Path]:
    found: list[Path] = []
    for folder, suffixes in SCOPES:
        base = root / folder
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            rel = path.relative_to(root).as_posix()
            if (
                path.is_file()
                and path.suffix in suffixes
                and rel not in EXCLUDED
                and not _SKIP_PARTS & set(path.relative_to(root).parts)
            ):
                found.append(path)
    return found


def unknown_references(root: Path, table: AliasTable | None = None) -> list[str]:
    root = Path(root)
    current = table or load_table()
    known = {agent.name for agent in load_roster(root)} | set(current.aliases.values())
    if current.active:
        known |= set(current.aliases)
    problems: list[str] = []
    for path in _files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = path.relative_to(root).as_posix()
        for match in AGENT_NAME.finditer(text):
            name = match.group(1)
            if name not in known:
                line = text.count("\n", 0, match.start()) + 1
                problems.append(f"{rel}:{line}: {name}")
    return sorted(set(problems))


def alias_problems(root: Path, table: AliasTable | None = None) -> list[str]:
    current = table or load_table()
    roster = {agent.name for agent in load_roster(Path(root))}
    problems = [
        f"alias {old} -> {new}: target is not a coordinator"
        for old, new in sorted(current.aliases.items())
        if current.active and new not in roster
    ]
    problems.extend(
        f"alias {old} is still a coordinator file"
        for old in sorted(current.aliases)
        if current.active and old in roster
    )
    return problems


def check(root: Path) -> dict[str, object]:
    unknown = unknown_references(root)
    aliases = alias_problems(root)
    return {"unknown": unknown, "alias_problems": aliases, "ok": not unknown and not aliases}


__all__ = ["AGENT_NAME", "alias_problems", "check", "unknown_references"]
