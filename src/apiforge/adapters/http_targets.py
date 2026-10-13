"""Static outbound HTTP target extraction: method + literal path near the call site.

Emits ``http.outbound`` facts only when a string literal carries a path. Targets
built from variables with no literal path segment are skipped, never guessed;
the caller reports them as low recall rather than inventing edges.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from apiforge.core.ids import stable_id
from apiforge.core.models import Fact, SourceRef

_SUFFIXES = {".py", ".java", ".kt", ".go", ".ts", ".js"}
_SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "build", "dist", "target"}
_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD")
_LITERAL = r"""f?[`"']([^`"'\n]*/[^`"'\n]*)[`"']"""
_PATTERNS: tuple[tuple[re.Pattern[str], int | None, int], ...] = (
    (
        re.compile(
            r"\b(?:requests|httpx|session|client|http_client|axios|this\.http|http)\s*\.\s*"
            r"(get|post|put|patch|delete|head)\s*\(\s*" + _LITERAL,
            re.IGNORECASE,
        ),
        1,
        2,
    ),
    (
        re.compile(
            r"\.(getForObject|getForEntity|postForObject|postForEntity|patchForObject)\s*\(\s*"
            + _LITERAL
        ),
        1,
        2,
    ),
    (re.compile(r"\bhttp\.(Get|Post|Head)\s*\(\s*" + _LITERAL), 1, 2),
    (
        re.compile(
            r"\bhttp\.NewRequest(?:WithContext)?\s*\((?:[^,]+,\s*)?"
            r"(?:\"(\w+)\"|http\.Method(\w+))\s*,\s*" + _LITERAL
        ),
        None,
        3,
    ),
    (re.compile(r"\bfetch\s*\(\s*" + _LITERAL), None, 1),
    (re.compile(r"\.uri\s*\(\s*" + _LITERAL), None, 1),
)
_INLINE_METHOD = re.compile(
    r"(?:method\s*[:=]\s*[\"'](\w+)[\"']|\.(get|post|put|patch|delete)\s*\(\s*\))", re.IGNORECASE
)
_SCHEME_HOST = re.compile(r"^[a-z][a-z0-9+.-]*://([^/]+)", re.IGNORECASE)
_TEMPLATE_PREFIX = re.compile(r"^(?:\$?\{[^}]*\}|%s|%v)+")


def _split(literal: str) -> tuple[str, str] | None:
    base = ""
    rest = literal.strip()
    host = _SCHEME_HOST.match(rest)
    if host:
        base = host.group(1).split(":")[0]
        rest = rest[host.end() :]
    else:
        prefix = _TEMPLATE_PREFIX.match(rest)
        if prefix:
            base = re.sub(r"[${}%]", "", prefix.group(0))
            rest = rest[prefix.end() :]
    rest = rest.split("?")[0].split("#")[0]
    if not rest.startswith("/"):
        return None
    return rest, base


def _method(match: re.Match[str], group: int | None, window: str) -> str:
    if group is not None:
        value = match.group(group)
        if not value:
            return "unknown"
        verb = next((item for item in _METHODS if value.upper().startswith(item)), None)
        return verb or "unknown"
    groups = [value for value in match.groups()[:-1] if value]
    if groups:
        return groups[0].upper()
    inline = _INLINE_METHOD.search(window)
    if inline:
        value = inline.group(1) or inline.group(2)
        if value and value.upper() in _METHODS:
            return value.upper()
    return "unknown"


def _files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and not path.is_symlink()
        and path.suffix.lower() in _SUFFIXES
        and not any(part in _SKIP_DIRS for part in path.relative_to(root).parts)
    )


def extract_http_targets(project_root: Path) -> tuple[Fact, ...]:
    root = Path(project_root)
    facts: dict[str, Fact] = {}
    for path in _files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = path.relative_to(root).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines = text.splitlines()
        for index, line in enumerate(lines):
            for pattern, method_group, literal_group in _PATTERNS:
                for match in pattern.finditer(line):
                    split = _split(match.group(literal_group))
                    if split is None:
                        continue
                    target, base = split
                    window = "\n".join(lines[max(0, index - 2) : index + 3])
                    method = _method(match, method_group, window)
                    measures = {"method": method, "path": target, "base_hint": base}
                    fact_id = stable_id(
                        "fact", {"k": "http.outbound", "p": rel, "l": index + 1, **measures}
                    )
                    facts[fact_id] = Fact(
                        fact_id=fact_id,
                        kind="http.outbound",
                        measures={**measures, "heuristic": "literal-near-call"},
                        attrs={},
                        source=SourceRef(
                            path=rel, sha256=digest, line=index + 1, extractor="http_targets"
                        ),
                    )
    return tuple(facts[key] for key in sorted(facts))


__all__ = ["extract_http_targets"]
