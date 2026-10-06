"""Gremlin traversal text -> top-level steps and declared shape measures.

Pure text analysis: nothing executes and nothing is inferred beyond the
steps written. Nested anonymous traversals (``repeat(out())``) count for
fan-out and mutation, never as top-level bounds.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_NAME = re.compile(r"\.\s*([A-Za-z_]\w*)\s*\(")
_QUOTED = re.compile(r"""['"]([^'"]+)['"]""")
_MUTATING = re.compile(r"\b(addV|addE|drop|mergeV|mergeE)\s*\(|\.\s*property\s*\(", re.IGNORECASE)
_FANOUT = ("out", "in", "both", "outE", "inE", "bothE")
_EMPTY_FANOUT = re.compile(r"(?<![\w$])(out|in|both|outE|inE|bothE)\s*\(\s*\)", re.IGNORECASE)
_BARE = re.compile(r"(\(\s*|,\s*)([A-Za-z]\w*)\s*\(")
_BOUNDS = frozenset({"limit", "range", "tail", "next", "count", "hasNext"})
_START_FILTERS = frozenset({"hasLabel", "has", "hasId", "hasKey"})
_STOPS = frozenset({"times", "until"})


@dataclass(frozen=True)
class Step:
    name: str
    args: str


def _close(text: str, start: int) -> int:
    depth, quote, i = 1, "", start
    while i < len(text) and depth:
        char = text[i]
        if quote:
            if char == quote and text[i - 1] != "\\":
                quote = ""
        elif char in "'\"":
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        i += 1
    return i


def steps(traversal: str) -> tuple[Step, ...]:
    """Top-level ``.step(args)`` calls in written order; Go PascalCase is normalized."""
    found: list[Step] = []
    pos = 0
    while True:
        match = _NAME.search(traversal, pos)
        if match is None:
            return tuple(found)
        end = _close(traversal, match.end())
        found.append(Step(_canonical_name(match.group(1)), traversal[match.end() : end - 1]))
        pos = end


def _canonical_name(name: str) -> str:
    parts = name.rstrip("_").split("_")
    camel = parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:])
    if len(camel) > 1 and camel[0].isupper() and not camel.isupper():
        return camel[0].lower() + camel[1:]
    return camel


def canonical(traversal: str) -> str:
    """Rewrite gremlin_python snake_case and gremlingo PascalCase steps to Gremlin names."""
    return _NAME.sub(lambda m: f".{_canonical_name(m.group(1))}(", traversal)


def _literals(args: str) -> list[str]:
    return [value.strip() for value in _QUOTED.findall(args) if value.strip()]


def _start_index(names: list[str]) -> int | None:
    for index, name in enumerate(names):
        if name in ("V", "E"):
            return index
    return None


def analyze(traversal: str) -> dict[str, object]:
    """Measures declared by the traversal text."""
    traversal = _BARE.sub(
        lambda m: f"{m.group(1)}{_canonical_name(m.group(2))}(", canonical(traversal)
    )
    chain = steps(traversal)
    names = [step.name for step in chain]
    risks: list[str] = []
    if "repeat" in names and not _STOPS & set(names):
        risks.append("repeat-without-stop")
    if _EMPTY_FANOUT.search(traversal):
        risks.append("fanout-without-edge-label")
    start = _start_index(names)
    if start is not None and not chain[start].args.strip():
        following = names[start + 1 : start + 2]
        if not (set(following) & (_START_FILTERS | _BOUNDS)):
            risks.append("unfiltered-start")
    labels: set[str] = set()
    edge_labels: set[str] = set()
    for step in chain:
        if step.name in ("hasLabel", "addV"):
            labels.update(_literals(step.args))
        elif step.name == "has":
            literals = _literals(step.args)
            if len(literals) >= 3:
                labels.add(literals[0])
        elif step.name in _FANOUT or step.name == "addE":
            edge_labels.update(_literals(step.args))
    return {
        "bounded": bool(_BOUNDS & set(names)),
        "mutation": bool(_MUTATING.search(traversal)),
        "labels_used": tuple(sorted(labels)),
        "edge_labels_used": tuple(sorted(edge_labels)),
        "shape_risks": tuple(dict.fromkeys(risks)),
    }
