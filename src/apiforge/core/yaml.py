"""Strict YAML and JSON loading shared by every contract parser.

Plain ``yaml.safe_load`` silently accepts aliases, merge keys and duplicate
mapping keys, and ``json.loads`` accepts duplicate keys and non-finite numbers.
Neither behavior is acceptable for a contract loader, so both parsers here
reject those constructs by name.
"""

from __future__ import annotations

import json
from math import isfinite
from pathlib import Path
from typing import Any

import yaml
from yaml.constructor import SafeConstructor
from yaml.events import AliasEvent

_SAFE_TAGS = frozenset(
    "tag:yaml.org,2002:" + tag for tag in ("str", "seq", "map", "null", "bool", "int", "float")
)

# Implicitly resolved tags kept: everything else (timestamp, binary, set, omap,
# pairs) would construct values that are not JSON-compatible. `merge` stays so
# `<<` still reaches the merge-key refusal instead of becoming a plain string.
_ALLOWED_IMPLICIT = frozenset(
    "tag:yaml.org,2002:" + tag for tag in ("bool", "int", "float", "null", "merge")
)


class StrictLoadError(ValueError):
    """A rejected input document; ``str()`` always begins with the code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


class _Loader(yaml.SafeLoader):
    """SafeLoader plus refusals for aliases, merge keys, custom tags and dup keys."""

    yaml_implicit_resolvers = {  # noqa: RUF012  # type: ignore[misc]
        first: [(tag, regexp) for tag, regexp in resolvers if tag in _ALLOWED_IMPLICIT]
        for first, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
    }

    def compose_node(self, parent: Any, index: Any) -> Any:
        event = self.peek_event()  # type: ignore[no-untyped-call]
        if isinstance(event, AliasEvent):
            raise StrictLoadError("AF-YAML-ALIAS", "YAML aliases are not supported")
        tag = getattr(event, "tag", None)
        if isinstance(tag, str) and tag:
            if tag == "tag:yaml.org,2002:merge":
                raise StrictLoadError("AF-YAML-MERGE-KEY", "YAML merge keys are not supported")
            if tag not in _SAFE_TAGS:
                raise StrictLoadError("AF-YAML-CUSTOM-TAG", f"custom tag {tag!r} is not supported")
        return super().compose_node(parent, index)


def _strict_construct_mapping(
    loader: yaml.Loader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        try:
            hash(key)
        except TypeError as exc:
            raise StrictLoadError(
                "AF-YAML-INVALID", f"mapping key {key!r} is not hashable"
            ) from exc
        if key in mapping:
            raise StrictLoadError("AF-YAML-DUPLICATE-KEY", f"duplicate mapping key {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _strict_construct_mapping)


def _finite_float(loader: yaml.Loader, node: yaml.ScalarNode) -> float:
    value = SafeConstructor.construct_yaml_float(loader, node)
    if not isfinite(value):
        raise StrictLoadError("AF-YAML-NON-FINITE", f"non-finite float {node.value!r} is not JSON")
    return float(value)


_Loader.add_constructor("tag:yaml.org,2002:float", _finite_float)


def load_yaml_strict(text: str, *, source: str = "<input>") -> object:
    """Parse YAML refusing aliases, merge keys, custom tags and duplicate keys."""
    try:
        return yaml.load(text, Loader=_Loader)
    except StrictLoadError:
        raise
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" line {mark.line + 1}" if mark is not None else ""
        problem = getattr(exc, "problem", None) or str(exc)
        raise StrictLoadError(
            "AF-YAML-INVALID", f"{source}: invalid YAML{where}: {problem}"
        ) from exc


def load_json_strict(text: str, *, source: str = "<input>") -> object:
    """Parse JSON refusing duplicate object keys and non-finite numbers."""

    def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        mapping: dict[str, Any] = {}
        for key, value in pairs:
            if key in mapping:
                raise StrictLoadError(
                    "AF-JSON-DUPLICATE-KEY", f"{source}: duplicate object key {key!r}"
                )
            mapping[key] = value
        return mapping

    def no_constant(name: str) -> None:
        raise StrictLoadError(
            "AF-JSON-NON-FINITE", f"{source}: non-finite literal {name} is not JSON"
        )

    def finite_float(value: str) -> float:
        number = float(value)
        if not isfinite(number):
            raise StrictLoadError("AF-JSON-NON-FINITE", f"{source}: non-finite number {value!r}")
        return number

    try:
        return json.loads(
            text,
            object_pairs_hook=no_duplicates,
            parse_constant=no_constant,
            parse_float=finite_float,
        )
    except StrictLoadError:
        raise
    except json.JSONDecodeError as exc:
        raise StrictLoadError(
            "AF-JSON-INVALID", f"{source}: invalid JSON line {exc.lineno}: {exc.msg}"
        ) from exc


def load_data_file(path: Path) -> object:
    """Load a YAML or JSON document (chosen by suffix) under the strict rules."""
    target = Path(path)
    try:
        text = target.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise StrictLoadError("AF-DOC-NOT-UTF8", f"{target.name}: file is not UTF-8") from exc
    if target.suffix.lower() == ".json":
        return load_json_strict(text, source=target.name)
    return load_yaml_strict(text, source=target.name)


StrictYamlError = StrictLoadError
"""Plan-facing alias: the strict loader's error type is ``StrictLoadError``."""


def load_yaml_mapping(text: str, *, source: str = "<input>") -> dict[Any, Any]:
    """Parse YAML that must be a mapping — frontmatter, catalogs, policies."""
    value = load_yaml_strict(text, source=source)
    if not isinstance(value, dict):
        raise StrictLoadError("AF-YAML-NOT-MAPPING", f"{source}: document is not a mapping")
    return value


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Split a leading ``---`` YAML frontmatter block from the body.

    Returns ``(block, body)`` where ``block`` is the text between the fences
    (newlines normalized to LF) or ``None`` when the fence never opens or
    never closes — in which case ``body`` is the unmodified input. A single
    leading UTF-8 BOM is tolerated.
    """
    if text.startswith("﻿"):
        text = text.removeprefix("﻿")
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        return None, text
    lines = normalized[4:].split("\n")
    for index, line in enumerate(lines):
        if line.rstrip() == "---":
            block = "\n".join(lines[:index]) + "\n"
            body = "\n".join(lines[index + 1 :])
            return block, body
    return None, text
