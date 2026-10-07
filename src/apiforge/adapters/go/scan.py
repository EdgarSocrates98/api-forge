"""Tree-sitter pass over a single Go source: call expressions -> route records."""

from __future__ import annotations

from dataclasses import dataclass, field

import tree_sitter_go
from tree_sitter import Language, Node, Parser

_PARSER = Parser(Language(tree_sitter_go.language()))

_VERB_METHODS = {
    "Get",
    "Post",
    "Put",
    "Delete",
    "Patch",
    "Head",
    "Options",
    "Trace",
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "PATCH",
    "HEAD",
    "OPTIONS",
    "TRACE",
}
_MUX_METHODS = {"Handle", "HandleFunc"}
_SCOPE_METHODS = {"Route", "Group"}
_UNRESOLVABLE = {"Mount", "Use", "Method", "With"}
_HTTP_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE"}


@dataclass(frozen=True)
class RouteRecord:
    method: str
    path: str
    handler: str
    via: str
    line: int


@dataclass
class FileScan:
    routes: list[RouteRecord] = field(default_factory=list)
    unresolved: list[tuple[str, int | None]] = field(default_factory=list)
    has_error: bool = False


def _text(node: Node | None) -> str:
    if node is None or node.text is None:
        return ""
    return node.text.decode("utf-8")


def _call_name(node: Node) -> str:
    func = node.child_by_field_name("function")
    if func is None:
        return ""
    if func.type == "selector_expression":
        return _text(func.child_by_field_name("field"))
    return _text(func)


def _args(node: Node) -> list[Node]:
    args = node.child_by_field_name("arguments")
    if args is None:
        return []
    return [c for c in args.children if c.type not in ("(", ")", ",")]


def _literal(node: Node | None) -> str | None:
    if node is None or node.type != "interpreted_string_literal":
        return None
    content = next(
        (c for c in node.children if c.type == "interpreted_string_literal_content"),
        None,
    )
    return _text(content)


def _join(prefix: str, sub: str) -> str:
    if not sub.startswith("/"):
        sub = "/" + sub
    return (prefix.rstrip("/") if prefix else "") + sub


def _split_method_path(literal: str) -> tuple[str, str]:
    parts = literal.strip().split(None, 1)
    if len(parts) == 2 and parts[0].upper() in _HTTP_METHODS:
        return parts[0].lower(), parts[1]
    return "any", literal.strip()


def _visit(node: Node, prefix: str, scan: FileScan, consumed: set[int]) -> None:
    if node.id in consumed:
        return
    if node.type != "call_expression":
        for child in node.children:
            _visit(child, prefix, scan, consumed)
        return
    name = _call_name(node)
    args = _args(node)
    line = node.start_point[0] + 1
    if name in _VERB_METHODS:
        literal = _literal(args[0]) if args else None
        if literal is None:
            scan.unresolved.append(("AF-GO-UNRESOLVED-ROUTE", line))
        else:
            scan.routes.append(
                RouteRecord(
                    method=name.lower(),
                    path=_join(prefix, literal),
                    handler=_text(args[1]) if len(args) > 1 else "",
                    via="call",
                    line=line,
                )
            )
    elif name in _MUX_METHODS:
        literal = _literal(args[0]) if args else None
        if literal is None:
            scan.unresolved.append(("AF-GO-UNRESOLVED-ROUTE", line))
        else:
            method, path = _split_method_path(literal)
            scan.routes.append(
                RouteRecord(
                    method=method,
                    path=_join(prefix, path),
                    handler=_text(args[1]) if len(args) > 1 else "",
                    via="mux",
                    line=line,
                )
            )
    elif name in _SCOPE_METHODS:
        literal = _literal(args[0]) if args else None
        body = args[1] if len(args) > 1 else None
        if literal is None or body is None or body.type != "func_literal":
            scan.unresolved.append(("AF-GO-UNRESOLVED-ROUTE", line))
        else:
            args_node = node.child_by_field_name("arguments")
            if args_node is not None:
                consumed.add(args_node.id)
            _visit(body, _join(prefix, literal), scan, consumed)
    elif name in _UNRESOLVABLE:
        scan.unresolved.append(("AF-GO-UNRESOLVED-ROUTE", line))
    for child in node.children:
        _visit(child, prefix, scan, consumed)


def scan_source(source: str) -> FileScan:
    """Parse one Go file; records, never judgments."""
    scan = FileScan()
    tree = _PARSER.parse(source.encode("utf-8"))
    scan.has_error = tree.root_node.has_error
    _visit(tree.root_node, "", scan, set())
    return scan
