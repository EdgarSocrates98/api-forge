"""Spring Boot extractor: *.java files -> CodeInventory via tree-sitter."""

from __future__ import annotations

import hashlib
from pathlib import Path

from apiforge.adapters.inventory import CodeInventory
from apiforge.adapters.spring.scan import scan_source
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_SKIPPED_DIRS = (
    ".git",
    ".apiforge",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "target",
)


def _discover(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*.java")):
        rel = path.relative_to(root)
        if any(part in _SKIPPED_DIRS for part in rel.parts):
            continue
        files.append(path)
    return files


def _diag(code: str, message: str, rel: str, digest: str, line: int | None) -> Diagnostic:
    return Diagnostic(
        code=code,
        status=FindingStatus.UNRESOLVED,
        message=message,
        source=SourceRef(path=rel, sha256=digest, line=line, extractor="spring"),
    )


def extract_spring(project_root: Path) -> CodeInventory:
    """Statically extract Spring routes; unresolvable shapes are named, not guessed."""
    root = Path(project_root)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    input_hashes: dict[str, str] = {}
    for path in _discover(root):
        rel = path.relative_to(root).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        input_hashes[rel] = digest
        scan = scan_source(path.read_text(encoding="utf-8"))
        if scan.has_error:
            diagnostics.append(
                _diag(
                    "AF-SPRING-PARSE",
                    f"{rel}: tree-sitter reported a parse error; extraction is partial",
                    rel,
                    digest,
                    None,
                )
            )
        for code, line in scan.unresolved:
            diagnostics.append(
                _diag(
                    code, f"{rel}: route shape could not be resolved statically", rel, digest, line
                )
            )
        for route in scan.routes:
            facts.append(
                Fact(
                    fact_id=stable_id(
                        "fact",
                        {
                            "kind": "code.route",
                            "method": route.method,
                            "path": route.path,
                            "file": rel,
                            "line": route.line,
                            "handler": route.handler,
                        },
                    ),
                    kind="code.route",
                    source=SourceRef(path=rel, sha256=digest, line=route.line, extractor="spring"),
                    measures={"method": route.method, "path": route.path},
                    attrs={
                        "handler": route.handler,
                        "via": route.via,
                        "reachable": True,
                    },
                )
            )
    return CodeInventory(
        framework="spring",
        root=str(root),
        facts=tuple(facts),
        diagnostics=tuple(diagnostics),
        input_hashes=input_hashes,
    )
