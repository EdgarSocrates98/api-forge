"""Per-file AST pass for the FastAPI extractor.

Collects raw declarations only — bindings, imports, route decorators and
`include_router` calls — without resolving cross-file references and without
ever importing the scanned module.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

HTTP_METHODS = frozenset({"get", "put", "post", "delete", "options", "head", "patch", "trace"})
_ROUTE_CALLS = HTTP_METHODS | {"route", "api_route"}


@dataclass(frozen=True)
class Binding:
    """A `name = FastAPI(...)` or `name = APIRouter(...)` assignment."""

    kind: str  # "app" | "router"
    name: str
    module: str
    file: str
    line: int
    prefix: str | None
    dynamic_prefix: bool


@dataclass(frozen=True)
class RouteDecl:
    """One decorated handler; `path`/`method` are None when dynamic."""

    target: str
    method: str | None
    path: str | None
    dynamic: bool
    function: str
    line: int


@dataclass(frozen=True)
class IncludeDecl:
    """One `obj.include_router(ref, prefix=...)` call."""

    parent: str
    ref: tuple[str, tuple[str, ...]]  # base name + attribute chain
    prefix: str | None
    dynamic_prefix: bool
    line: int


@dataclass(frozen=True)
class FileScan:
    module: str
    rel: str
    sha256: str
    bindings: dict[str, Binding] = field(default_factory=dict)
    imports: dict[str, tuple[str, str | None]] = field(default_factory=dict)
    routes: tuple[RouteDecl, ...] = ()
    includes: tuple[IncludeDecl, ...] = ()
    syntax_error: str | None = None


def module_name(rel: Path) -> str:
    parts = list(rel.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts) or rel.stem


def _literal(node: ast.expr) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _call_name(func: ast.expr) -> str:
    while isinstance(func, ast.Attribute):
        func = func.value
    return func.id if isinstance(func, ast.Name) else ""


def _call_attr(func: ast.expr) -> str:
    return func.attr if isinstance(func, ast.Attribute) else ""


def _kwarg(call: ast.Call, name: str) -> ast.expr | None:
    for keyword in call.keywords:
        if keyword.arg == name:
            return keyword.value
    return None


def _ref_parts(expr: ast.expr) -> tuple[str, tuple[str, ...]] | None:
    attrs: list[str] = []
    while isinstance(expr, ast.Attribute):
        attrs.append(expr.attr)
        expr = expr.value
    if isinstance(expr, ast.Name):
        return expr.id, tuple(reversed(attrs))
    return None


def _methods(call: ast.Call, attr: str) -> tuple[str | None, ...]:
    if attr in HTTP_METHODS:
        return (attr,)
    arg = _kwarg(call, "methods")
    if arg is None:
        return ("get",)
    if isinstance(arg, (ast.List, ast.Tuple)):
        out: list[str | None] = []
        for item in arg.elts:
            literal = _literal(item)
            out.append(literal.lower() if literal is not None else None)
        return tuple(out)
    return (None,)


def _scan_node(node: ast.AST, scan: dict[str, object]) -> None:
    bindings: dict[str, Binding] = scan["bindings"]  # type: ignore[assignment]
    imports: dict[str, tuple[str, str | None]] = scan["imports"]  # type: ignore[assignment]
    routes: list[RouteDecl] = scan["routes"]  # type: ignore[assignment]
    includes: list[IncludeDecl] = scan["includes"]  # type: ignore[assignment]
    module = cast(str, scan["module"])
    rel = cast(str, scan["rel"])

    if isinstance(node, ast.ImportFrom):
        base = "." * node.level + (node.module or "")
        resolved = _resolve_from(module, base)
        for alias in node.names:
            local = alias.asname or alias.name
            if alias.name == "*":
                continue
            imports[local] = (resolved, alias.name)
        return
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.asname:
                imports[alias.asname] = (alias.name, None)
            else:
                imports[alias.name.split(".")[0]] = (alias.name.split(".")[0], None)
        return
    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
        call = node.value
        kind = ""
        if _call_name(call.func) == "FastAPI" or _call_attr(call.func) == "FastAPI":
            kind = "app"
        elif _call_name(call.func) == "APIRouter" or _call_attr(call.func) == "APIRouter":
            kind = "router"
        if kind:
            arg = _kwarg(call, "prefix")
            prefix = _literal(arg) if arg is not None else ("" if kind == "app" else None)
            dynamic = arg is not None and prefix is None
            for target in node.targets:
                if isinstance(target, ast.Name):
                    bindings[target.id] = Binding(
                        kind=kind,
                        name=target.id,
                        module=module,
                        file=rel,
                        line=node.lineno,
                        prefix=prefix,
                        dynamic_prefix=dynamic,
                    )
        return
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            attr = _call_attr(decorator.func)
            if attr not in _ROUTE_CALLS:
                continue
            owner = _call_name(decorator.func)
            if not owner:
                continue
            path = _literal(decorator.args[0]) if decorator.args else None
            dynamic = path is None and bool(decorator.args)
            for method in _methods(decorator, attr):
                routes.append(
                    RouteDecl(
                        target=owner,
                        method=method,
                        path=path,
                        dynamic=dynamic or method is None,
                        function=node.name,
                        line=decorator.lineno,
                    )
                )
        return
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        call = node.value
        if _call_attr(call.func) == "include_router" and call.args:
            parent = _call_name(call.func.value)  # type: ignore[attr-defined]
            ref = _ref_parts(call.args[0])
            arg = _kwarg(call, "prefix")
            prefix = _literal(arg) if arg is not None else None
            if parent and ref is not None:
                includes.append(
                    IncludeDecl(
                        parent=parent,
                        ref=ref,
                        prefix=prefix,
                        dynamic_prefix=arg is not None and prefix is None,
                        line=node.lineno,
                    )
                )
            elif parent:
                includes.append(
                    IncludeDecl(
                        parent=parent,
                        ref=("", ()),
                        prefix=prefix,
                        dynamic_prefix=True,
                        line=node.lineno,
                    )
                )


def _resolve_from(module: str, base: str) -> str:
    """Resolve a `from ... import` module (possibly relative) against `module`."""
    if not base.startswith("."):
        return base
    level = len(base) - len(base.lstrip("."))
    rest = base.lstrip(".")
    parts = module.split(".")[:-1]  # drop the file's own module name
    if level > 1:
        parts = parts[: -(level - 1)] if level - 1 <= len(parts) else []
    return ".".join([*parts, rest]) if rest else ".".join(parts)


def scan_file(path: Path, rel: Path, digest: str) -> FileScan:
    module = module_name(rel)
    scan: dict[str, object] = {
        "module": module,
        "rel": rel.as_posix(),
        "bindings": {},
        "imports": {},
        "routes": [],
        "includes": [],
    }
    try:
        tree = ast.parse(path.read_bytes())
    except SyntaxError as exc:
        return FileScan(
            module=module,
            rel=rel.as_posix(),
            sha256=digest,
            syntax_error=f"line {exc.lineno}: {exc.msg}",
        )
    for node in ast.walk(tree):
        _scan_node(node, scan)
    return FileScan(
        module=module,
        rel=rel.as_posix(),
        sha256=digest,
        bindings=scan["bindings"],  # type: ignore[arg-type]
        imports=scan["imports"],  # type: ignore[arg-type]
        routes=tuple(scan["routes"]),  # type: ignore[arg-type]
        includes=tuple(scan["includes"]),  # type: ignore[arg-type]
    )
