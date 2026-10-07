"""Static extraction of graph-database call sites (Neptune, Neo4j).

Python is parsed with ``ast``: the outermost call of a traversal chain is
one fact however many lines it spans. Java, Go and TypeScript/JavaScript
are scanned by pattern only when the file imports a graph driver; a chain
continues across lines while the next line starts with ``.`` — every such
file carries an ``AF-GDB-HEURISTIC`` diagnostic. Nothing executes.
"""

from __future__ import annotations

import ast
import hashlib
import re
from pathlib import Path
from typing import Any

from apiforge.adapters.graph_ import cypher, gremlin, sparql
from apiforge.adapters.inventory import CodeInventory
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

FACT_KIND = "data.graph.query"
EXTRACTOR = "graph"
VENDORS = ("neptune", "neo4j")
RISK_MEASURES = {
    "repeat-without-stop": "repeat_without_stop",
    "fanout-without-edge-label": "fanout_without_edge_label",
    "unfiltered-start": "unfiltered_start",
    "open-variable-length-path": "open_variable_length_path",
    "unlabeled-node-pattern": "unlabeled_node_pattern",
    "cartesian-pattern": "cartesian_pattern",
    "unbounded-property-path": "unbounded_property_path",
    "dynamic-query-text": "dynamic_query_text",
    "analytics-unscoped-algorithm": "analytics_unscoped_algorithm",
    "vector-search-without-topk": "vector_search_without_topk",
}
_ANALYZERS = {"gremlin": gremlin.analyze, "opencypher": cypher.analyze, "sparql": sparql.analyze}
_QUERY_TEXT_LIMIT = 500

_PY_GREMLIN = ("gremlin_python",)
_PY_NEO4J = ("neo4j",)
_PY_SPARQL = ("SPARQLWrapper",)
_PY_BOTO = ("boto3", "aioboto3")
_PY_METHODS = {
    "execute_gremlin_query": ("gremlin", "neptune"),
    "execute_open_cypher_query": ("opencypher", "neptune"),
    "execute_sparql": ("sparql", "neptune"),
    "submit": ("gremlin", "neptune"),
    "submit_async": ("gremlin", "neptune"),
    "setQuery": ("sparql", "neptune"),
}
_PY_NEO4J_METHODS = {"run", "execute_query"}
_PY_KEYWORDS = (
    "gremlinQuery",
    "openCypherQuery",
    "sparqlQuery",
    "queryString",
    "query",
    "query_",
    "message",
)
_TRAVERSAL_ROOTS = frozenset({"V", "E", "addV", "addE", "mergeV", "mergeE", "inject"})

_IMPORTS = {
    "java": {
        "gremlin": re.compile(r"org\.apache\.tinkerpop"),
        "neo4j": re.compile(r"org\.neo4j\.driver"),
    },
    "go": {
        "gremlin": re.compile(r"tinkerpop/gremlin-go|gremlingo"),
        "neo4j": re.compile(r"neo4j-go-driver"),
    },
    "ts": {
        "gremlin": re.compile(r"""(from|require\()\s*['"]gremlin['"]"""),
        "neo4j": re.compile(r"""(from|require\()\s*['"]neo4j-driver(-lite)?['"]"""),
    },
}
_SUFFIX = {".java": "java", ".go": "go", ".ts": "ts", ".tsx": "ts", ".js": "ts", ".mjs": "ts"}
_CHAIN_START = re.compile(r"\bg\s*\.\s*(V|E|addV|addE|mergeV|mergeE|AddV|AddE|MergeV|MergeE)\s*\(")
_CYPHER_CALL = {
    "java": re.compile(r"\.\s*(run|executableQuery)\s*\("),
    "go": re.compile(r"(\.\s*Run|\bExecuteQuery)\s*\("),
    "ts": re.compile(r"\.\s*(run|executeQuery)\s*\("),
}
_LITERAL = re.compile(
    r'"""(.*?)"""|"((?:[^"\\]|\\.)*)"|\'((?:[^\'\\]|\\.)*)\'|`([^`]*)`', re.DOTALL
)
_NEPTUNE_HINT = re.compile(r"neptune", re.IGNORECASE)
_CYPHER_WORD = re.compile(r"\b(MATCH|CREATE|MERGE|RETURN|CALL|UNWIND|WITH)\b", re.IGNORECASE)
_CYPHER_RECEIVER = re.compile(r"session|tx|transaction|driver|neo4j|graph|db", re.IGNORECASE)
_GO_IDENT_ARG = re.compile(r"^\s*[A-Za-z_][\w.]*\s*,\s*")


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _diag(code: str, rel: str, digest: str, message: str, line: int | None = None) -> Diagnostic:
    return Diagnostic(
        code=code,
        status=FindingStatus.UNRESOLVED,
        message=f"{rel}: {message}",
        source=SourceRef(path=rel, sha256=digest, line=line, extractor=EXTRACTOR),
    )


def query_measures(
    language: str, text: str | None, *, dynamic: bool = False, injection_shaped: bool = False
) -> dict[str, Any]:
    """Analyzer output flattened into fact measures (booleans per shape risk)."""
    if text is None:
        analysis: dict[str, Any] = {
            "bounded": False,
            "mutation": False,
            "labels_used": (),
            "edge_labels_used": (),
            "shape_risks": (),
        }
    else:
        analysis = _ANALYZERS[language](text)
    risks = list(analysis["shape_risks"])
    if injection_shaped:
        risks.append("dynamic-query-text")
    measures: dict[str, Any] = {
        "language": language,
        "bounded": bool(analysis["bounded"]),
        "unbounded": not analysis["bounded"] and not analysis["mutation"] and text is not None,
        "mutation": bool(analysis["mutation"]),
        "query_dynamic": dynamic,
        "labels_used": list(analysis["labels_used"]),
        "edge_labels_used": list(analysis["edge_labels_used"]),
        "shape_risks": list(dict.fromkeys(risks)),
    }
    if text is not None:
        measures["query_text"] = text[:_QUERY_TEXT_LIMIT]
        measures["query_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    for risk in measures["shape_risks"]:
        measures[RISK_MEASURES[risk]] = True
    if measures["mutation"]:
        measures["command"] = "mutation"
    return measures


def _fact(rel: str, digest: str, line: int, vendor: str, operation: str, **measures: Any) -> Fact:
    payload = {"vendor": vendor, "operation": operation, "binding": "name", **measures}
    return Fact(
        fact_id=stable_id("fact", {"k": FACT_KIND, "p": rel, "l": line, **payload}),
        kind=FACT_KIND,
        source=SourceRef(path=rel, sha256=digest, line=line, extractor=EXTRACTOR),
        measures=payload,
        attrs={},
    )


def _py_imports(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def _py_query_arg(call: ast.Call) -> ast.expr | None:
    for keyword in call.keywords:
        if keyword.arg in _PY_KEYWORDS:
            return keyword.value
    return call.args[0] if call.args else None


def _py_text(node: ast.expr | None) -> tuple[str | None, bool, bool]:
    """(literal text, dynamic, injection-shaped) for a query argument."""
    if node is None:
        return None, True, False
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value, False, False
    if isinstance(node, ast.JoinedStr | ast.BinOp):
        return None, True, True
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "format"
    ):
        return None, True, True
    return None, True, False


def _chain_of(node: ast.Call) -> tuple[list[ast.Call], ast.expr]:
    chain: list[ast.Call] = []
    cursor: ast.expr = node
    while isinstance(cursor, ast.Call) and isinstance(cursor.func, ast.Attribute):
        chain.append(cursor)
        cursor = cursor.func.value
    return chain, cursor


def _attrs(chain: list[ast.Call]) -> list[str]:
    return [_normal(call.func.attr) for call in chain if isinstance(call.func, ast.Attribute)]


def _normal(name: str) -> str:
    parts = name.rstrip("_").split("_")
    return parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:])


def _scan_python(path: Path, rel: str, digest: str) -> tuple[list[Fact], list[Diagnostic]]:
    text = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [], [_diag("AF-GDB-PARSE", rel, digest, f"parse failed: {exc.msg}", exc.lineno)]
    imports = _py_imports(tree)
    has_gremlin = bool(imports & set(_PY_GREMLIN))
    has_neo4j = bool(imports & set(_PY_NEO4J))
    has_sparql = bool(imports & set(_PY_SPARQL))
    has_boto = bool(imports & set(_PY_BOTO))
    if not (has_gremlin or has_neo4j or has_sparql or has_boto):
        return [], []
    neo4j_vendor = "neptune" if _NEPTUNE_HINT.search(text) else "neo4j"
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    inner: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or id(node) in inner:
            continue
        if not isinstance(node.func, ast.Attribute):
            continue
        method = node.func.attr
        chain, root = _chain_of(node)
        roots = [name for name in _attrs(chain) if name in _TRAVERSAL_ROOTS]
        if has_gremlin and roots and isinstance(root, ast.Name | ast.Attribute):
            inner.update(id(c) for c in chain[1:])
            segment = ast.get_source_segment(text, node) or ""
            facts.append(
                _fact(
                    rel,
                    digest,
                    node.lineno,
                    "neptune",
                    f"traverse_{roots[-1].lower()}",
                    **query_measures("gremlin", segment),
                )
            )
            continue
        target: tuple[str, str] | None = None
        if method in _PY_METHODS and (has_boto or has_gremlin or has_sparql):
            if method in ("submit", "submit_async") and not has_gremlin:
                continue
            if method == "setQuery" and not has_sparql:
                continue
            if method.startswith("execute_") and not has_boto:
                continue
            target = _PY_METHODS[method]
        elif (
            method == "execute_query"
            and has_boto
            and any(keyword.arg == "queryString" for keyword in node.keywords)
        ):
            target = ("opencypher", "neptune")
        elif method in _PY_NEO4J_METHODS and has_neo4j:
            target = ("opencypher", neo4j_vendor)
        if target is None:
            continue
        language, vendor = target
        literal, dynamic, injection = _py_text(_py_query_arg(node))
        if method in _PY_NEO4J_METHODS and not _cypher_site(literal, _receiver(node)):
            continue
        if dynamic:
            diagnostics.append(
                _diag(
                    "AF-GDB-DYNAMIC-QUERY", rel, digest, "query text is not a literal", node.lineno
                )
            )
        facts.append(
            _fact(
                rel,
                digest,
                node.lineno,
                vendor,
                method,
                **query_measures(language, literal, dynamic=dynamic, injection_shaped=injection),
            )
        )
    if facts:
        diagnostics.append(
            _diag("AF-GDB-HEURISTIC", rel, digest, "receivers matched by name — binding not proven")
        )
    return facts, diagnostics


def _receiver(call: ast.Call) -> str:
    value = call.func.value if isinstance(call.func, ast.Attribute) else None
    if isinstance(value, ast.Name):
        return value.id
    if isinstance(value, ast.Attribute):
        return value.attr
    return ""


def _cypher_site(literal: str | None, receiver: str) -> bool:
    if literal is not None:
        return bool(_CYPHER_WORD.search(literal))
    return bool(_CYPHER_RECEIVER.search(receiver))


def blank_comments(text: str) -> str:
    """Replace ``//`` and ``/* */`` comments with spaces; strings and newlines survive."""
    out: list[str] = []
    i, quote = 0, ""
    while i < len(text):
        char = text[i]
        if quote:
            out.append(char)
            if char == "\\" and i + 1 < len(text):
                out.append(text[i + 1])
                i += 2
                continue
            if char == quote:
                quote = ""
            i += 1
            continue
        if char in "'\"`":
            quote = char
            out.append(char)
            i += 1
            continue
        if text.startswith("//", i):
            end = text.find("\n", i)
            end = len(text) if end == -1 else end
            out.append(" " * (end - i))
            i = end
            continue
        if text.startswith("/*", i):
            end = text.find("*/", i + 2)
            end = len(text) if end == -1 else end + 2
            out.append("".join("\n" if c == "\n" else " " for c in text[i:end]))
            i = end
            continue
        out.append(char)
        i += 1
    return "".join(out)


def _statement_end(text: str, start: int) -> int:
    depth, quote, i = 0, "", start
    while i < len(text):
        char = text[i]
        if quote:
            if char == quote and text[i - 1] != "\\":
                quote = ""
        elif char in "'\"`":
            quote = char
        elif char in "([{":
            depth += 1
        elif char in ")]}":
            if depth == 0:
                return i
            depth -= 1
        elif depth == 0 and char == ";":
            return i
        elif depth == 0 and char == "\n":
            rest = text[i + 1 :].lstrip()
            if not rest.startswith("."):
                return i
        i += 1
    return i


def _call_args(text: str, open_paren: int) -> str:
    end = gremlin._close(text, open_paren)
    return text[open_paren : end - 1]


def _first_arg_text(args: str, lang: str) -> tuple[str | None, bool, bool]:
    body = args.strip()
    if lang == "go":
        while not body.startswith(("fmt.Sprintf", '"', "`")) and _GO_IDENT_ARG.match(body):
            body = _GO_IDENT_ARG.sub("", body, count=1)
        if body.startswith("fmt.Sprintf"):
            return None, True, True
    literal = _LITERAL.match(body)
    if literal is None:
        return None, True, False
    value = next(group for group in literal.groups() if group is not None)
    after = body[literal.end() :].lstrip()
    if after.startswith("+") or (literal.group(4) is not None and "${" in value):
        return None, True, True
    return value, False, False


def _scan_pattern(
    path: Path, rel: str, digest: str, lang: str
) -> tuple[list[Fact], list[Diagnostic]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [], []
    text = blank_comments(text)
    table = _IMPORTS[lang]
    has_gremlin = bool(table["gremlin"].search(text))
    has_neo4j = bool(table["neo4j"].search(text))
    if not (has_gremlin or has_neo4j):
        return [], []
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    if has_gremlin:
        for match in _CHAIN_START.finditer(text):
            end = _statement_end(text, match.start())
            chain = text[match.start() : end]
            line = text.count("\n", 0, match.start()) + 1
            root = match.group(1)
            facts.append(
                _fact(
                    rel,
                    digest,
                    line,
                    "neptune",
                    f"traverse_{root[:1].lower() + root[1:]}".lower(),
                    **query_measures("gremlin", chain),
                )
            )
    if has_neo4j:
        vendor = "neptune" if _NEPTUNE_HINT.search(text) else "neo4j"
        for match in _CYPHER_CALL[lang].finditer(text):
            args = _call_args(text, match.end())
            literal, dynamic, injection = _first_arg_text(args, lang)
            receiver = re.search(r"(\w+)\s*$", text[: match.start()])
            if not _cypher_site(literal, receiver.group(1) if receiver else match.group(1)):
                continue
            line = text.count("\n", 0, match.start()) + 1
            if dynamic:
                diagnostics.append(
                    _diag("AF-GDB-DYNAMIC-QUERY", rel, digest, "query text is not a literal", line)
                )
            facts.append(
                _fact(
                    rel,
                    digest,
                    line,
                    vendor,
                    match.group(1).strip(". ").lower(),
                    **query_measures(
                        "opencypher", literal, dynamic=dynamic, injection_shaped=injection
                    ),
                )
            )
    if facts:
        diagnostics.append(
            _diag(
                "AF-GDB-HEURISTIC", rel, digest, f"{lang} call sites matched by pattern, not parsed"
            )
        )
    return facts, diagnostics


def extract_graph_access(project_root: Path, vendor: str | None = None) -> CodeInventory:
    """Scan a project tree for graph call sites; ``vendor`` filters the facts."""
    if vendor is not None and vendor not in VENDORS:
        raise ValueError(f"vendor {vendor!r} not in {VENDORS}")
    root = Path(project_root)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    input_hashes: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        if any(part in {"node_modules", ".git", "__pycache__", ".venv"} for part in path.parts):
            continue
        if path.suffix == ".py":
            rel = path.relative_to(root).as_posix()
            digest = _digest(path)
            found, diags = _scan_python(path, rel, digest)
        elif path.suffix in _SUFFIX:
            rel = path.relative_to(root).as_posix()
            digest = _digest(path)
            found, diags = _scan_pattern(path, rel, digest, _SUFFIX[path.suffix])
        else:
            continue
        if vendor is not None:
            found = [fact for fact in found if fact.measures.get("vendor") == vendor]
            if not found:
                diags = [d for d in diags if d.code == "AF-GDB-PARSE"]
        if found or diags:
            input_hashes[rel] = digest
            facts.extend(found)
            diagnostics.extend(diags)
    return CodeInventory(
        framework=f"{vendor or 'graph'}-access",
        root=str(root),
        facts=tuple(sorted(facts, key=lambda f: f.fact_id)),
        diagnostics=tuple(diagnostics),
        input_hashes=input_hashes,
    )


def extract_neptune_access(project_root: Path) -> CodeInventory:
    """Neptune Gremlin/openCypher/SPARQL call sites."""
    return extract_graph_access(project_root, "neptune")


def extract_neo4j_access(project_root: Path) -> CodeInventory:
    """Neo4j openCypher call sites."""
    return extract_graph_access(project_root, "neo4j")
