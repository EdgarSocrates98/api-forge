"""Tree-sitter pass over a single Java source: annotations -> route records."""

from __future__ import annotations

from dataclasses import dataclass, field

import tree_sitter_java
from tree_sitter import Language, Node, Parser

_PARSER = Parser(Language(tree_sitter_java.language()))

_CONTROLLER_ANNOTATIONS = {"RestController", "Controller"}
_CLASS_PATH_ANNOTATIONS = {"RequestMapping", "Path"}
_METHOD_MAPPINGS = {
    "GetMapping": "get",
    "PostMapping": "post",
    "PutMapping": "put",
    "DeleteMapping": "delete",
    "PatchMapping": "patch",
}
_JAXRS_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
_PREDICATE_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}


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


def _modifiers(node: Node) -> Node | None:
    return next((c for c in node.children if c.type == "modifiers"), None)


def _annotations(modifiers: Node | None) -> list[Node]:
    if modifiers is None:
        return []
    return [c for c in modifiers.children if c.type in ("marker_annotation", "annotation")]


def _ann_name(node: Node) -> str:
    name = node.child_by_field_name("name")
    return _text(name).rsplit(".", 1)[-1]


def _ann_literal(node: Node) -> tuple[str | None, bool]:
    """Return (literal_value, has_nonliteral_args) for an annotation node."""
    if node.type == "marker_annotation":
        return None, False
    args = node.child_by_field_name("arguments")
    if args is None:
        return None, False
    literals: list[str] = []
    nonliteral = False
    for child in args.children:
        if child.type in ("(", ")", ","):
            continue
        if child.type == "string_literal":
            frag = next((c for c in child.children if c.type == "string_fragment"), None)
            literals.append(_text(frag))
        elif child.type == "element_value_pair":
            value = child.child_by_field_name("value")
            if value is not None and value.type == "string_literal":
                frag = next((c for c in value.children if c.type == "string_fragment"), None)
                literals.append(_text(frag))
            elif value is not None and value.type == "element_value_array_initializer":
                for v in value.children:
                    if v.type == "string_literal":
                        frag = next(
                            (c for c in v.children if c.type == "string_fragment"),
                            None,
                        )
                        literals.append(_text(frag))
            else:
                nonliteral = True
        else:
            nonliteral = True
    if literals:
        return literals[0], nonliteral
    return None, True


def _request_method(node: Node) -> str | None:
    """Extract method=RequestMethod.X (or method="X") from @RequestMapping."""
    args = node.child_by_field_name("arguments")
    if args is None:
        return None
    for child in args.children:
        if child.type != "element_value_pair":
            continue
        key = child.child_by_field_name("key")
        if _text(key) != "method":
            continue
        value = _text(child.child_by_field_name("value"))
        return value.rsplit(".", 1)[-1].strip('"').lower() or None
    return None


def _join(prefix: str, sub: str | None) -> str:
    if not sub:
        return prefix or "/"
    if not sub.startswith("/"):
        sub = "/" + sub
    return (prefix.rstrip("/") if prefix else "") + sub


def _scan_class(node: Node, scan: FileScan) -> None:
    modifiers = _modifiers(node)
    anns = _annotations(modifiers)
    names = {_ann_name(a) for a in anns}
    is_controller = bool(names & _CONTROLLER_ANNOTATIONS)
    class_path = ""
    is_jaxrs = False
    for a in anns:
        if _ann_name(a) not in _CLASS_PATH_ANNOTATIONS:
            continue
        literal, nonliteral = _ann_literal(a)
        if _ann_name(a) == "Path":
            is_jaxrs = True
        if literal is not None:
            class_path = literal
        elif nonliteral:
            scan.unresolved.append(("AF-SPRING-UNRESOLVED-ROUTE", a.start_point[0] + 1))
    if not (is_controller or is_jaxrs):
        return
    body = node.child_by_field_name("body")
    cls = _text(node.child_by_field_name("name"))
    if body is None:
        return
    for member in body.children:
        if member.type != "method_declaration":
            continue
        _scan_method(member, cls, class_path, is_jaxrs, scan)


def _scan_method(node: Node, cls: str, class_path: str, is_jaxrs: bool, scan: FileScan) -> None:
    anns = _annotations(_modifiers(node))
    method_name = _text(node.child_by_field_name("name"))
    sub: str | None = None
    http: str | None = None
    via = "jaxrs" if is_jaxrs else "controller"
    for a in anns:
        name = _ann_name(a)
        if name in _METHOD_MAPPINGS:
            http = _METHOD_MAPPINGS[name]
            literal, nonliteral = _ann_literal(a)
            if literal is not None:
                sub = literal
            elif nonliteral:
                scan.unresolved.append(("AF-SPRING-UNRESOLVED-ROUTE", a.start_point[0] + 1))
                return
        elif name == "RequestMapping" and not is_jaxrs:
            http = _request_method(a) or http or "get"
            literal, nonliteral = _ann_literal(a)
            if literal is not None:
                sub = literal
            elif nonliteral and _request_method(a) is None:
                scan.unresolved.append(("AF-SPRING-UNRESOLVED-ROUTE", a.start_point[0] + 1))
                return
        elif name in _JAXRS_METHODS:
            http = name.lower()
        elif name == "Path":
            literal, nonliteral = _ann_literal(a)
            if literal is not None:
                sub = literal
            elif nonliteral:
                scan.unresolved.append(("AF-SPRING-UNRESOLVED-ROUTE", a.start_point[0] + 1))
                return
    if http is None:
        return
    scan.routes.append(
        RouteRecord(
            method=http,
            path=_join(class_path, sub),
            handler=f"{cls}.{method_name}",
            via=via,
            line=node.start_point[0] + 1,
        )
    )


def _scan_router_functions(root: Node, scan: FileScan) -> None:
    stack = [root]
    while stack:
        node = stack.pop()
        if node.type == "method_invocation" and _text(node.child_by_field_name("name")) == "route":
            args = node.child_by_field_name("arguments")
            if args is not None:
                for arg in args.children:
                    if arg.type != "method_invocation":
                        continue
                    verb = _text(arg.child_by_field_name("name")).upper()
                    if verb not in _PREDICATE_METHODS:
                        continue
                    pred_args = arg.child_by_field_name("arguments")
                    literal = None
                    if pred_args is not None:
                        for p in pred_args.children:
                            if p.type == "string_literal":
                                frag = next(
                                    (c for c in p.children if c.type == "string_fragment"),
                                    None,
                                )
                                literal = _text(frag)
                    if literal is None:
                        scan.unresolved.append(
                            ("AF-SPRING-UNRESOLVED-ROUTE", node.start_point[0] + 1)
                        )
                    else:
                        scan.routes.append(
                            RouteRecord(
                                method=verb.lower(),
                                path=literal,
                                handler=_text(node.child_by_field_name("object")) or "router",
                                via="router-function",
                                line=node.start_point[0] + 1,
                            )
                        )
        stack.extend(node.children)


def scan_source(source: str) -> FileScan:
    """Parse one Java file; records, never judgments."""
    scan = FileScan()
    tree = _PARSER.parse(source.encode("utf-8"))
    scan.has_error = tree.root_node.has_error
    stack = [tree.root_node]
    while stack:
        node = stack.pop()
        if node.type == "class_declaration":
            _scan_class(node, scan)
        stack.extend(node.children)
    _scan_router_functions(tree.root_node, scan)
    return scan
