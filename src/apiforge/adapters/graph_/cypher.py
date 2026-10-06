"""openCypher query text -> declared shape measures (Neptune and Neo4j).

Pure text analysis over the query string as written; string literals are
blanked first so keywords inside quotes never count.
"""

from __future__ import annotations

import re

_STRING = re.compile(r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"")
_CLAUSE = re.compile(
    r"\b(OPTIONAL\s+MATCH|MATCH|WHERE|WITH|RETURN|UNWIND|CALL|CREATE|MERGE|SET|DELETE|"
    r"DETACH\s+DELETE|REMOVE|ORDER\s+BY|SKIP|LIMIT|UNION|FOREACH)\b",
    re.IGNORECASE,
)
_MUTATION = re.compile(r"\b(CREATE|MERGE|SET|DELETE|REMOVE)\b", re.IGNORECASE)
_LIMIT = re.compile(r"\bLIMIT\s+(\d+|\$\w+)", re.IGNORECASE)
_NODE = re.compile(r"\(\s*([A-Za-z_]\w*)?\s*((?::\s*`?\w+`?\s*)*)\s*(\{[^}]*\})?\s*\)")
_REL = re.compile(r"\[([^\]]*)\]")
_REL_LABEL = re.compile(r":\s*`?(\w+)`?")
_HOPS = re.compile(r"\*\s*(\d+)?\s*(\.\.\s*(\d+)?)?")
_ALGO = re.compile(r"\bCALL\s+neptune\.algo\.([\w.]+)", re.IGNORECASE)
_TOPK = re.compile(r"\btopK\s*:", re.IGNORECASE)
_AGGREGATES = ("count", "sum", "avg", "min", "max")


def _blank_strings(query: str) -> str:
    return _STRING.sub(lambda m: "'" + " " * (len(m.group(0)) - 2) + "'", query)


def _clauses(query: str) -> list[tuple[str, str]]:
    marks = list(_CLAUSE.finditer(query))
    out: list[tuple[str, str]] = []
    for index, mark in enumerate(marks):
        end = marks[index + 1].start() if index + 1 < len(marks) else len(query)
        out.append((re.sub(r"\s+", " ", mark.group(1).upper()), query[mark.end() : end]))
    return out


def _split_top(text: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for char in text:
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        if char == "," and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(char)
    parts.append("".join(current))
    return [part for part in parts if part.strip()]


def _variables(pattern: str) -> set[str]:
    names = {m.group(1) for m in _NODE.finditer(pattern) if m.group(1)}
    for rel in _REL.findall(pattern):
        head = re.match(r"\s*([A-Za-z_]\w*)", rel)
        if head and not rel.lstrip().startswith(":"):
            names.add(head.group(1))
    return names


def _open_path(pattern: str) -> bool:
    for rel in _REL.findall(pattern):
        hops = _HOPS.search(rel)
        if hops is None:
            continue
        has_range, upper = hops.group(2) is not None, hops.group(3)
        if (hops.group(1) is None and not has_range) or (has_range and upper is None):
            return True
    return False


def _aggregate_only(items: str) -> bool:
    parts = _split_top(items)
    return bool(parts) and all(
        re.match(rf"\s*({'|'.join(_AGGREGATES)})\s*\(", part, re.IGNORECASE) for part in parts
    )


def analyze(query: str) -> dict[str, object]:
    """Measures declared by the openCypher text."""
    text = _blank_strings(query)
    clauses = _clauses(text)
    risks: list[str] = []
    bound: set[str] = set()
    labels: set[str] = set()
    edge_labels: set[str] = set()
    matched_before_call = False
    returns_aggregate = False
    for keyword, body in clauses:
        if keyword in ("MATCH", "OPTIONAL MATCH"):
            matched_before_call = True
            parts = _split_top(body)
            part_vars = [_variables(part) for part in parts]
            for node in _NODE.finditer(body):
                labels.update(re.findall(r":\s*`?(\w+)`?", node.group(2) or ""))
            for rel in _REL.findall(body):
                edge_labels.update(_REL_LABEL.findall(rel.split("*")[0]))
            if _open_path(body):
                risks.append("open-variable-length-path")
            nodes = list(_NODE.finditer(body))
            anchored = any(
                (node.group(2) or "").strip() or node.group(3) or node.group(1) in bound
                for node in nodes
            )
            if nodes and not anchored:
                risks.append("unlabeled-node-pattern")
            if len(parts) > 1 and any(
                not (vars_ & set().union(*(v for j, v in enumerate(part_vars) if j != i)))
                for i, vars_ in enumerate(part_vars)
            ):
                risks.append("cartesian-pattern")
            for vars_ in part_vars:
                bound |= vars_
        elif keyword == "CALL":
            algo = _ALGO.search("CALL" + body)
            if algo:
                name = algo.group(1).lower()
                if name.startswith("vectors."):
                    if "topk" in name and not _TOPK.search(body):
                        risks.append("vector-search-without-topk")
                elif not matched_before_call:
                    risks.append("analytics-unscoped-algorithm")
        elif keyword == "RETURN":
            returns_aggregate = _aggregate_only(body)
        elif keyword == "WITH":
            for part in _split_top(body):
                alias = re.search(r"\bAS\s+(\w+)", part, re.IGNORECASE)
                bound.add(alias.group(1) if alias else part.strip())
    return {
        "bounded": bool(_LIMIT.search(text)) or returns_aggregate,
        "mutation": bool(_MUTATION.search(text)),
        "labels_used": tuple(sorted(labels)),
        "edge_labels_used": tuple(sorted(edge_labels)),
        "shape_risks": tuple(dict.fromkeys(risks)),
    }
