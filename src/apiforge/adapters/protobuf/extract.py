"""Protobuf extractor: *.proto -> proto.* facts, offline — no protoc.

A deterministic mini-parser: comments are stripped, braces tracked, and the
``message``/``service``/``enum`` vocabulary extracted. ``rpc`` lines carry
their streaming flags as data. Unbalanced braces are ``AF-PROTO-PARSE``
diagnostics; anything outside the known vocabulary is ignored, never
guessed at.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from apiforge.adapters.inventory import CodeInventory
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_EXTRACTOR = "proto-file"

_BLOCK = re.compile(r"^\s*(message|service|enum)\s+(\w+)\s*\{")
_RPC = re.compile(
    r"^\s*rpc\s+(\w+)\s*\(\s*(stream\s+)?([\w.]+)\s*\)\s*"
    r"returns\s*\(\s*(stream\s+)?([\w.]+)\s*\)"
)
_PACKAGE = re.compile(r"^\s*package\s+([\w.]+)\s*;")
_IMPORT = re.compile(r'^\s*import\s+(?:public\s+|weak\s+)?"([^"]+)"\s*;')
_FIELD = re.compile(r"^\s*(?:repeated\s+|optional\s+)?[\w.]+\s+\w+\s*=\s*\d+")
_OPTION = re.compile(r"^\s*option\s+")


def _fact(
    kind: str, rel: str, digest: str, measures: dict[str, Any], attrs: dict[str, Any]
) -> Fact:
    return Fact(
        fact_id=stable_id("fact", {"kind": kind, "file": rel, **measures}),
        kind=kind,
        source=SourceRef(path=rel, sha256=digest, extractor=_EXTRACTOR),
        measures=measures,
        attrs=attrs,
    )


def _diag(code: str, rel: str, digest: str, message: str, line: int | None = None) -> Diagnostic:
    return Diagnostic(
        code=code,
        status=FindingStatus.UNRESOLVED,
        message=message,
        source=SourceRef(path=rel, sha256=digest, line=line, extractor=_EXTRACTOR),
    )


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", "", text)


def _parse_file(path: Path, rel: str) -> tuple[list[Fact], list[Diagnostic], str]:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    try:
        text = _strip_comments(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        return [], [_diag("AF-PROTO-PARSE", rel, digest, str(exc))], digest

    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    package = ""
    imports: list[str] = []
    stack: list[tuple[str, str]] = []  # (kind, name)
    rpcs: list[dict[str, Any]] = []
    field_counts: dict[str, int] = {}
    braces = 0

    for lineno, line in enumerate(text.splitlines(), 1):
        opens = line.count("{")
        closes = line.count("}")
        if m := _PACKAGE.match(line):
            package = m.group(1)
        elif m := _IMPORT.match(line):
            imports.append(m.group(1))
        elif m := _BLOCK.match(line):
            kind, name = m.groups()
            stack.append((kind, name))
            if kind == "message":
                field_counts[name] = 0
        elif m := _RPC.match(line):
            if stack and stack[-1][0] == "service":
                name, cstream, req, sstream, resp = m.groups()
                rpcs.append(
                    {
                        "service": stack[-1][1],
                        "name": name,
                        "request": req,
                        "response": resp,
                        "client_streaming": bool(cstream),
                        "server_streaming": bool(sstream),
                    }
                )
        elif _FIELD.match(line) and stack and stack[-1][0] == "message":
            field_counts[stack[-1][1]] += 1
        elif _OPTION.match(line):
            pass
        braces += opens - closes
        for _ in range(closes):
            if stack:
                stack.pop()
        if braces < 0:
            diagnostics.append(_diag("AF-PROTO-PARSE", rel, digest, "unbalanced braces", lineno))
            return facts, diagnostics, digest
    if braces != 0 or stack:
        diagnostics.append(_diag("AF-PROTO-PARSE", rel, digest, "unclosed block at end of file"))

    facts.append(
        _fact(
            "proto.file",
            rel,
            digest,
            {"file": rel},
            {
                "package": package,
                "imports": tuple(sorted(imports)),
                "services": tuple(sorted({r["service"] for r in rpcs})),
                "messages": tuple(sorted(field_counts)),
            },
        )
    )
    for service in sorted({r["service"] for r in rpcs}):
        facts.append(
            _fact(
                "proto.service",
                rel,
                digest,
                {"service": service},
                {"rpcs": tuple(r["name"] for r in rpcs if r["service"] == service)},
            )
        )
    for rpc in rpcs:
        facts.append(
            _fact(
                "proto.rpc",
                rel,
                digest,
                {"service": rpc["service"], "rpc": rpc["name"]},
                {
                    "request": rpc["request"],
                    "response": rpc["response"],
                    "client_streaming": rpc["client_streaming"],
                    "server_streaming": rpc["server_streaming"],
                },
            )
        )
    for name, count in sorted(field_counts.items()):
        facts.append(
            _fact(
                "proto.message",
                rel,
                digest,
                {"message": name},
                {"fields": count},
            )
        )
    return facts, diagnostics, digest


def extract_protobuf(root: Path) -> CodeInventory:
    """All *.proto under root -> proto.* facts."""
    root = Path(root)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    files = sorted(root.rglob("*.proto"))
    if not files:
        diagnostics.append(
            Diagnostic(
                code="AF-PROTO-EMPTY",
                status=FindingStatus.UNRESOLVED,
                message=f"no *.proto under {root}",
            )
        )
    for path in files:
        rel = path.relative_to(root).as_posix()
        file_facts, file_diags, digest = _parse_file(path, rel)
        hashes[rel] = digest
        facts.extend(file_facts)
        diagnostics.extend(file_diags)
    return CodeInventory(
        framework="protobuf",
        root=str(root),
        diagnostics=tuple(diagnostics),
        facts=tuple(facts),
        input_hashes=hashes,
    )
