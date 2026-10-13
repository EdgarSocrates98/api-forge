"""Static FastAPI inventory: AST only, never imports or executes project code.

Pass one (`scan_file`) records `FastAPI`/`APIRouter` bindings, imports, route
decorators and `include_router` calls per file. The resolver then binds each
declaration to a `(module, name)` key, walks the include graph from every
`FastAPI` app accumulating prefixes, and emits one `code.route` fact per
resolved route occurrence — duplicates and unreachable routers included, each
with its own provenance. Anything not statically resolvable becomes a named
unresolved diagnostic instead of a guessed route.
"""

from __future__ import annotations

import os
from pathlib import Path

from apiforge.adapters.fastapi.models import FastApiInventory
from apiforge.adapters.fastapi.scan import (
    Binding,
    FileScan,
    RouteDecl,
    scan_file,
)
from apiforge.adapters.inventory import static_execution
from apiforge.core.ids import stable_id
from apiforge.core.io import sha256_file
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_PRUNED_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".apiforge",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        "node_modules",
        "dist",
        "build",
    }
)

Key = tuple[str, str]  # (module, binding name)


def _discover(root: Path) -> tuple[list[Path], list[Path]]:
    files: list[Path] = []
    escaped: list[Path] = []
    base = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in _PRUNED_DIRS)
        for name in sorted(filenames):
            if not name.endswith(".py"):
                continue
            path = Path(dirpath) / name
            try:
                path.resolve().relative_to(base)
            except ValueError:
                escaped.append(path)
                continue
            files.append(path)
    return files, escaped


def _resolve_ref(
    base: str,
    attrs: tuple[str, ...],
    scan: FileScan,
    scans: dict[str, FileScan],
    bindings: dict[Key, Binding],
) -> Key | None:
    if not attrs:
        if base in scan.bindings:
            return (scan.module, base)
        imported = scan.imports.get(base)
        if imported and imported[1] is not None:
            return (imported[0], imported[1])
        return None
    imported = scan.imports.get(base)
    if imported is None:
        return None
    module, attr = imported
    chain = [attr, *attrs] if attr else list(attrs)
    for cut in range(len(chain)):
        candidate = ".".join([module, *chain[:cut]]) if cut else module
        if (candidate, chain[cut]) in bindings:
            return (candidate, chain[cut])
    return None


def _resolve_local(name: str, scan: FileScan, bindings: dict[Key, Binding]) -> Key | None:
    if name in scan.bindings:
        return (scan.module, name)
    imported = scan.imports.get(name)
    if imported and imported[1] and (imported[0], imported[1]) in bindings:
        return (imported[0], imported[1] or name)
    return None


def _diag(code: str, message: str, rel: str, digest: str, line: int | None) -> Diagnostic:
    return Diagnostic(
        code=code,
        status=FindingStatus.UNRESOLVED,
        message=message,
        source=SourceRef(path=rel, sha256=digest, line=line, extractor="fastapi"),
    )


def extract_fastapi(project_root: Path) -> FastApiInventory:
    """Extract route facts and diagnostics from a FastAPI project tree."""
    root = Path(project_root)
    files, escaped = _discover(root)
    scans: dict[str, FileScan] = {}
    input_hashes: dict[str, str] = {}
    diagnostics: list[Diagnostic] = []
    for file in files:
        rel = file.relative_to(root).as_posix()
        digest = sha256_file(file)
        input_hashes[rel] = digest
        scanned = scan_file(file, Path(rel), digest)
        scans[scanned.module] = scanned
        if scanned.syntax_error is not None:
            diagnostics.append(
                _diag(
                    "AF-FASTAPI-PARSE",
                    f"{rel}: {scanned.syntax_error}",
                    rel,
                    digest,
                    None,
                )
            )
    for path in escaped:
        diagnostics.append(
            _diag(
                "AF-FASTAPI-SYMLINK-ESCAPE",
                f"{path.name}: symlink escapes the project root",
                path.name,
                "0" * 64,
                None,
            )
        )

    bindings: dict[Key, Binding] = {}
    routes_by: dict[Key, list[tuple[RouteDecl, FileScan]]] = {}
    edges: dict[Key, list[tuple[Key, str | None, bool, FileScan, int]]] = {}
    apps: list[Key] = []
    for scan in scans.values():
        for binding in scan.bindings.values():
            key = (binding.module, binding.name)
            bindings[key] = binding
            if binding.kind == "app":
                apps.append(key)
            if binding.dynamic_prefix:
                diagnostics.append(
                    _diag(
                        "AF-FASTAPI-DYNAMIC-ROUTE",
                        f"{binding.name}: router prefix is not a literal",
                        binding.file,
                        scan.sha256,
                        binding.line,
                    )
                )
    for scan in scans.values():
        for decl in scan.routes:
            route_key = _resolve_local(decl.target, scan, bindings)
            if route_key is None:
                diagnostics.append(
                    _diag(
                        "AF-FASTAPI-DYNAMIC-ROUTE",
                        f"{decl.function}: decorated object {decl.target!r} is unresolved",
                        scan.rel,
                        scan.sha256,
                        decl.line,
                    )
                )
                continue
            if decl.dynamic:
                diagnostics.append(
                    _diag(
                        "AF-FASTAPI-DYNAMIC-ROUTE",
                        f"{decl.function}: route path or methods are not literals",
                        scan.rel,
                        scan.sha256,
                        decl.line,
                    )
                )
                if decl.path is None or decl.method is None:
                    continue
            routes_by.setdefault(route_key, []).append((decl, scan))
        for include in scan.includes:
            parent = _resolve_local(include.parent, scan, bindings)
            child = _resolve_ref(include.ref[0], include.ref[1], scan, scans, bindings)
            if parent is None or child is None:
                diagnostics.append(
                    _diag(
                        "AF-FASTAPI-DYNAMIC-ROUTE",
                        f"include_router at {scan.rel}:{include.line} cannot be resolved",
                        scan.rel,
                        scan.sha256,
                        include.line,
                    )
                )
                continue
            edges.setdefault(parent, []).append(
                (child, include.prefix, include.dynamic_prefix, scan, include.line)
            )
            if include.dynamic_prefix:
                diagnostics.append(
                    _diag(
                        "AF-FASTAPI-DYNAMIC-ROUTE",
                        f"include_router at {scan.rel}:{include.line} has a dynamic prefix",
                        scan.rel,
                        scan.sha256,
                        include.line,
                    )
                )

    facts: list[Fact] = []
    visited: set[Key] = set()

    def emit(
        key: Key, decl: RouteDecl, scan: FileScan, prefix: str, reachable: bool, via: str | None
    ) -> None:
        path = prefix + (decl.path or "")
        facts.append(
            Fact(
                fact_id=stable_id(
                    "fact",
                    {
                        "kind": "code.route",
                        "method": decl.method,
                        "path": path,
                        "file": scan.rel,
                        "line": decl.line,
                        "function": decl.function,
                        "via": via,
                    },
                ),
                kind="code.route",
                source=SourceRef(
                    path=scan.rel, sha256=scan.sha256, line=decl.line, extractor="fastapi"
                ),
                attrs={
                    "function": decl.function,
                    "router": decl.target,
                    "reachable": reachable,
                    "via": via,
                },
                measures={"method": decl.method, "path": path},
            )
        )

    def visit(key: Key, acc_prefix: str, on_path: frozenset[Key], via: str | None) -> None:
        if key not in bindings:
            rel = (via or "<root>").split(":", 1)[0]
            source_scan = next((item for item in scans.values() if item.rel == rel), None)
            diagnostics.append(
                _diag(
                    "AF-FASTAPI-UNRESOLVED-BINDING",
                    f"binding {key[0]!r}.{key[1]!r} is not present in the static index",
                    rel,
                    source_scan.sha256 if source_scan is not None else "0" * 64,
                    None,
                )
            )
            return
        visited.add(key)
        binding = bindings[key]
        prefix = acc_prefix + (binding.prefix or "")
        for decl, scan in routes_by.get(key, []):
            emit(key, decl, scan, prefix, True, via)
        for child, edge_prefix, _dynamic, scan, line in edges.get(key, []):
            if child not in bindings:
                diagnostics.append(
                    _diag(
                        "AF-FASTAPI-UNRESOLVED-BINDING",
                        f"include_router target {child[0]!r}.{child[1]!r} is not present in the static index",
                        scan.rel,
                        scan.sha256,
                        line,
                    )
                )
                continue
            if child in on_path:
                diagnostics.append(
                    _diag(
                        "AF-FASTAPI-INCLUDE-CYCLE",
                        f"include_router cycle at {scan.rel}:{line}",
                        scan.rel,
                        scan.sha256,
                        line,
                    )
                )
                continue
            visit(
                child,
                prefix + (edge_prefix or ""),
                on_path | {child},
                f"{scan.rel}:{line}",
            )

    for app in sorted(apps):
        visit(app, "", frozenset({app}), None)
    for key in sorted(bindings):
        if key in visited or bindings[key].kind == "app":
            continue
        binding = bindings[key]
        for decl, scan in routes_by.get(key, []):
            emit(key, decl, scan, binding.prefix or "", False, None)
        visited.add(key)

    facts.sort(
        key=lambda fact: (
            str(fact.measures["path"]),
            str(fact.measures["method"]),
            fact.source.path,
            fact.source.line or 0,
        )
    )
    diagnostics.sort(
        key=lambda d: (
            d.code,
            d.source.path if d.source else "",
            d.source.line or 0 if d.source else 0,
            d.message,
        )
    )
    return FastApiInventory(
        root=root.as_posix(),
        facts=tuple(facts),
        diagnostics=tuple(diagnostics),
        input_hashes=input_hashes,
        execution=static_execution(
            "fastapi",
            input_hashes,
            tuple(diagnostics),
            limitations=(
                "does not import or execute application code",
                "dynamic routes remain unresolved",
            ),
        ),
    )
