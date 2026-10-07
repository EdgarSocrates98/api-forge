"""Canonical-schema dedup: code models are reported as parity or delta, not repeated."""

from __future__ import annotations

import ast
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_MODEL_SUFFIXES = {".py", ".java", ".kt", ".go"}
_JAVA_FIELD = re.compile(
    r"^\s*(?:private|protected|public)?\s*(?:final\s+)?[\w<>\[\],. ?]+\s+(\w+)\s*(?:=[^;]*)?;"
)
_JAVA_RECORD = re.compile(r"\brecord\s+(\w+)\s*\(([^)]*)\)")
_GO_FIELD = re.compile(r"^\s*([A-Z]\w*)\s+[\w.\[\]*]+")
_STRING = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')


@dataclass(frozen=True)
class CodeModel:
    name: str
    path: Path
    span: tuple[int, int]
    fields: tuple[str, ...]
    text: str


def schema_fields(schema: Mapping[str, Any]) -> tuple[str, ...]:
    properties = schema.get("properties")
    if not isinstance(properties, Mapping):
        return ()
    return tuple(sorted(str(name) for name in properties))


def compare(
    schema: tuple[str, ...], model: tuple[str, ...]
) -> tuple[bool, dict[str, tuple[str, ...]]]:
    wanted = {_norm(item) for item in schema}
    found = {_norm(item) for item in model}
    missing = tuple(sorted(item for item in schema if _norm(item) not in found))
    extra = tuple(sorted(item for item in model if _norm(item) not in wanted))
    delta = {key: value for key, value in (("missing", missing), ("extra", extra)) if value}
    return not delta, delta


def find_models(project: Path, names: Iterable[str]) -> dict[str, CodeModel]:
    wanted = set(names)
    found: dict[str, CodeModel] = {}
    if not wanted or not project.is_dir():
        return found
    for path in sorted(project.rglob("*")):
        if path.suffix not in _MODEL_SUFFIXES or not path.is_file() or ".apiforge" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not any(name in text for name in wanted - set(found)):
            continue
        for model in _models_in(path, text):
            if model.name in wanted and model.name not in found:
                found[model.name] = model
    return found


def _models_in(path: Path, text: str) -> list[CodeModel]:
    if path.suffix == ".py":
        return _python_models(path, text)
    if path.suffix == ".go":
        return _go_models(path, text)
    return _java_models(path, text)


def _python_models(path: Path, text: str) -> list[CodeModel]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    lines = text.splitlines()
    models: list[CodeModel] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        fields = tuple(
            item.target.id
            for item in node.body
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)
        )
        end = node.end_lineno or node.lineno
        models.append(
            CodeModel(
                node.name, path, (node.lineno, end), fields, "\n".join(lines[node.lineno - 1 : end])
            )
        )
    return models


def _java_models(path: Path, text: str) -> list[CodeModel]:
    lines = text.splitlines()
    models: list[CodeModel] = []
    for match in _JAVA_RECORD.finditer(text):
        line_no = text.count("\n", 0, match.start()) + 1
        fields = tuple(
            part.strip().split()[-1] for part in match.group(2).split(",") if part.strip()
        )
        models.append(
            CodeModel(match.group(1), path, (line_no, line_no), fields, lines[line_no - 1])
        )
    for index, line in enumerate(lines):
        declared = re.search(r"\bclass\s+(\w+)", line)
        if declared is None:
            continue
        start, end = index + 1, brace_block_end(lines, index)
        body = lines[index + 1 : end - 1]
        fields = tuple(
            found.group(1)
            for item in body
            if "(" not in item and (found := _JAVA_FIELD.match(item)) is not None
        )
        models.append(
            CodeModel(declared.group(1), path, (start, end), fields, "\n".join(lines[index:end]))
        )
    return models


def _go_models(path: Path, text: str) -> list[CodeModel]:
    lines = text.splitlines()
    models: list[CodeModel] = []
    for index, line in enumerate(lines):
        match = re.match(r"^type\s+(\w+)\s+struct\s*\{", line)
        if match is None:
            continue
        end = brace_block_end(lines, index)
        fields = tuple(
            found.group(1)
            for item in lines[index + 1 : end - 1]
            if (found := _GO_FIELD.match(item))
        )
        models.append(
            CodeModel(match.group(1), path, (index + 1, end), fields, "\n".join(lines[index:end]))
        )
    return models


def code_only(line: str) -> str:
    return _STRING.sub('""', line.split("//", 1)[0])


def brace_block_end(lines: list[str], start: int, limit: int = 120) -> int:
    depth = 0
    opened = False
    for index in range(start, min(len(lines), start + limit)):
        code = code_only(lines[index])
        depth += code.count("{") - code.count("}")
        opened = opened or "{" in code
        if opened and depth <= 0:
            return index + 1
    return min(len(lines), start + limit)


def _norm(name: str) -> str:
    return name.replace("_", "").lower()


__all__ = [
    "CodeModel",
    "brace_block_end",
    "code_only",
    "compare",
    "find_models",
    "schema_fields",
]
