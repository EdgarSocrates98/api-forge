"""Static extraction of MongoDB/DynamoDB/Neptune data-access call sites.

Same contract as the Redis adapter: Python files are parsed with ``ast``
(binding by constructor when visible, ``binding: name`` heuristic
otherwise — always named), Java/Go are scanned by pattern only when the
file imports the driver package. Composite postures (``full_scan``,
``unfiltered_write``, ``unbounded``) are computed here from *declared*
arguments — a keyword argument that exists counts as declared, its value
is never inferred.
"""

from __future__ import annotations

import ast
import hashlib
import re
from pathlib import Path
from typing import Any

from apiforge.adapters.inventory import CodeInventory
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_MONGO_PACKAGES = ("pymongo", "motor", "mongoengine", "beanie")
_MONGO_OPS = {
    "find",
    "find_one",
    "insert_one",
    "insert_many",
    "update_one",
    "update_many",
    "delete_one",
    "delete_many",
    "replace_one",
    "aggregate",
    "count_documents",
    "distinct",
    "find_one_and_update",
    "find_one_and_delete",
    "bulk_write",
    "watch",
}
_MONGO_FILTERED_WRITES = {"delete_many", "update_many", "replace_one"}
_MONGO_READS = {"find", "aggregate", "distinct", "count_documents"}

_DYNAMO_PACKAGES = ("boto3", "aioboto3")
_DYNAMO_OPS = {
    "scan",
    "query",
    "get_item",
    "put_item",
    "update_item",
    "delete_item",
    "batch_get_item",
    "batch_write_item",
    "transact_write_items",
    "transact_get_items",
    "describe_table",
}

_NEPTUNE_PACKAGES = ("gremlin_python", "gremlingo", "aioboto3", "boto3")
_NEPTUNE_QUERY_METHODS = {
    "execute_gremlin_query": "gremlin",
    "execute_open_cypher_query": "opencypher",
    "execute_sparql": "sparql",
}
_LIMIT_RE = re.compile(r"\bLIMIT\s+\d+|\.limit\s*\(|\.range\s*\(", re.IGNORECASE)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fact(
    kind: str,
    rel: str,
    digest: str,
    line: int,
    extractor: str,
    **kwargs: Any,
) -> Fact:
    measures = {k: v for k, v in kwargs.items() if v is not None}
    return Fact(
        fact_id=stable_id("fact", {"k": kind, "p": rel, "l": line, **measures}),
        kind=kind,
        source=SourceRef(path=rel, sha256=digest, line=line, extractor=extractor),
        measures=measures,
        attrs={},
    )


def _parse_python(path: Path, rel: str, digest: str, extractor: str) -> ast.Module | Diagnostic:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError) as exc:
        return Diagnostic(
            code=f"AF-{extractor.upper()}-PARSE",
            status=FindingStatus.UNRESOLVED,
            message=f"{rel}: {exc}",
            source=SourceRef(path=rel, sha256=digest, extractor=extractor),
        )


def _imports(tree: ast.Module, packages: tuple[str, ...]) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in packages:
                    return True
        elif (
            isinstance(node, ast.ImportFrom)
            and node.module
            and node.module.split(".")[0] in packages
        ):
            return True
    return False


def _kwarg_names(node: ast.Call) -> set[str]:
    return {kw.arg for kw in node.keywords if kw.arg}


def _str_constant(node: ast.expr) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _collection_of(func: ast.expr) -> str | None:
    """`db["orders"]`/`client["d"]["orders"]`/`db.orders` -> literal name."""
    node = func
    found: str | None = None
    while True:
        if isinstance(node, ast.Attribute):
            if found is None and node.attr.isidentifier() and not node.attr.startswith("_"):
                found = node.attr
            node = node.value
        elif isinstance(node, ast.Subscript):
            lit = _str_constant(node.slice)
            if lit:
                found = lit
            node = node.value
        else:
            return found


def _first_arg_unfiltered(node: ast.Call) -> bool:
    """No args or an empty `{}`/`{}`-equivalent literal first arg."""
    if not node.args:
        return True
    first = node.args[0]
    return isinstance(first, ast.Dict) and not first.keys


def _heuristic_diag(rel: str, digest: str, extractor: str) -> Diagnostic:
    return Diagnostic(
        code=f"AF-{extractor.upper()}-HEURISTIC-BINDING",
        status=FindingStatus.UNRESOLVED,
        message=f"{rel}: receivers matched by name — binding not proven",
        source=SourceRef(path=rel, sha256=digest, extractor=extractor),
    )


def _scan_python_mongo(path: Path, rel: str, digest: str) -> tuple[list[Fact], list[Diagnostic]]:
    tree = _parse_python(path, rel, digest, "mongo")
    if isinstance(tree, Diagnostic):
        return [], [tree]
    if not _imports(tree, _MONGO_PACKAGES):
        return [], []
    # `<call>.limit(n)` / `.batch_size(n)` bound the inner find/aggregate
    bounded: set[int] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in ("limit", "batch_size")
            and isinstance(node.func.value, ast.Call)
            and isinstance(node.func.value.func, ast.Attribute)
            and node.func.value.func.attr in _MONGO_READS
        ):
            bounded.add(id(node.func.value))
    # `orders = db["orders"]` / `orders = db.orders` — receiver names bound
    # to a literal collection name
    names: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and not isinstance(node.value, ast.Call):
            lit = _collection_of(node.value)
            if lit:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        names[target.id] = lit
    facts: list[Fact] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        op = node.func.attr
        if op not in _MONGO_OPS:
            continue
        receiver = node.func.value
        collection = (
            names.get(receiver.id) if isinstance(receiver, ast.Name) else _collection_of(receiver)
        )
        has_limit = "limit" in _kwarg_names(node) or id(node) in bounded
        measures: dict[str, Any] = {
            "operation": op,
            "entity": collection,
            "binding": "name",
        }
        if op in _MONGO_READS:
            measures["has_limit"] = has_limit
            measures["unbounded_find"] = not has_limit
        if op in _MONGO_FILTERED_WRITES:
            measures["unfiltered_write"] = _first_arg_unfiltered(node)
        facts.append(_fact("data.mongo.operation", rel, digest, node.lineno, "mongo", **measures))
    diagnostics = [_heuristic_diag(rel, digest, "mongo")] if facts else []
    return facts, diagnostics


def _scan_python_dynamo(path: Path, rel: str, digest: str) -> tuple[list[Fact], list[Diagnostic]]:
    tree = _parse_python(path, rel, digest, "dynamo")
    if isinstance(tree, Diagnostic):
        return [], [tree]
    if not _imports(tree, _DYNAMO_PACKAGES):
        return [], []
    if "dynamodb" not in path.read_text(encoding="utf-8"):
        return [], []
    facts: list[Fact] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        op = node.func.attr
        if op not in _DYNAMO_OPS:
            continue
        kwargs = _kwarg_names(node)
        table = next(
            (
                _str_constant(kw.value)
                for kw in node.keywords
                if kw.arg == "TableName" and _str_constant(kw.value)
            ),
            None,
        )
        measures: dict[str, Any] = {
            "operation": op,
            "entity": table,
            "binding": "name",
        }
        if op == "scan":
            measures["full_scan"] = not ({"Limit", "FilterExpression", "IndexName"} & kwargs)
        if op == "query":
            measures["query_without_key_condition"] = "KeyConditionExpression" not in kwargs
        facts.append(_fact("data.dynamo.operation", rel, digest, node.lineno, "dynamo", **measures))
    # resource API: dynamodb.Table("name") binds receivers to a table literal
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "Table"
            and node.args
        ):
            table = _str_constant(node.args[0])
            if table:
                facts.append(
                    _fact(
                        "data.dynamo.table_ref",
                        rel,
                        digest,
                        node.lineno,
                        "dynamo",
                        entity=table,
                        binding="name",
                    )
                )
    diagnostics = [_heuristic_diag(rel, digest, "dynamo")] if facts else []
    return facts, diagnostics


def _scan_python_neptune(path: Path, rel: str, digest: str) -> tuple[list[Fact], list[Diagnostic]]:
    text = path.read_text(encoding="utf-8")
    tree = _parse_python(path, rel, digest, "neptune")
    if isinstance(tree, Diagnostic):
        return [], [tree]
    if not _imports(tree, _NEPTUNE_PACKAGES):
        return [], []
    lines = text.splitlines()
    facts: list[Fact] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        method = node.func.attr
        if method in _NEPTUNE_QUERY_METHODS:
            query = next(
                (_str_constant(kw.value) for kw in node.keywords if _str_constant(kw.value)),
                None,
            )
            facts.append(
                _fact(
                    "data.neptune.query",
                    rel,
                    digest,
                    node.lineno,
                    "neptune",
                    language=_NEPTUNE_QUERY_METHODS[method],
                    operation=method,
                    binding="name",
                    unbounded=not bool(query and _LIMIT_RE.search(query)),
                )
            )
        elif method in ("V", "E") and isinstance(node.func.value, ast.Name):
            # g.V()/g.E() traversal — a same-line .limit(/.range( bounds it;
            # multi-line chains keep unbounded=True (conservative, honest)
            line = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
            facts.append(
                _fact(
                    "data.neptune.query",
                    rel,
                    digest,
                    node.lineno,
                    "neptune",
                    language="gremlin",
                    operation=f"traverse_{method.lower()}",
                    binding="name",
                    unbounded=not bool(_LIMIT_RE.search(line)),
                )
            )
    diagnostics = [_heuristic_diag(rel, digest, "neptune")] if facts else []
    return facts, diagnostics


_JAVA_DB_RE = {
    "mongo": (
        re.compile(r"com\.mongodb|MongoCollection|MongoTemplate"),
        re.compile(
            r"\.(find|insertOne|insertMany|updateOne|updateMany|"
            r"deleteOne|deleteMany|replaceOne|aggregate|watch)\s*\("
        ),
        {"deleteMany", "updateMany", "replaceOne"},
    ),
    "dynamo": (
        re.compile(r"software\.amazon\.awssdk\.services\.dynamodb|DynamoDbClient|DynamoDBMapper"),
        re.compile(
            r"\.(scan|query|getItem|putItem|updateItem|deleteItem|"
            r"batchGetItem|batchWriteItem|transactWriteItems)\s*\("
        ),
        set(),
    ),
    "neptune": (
        re.compile(r"gremlin|tinkerpop|neptune"),
        re.compile(r"\bg\s*\.\s*(V|E)\s*\("),
        set(),
    ),
}
_GO_DB_RE = {
    "mongo": (
        re.compile(r"go\.mongodb\.org/mongo-driver"),
        re.compile(
            r"\.(Find|FindOne|InsertOne|InsertMany|UpdateOne|"
            r"UpdateMany|DeleteOne|DeleteMany|Aggregate|Watch)\s*\("
        ),
        {"DeleteMany", "UpdateMany"},
    ),
    "dynamo": (
        re.compile(r"aws-sdk-go.*/service/dynamodb"),
        re.compile(
            r"\.(Scan|Query|GetItem|PutItem|UpdateItem|DeleteItem|"
            r"BatchGetItem|BatchWriteItem|TransactWriteItems)"
            r"(WithContext)?\s*\("
        ),
        set(),
    ),
    "neptune": (
        re.compile(r"gremlingo|neptune"),
        re.compile(r"\bg\s*\.\s*(V|E)\s*\("),
        set(),
    ),
}


def _scan_by_pattern(
    path: Path,
    rel: str,
    digest: str,
    extractor: str,
    table: dict[str, tuple[re.Pattern[str], re.Pattern[str], set[str]]],
) -> tuple[list[Fact], list[Diagnostic]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [], []
    import_re, op_re, _filtered = table[extractor]
    if not import_re.search(text):
        return [], []
    facts: list[Fact] = []
    for index, line in enumerate(text.splitlines(), 1):
        for match in op_re.finditer(line):
            op = match.group(1)
            low = op.lower()
            measures: dict[str, Any] = {
                "operation": low,
                "binding": "name",
            }
            if extractor == "mongo":
                mongo_reads = {r.replace("_", "") for r in _MONGO_READS}
                if low in _MONGO_READS or low in mongo_reads:
                    has_limit = bool(_LIMIT_RE.search(line))
                    measures["has_limit"] = has_limit
                    measures["unbounded_find"] = not has_limit
                if low in {w.replace("_", "") for w in _MONGO_FILTERED_WRITES}:
                    # unfiltered only when the arg list is visibly empty
                    # ( `()` / `{}` / `new Document()` ) — anything else is
                    # a declared filter, never analyzed
                    after = line[match.end() :]
                    measures["unfiltered_write"] = bool(
                        re.match(r"\s*\)", after)
                        or re.match(r"\s*\{\s*\}\s*\)", after)
                        or re.match(
                            r"\s*new\s+(Document|BasicDBObject)\s*\(\s*\)\s*\)",
                            after,
                        )
                    )
            if extractor == "dynamo":
                if low == "scan":
                    measures["full_scan"] = not re.search(
                        r"Limit|FilterExpression|IndexName|withLimit|"
                        r"filterExpression|\.limit\s*\(",
                        line,
                    )
                if low == "query":
                    measures["query_without_key_condition"] = not re.search(
                        r"KeyConditionExpression|keyConditionExpression|"
                        r"withKeyConditionExpression",
                        line,
                    )
            if extractor == "neptune":
                measures["language"] = "gremlin"
                measures["unbounded"] = not bool(_LIMIT_RE.search(line))
            facts.append(
                _fact(
                    f"data.{extractor}.operation"
                    if extractor != "neptune"
                    else "data.neptune.query",
                    rel,
                    digest,
                    index,
                    extractor,
                    **measures,
                )
            )
    diagnostics = [_heuristic_diag(rel, digest, extractor)] if facts else []
    return facts, diagnostics


_SCANNERS = {
    "mongo": (_scan_python_mongo, _JAVA_DB_RE["mongo"], _GO_DB_RE["mongo"]),
    "dynamo": (_scan_python_dynamo, _JAVA_DB_RE["dynamo"], _GO_DB_RE["dynamo"]),
    "neptune": (
        _scan_python_neptune,
        _JAVA_DB_RE["neptune"],
        _GO_DB_RE["neptune"],
    ),
}


def extract_data_access(project_root: Path, database: str) -> CodeInventory:
    """Scan a project tree for data-access call sites — no code executes."""
    if database not in _SCANNERS:
        raise ValueError(f"database {database!r} not in {sorted(_SCANNERS)}")
    py_scan = _SCANNERS[database][0]
    root = Path(project_root)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    input_hashes: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(root).as_posix()
        digest = _digest(path)
        if path.suffix == ".py":
            f, d = py_scan(path, rel, digest)
        elif path.suffix == ".java":
            f, d = _scan_by_pattern(path, rel, digest, database, _JAVA_DB_RE)
        elif path.suffix == ".go":
            f, d = _scan_by_pattern(path, rel, digest, database, _GO_DB_RE)
        else:
            continue
        if f or d:
            input_hashes[rel] = digest
            facts.extend(f)
            diagnostics.extend(d)
    return CodeInventory(
        framework=f"{database}-access",
        root=str(root),
        facts=tuple(sorted(facts, key=lambda f: f.fact_id)),
        diagnostics=tuple(diagnostics),
        input_hashes=input_hashes,
    )


def extract_mongo(project_root: Path) -> CodeInventory:
    """MongoDB/DocumentDB call sites (pymongo, motor, driver patterns)."""
    return extract_data_access(project_root, "mongo")


def extract_dynamo_access(project_root: Path) -> CodeInventory:
    """DynamoDB data-plane call sites (boto3 client and resource APIs)."""
    return extract_data_access(project_root, "dynamo")


def extract_neptune_access(project_root: Path) -> CodeInventory:
    """Neptune gremlin/openCypher/SPARQL call sites."""
    return extract_data_access(project_root, "neptune")
